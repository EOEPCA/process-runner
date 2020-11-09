import click
import os
import sys
import json
from time import sleep
import logging
from .execution import Execution
from .workflow import Workflow
from .process import Process

from pystac import *
from urllib.parse import urlparse
import requests
from requests.auth import HTTPBasicAuth
#from pystac import STAC_IO
import uuid


logging.basicConfig(stream=sys.stderr, 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

os.environ['STAGEIN_USERNAME'] = 'eoepca-storage'
os.environ['STAGEIN_PASSWORD'] = '4k8wMajA5ABaYdk'

def my_read_method(uri):
    
    parsed = urlparse(uri)
    
    if parsed.scheme.startswith('http'):
    
        if os.environ.get('STAGEIN_PASSWORD') is None:
            
            return requests.get(uri).text
            
        else:
      
            return requests.get(uri, 
                                auth=HTTPBasicAuth(username=os.environ.get('STAGEIN_USERNAME'), 
                                                   password=os.environ.get('STAGEIN_PASSWORD'))
                               ).text
    else:
        return STAC_IO.default_read_text_method(uri)

STAC_IO.read_text_method = my_read_method


def to_execute_inputs(wps_inputs, wps_params):
    
    execute_inputs = []

    for _input in wps_inputs:

        execute_inputs.append({'id': _input['id'], 
                              'input': {'dataType': _input['input']['literalDataDomains'][0]['dataType'],
                                        'value': wps_params[_input['id']]}})

    return execute_inputs

def check_code(r, http_status):

    if r.status_code == http_status:
        
        return True
    
    else: 
        
        return False
    
@click.command(name='wps3', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option('--application_package_url')
@click.option('--wps_endpoint')
@click.pass_context
def main(ctx, application_package_url, wps_endpoint):
    
    _wps_params = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}
    
    token = os.environ['TOKEN']
    
    # get process id
    app_package = Workflow(application_package_url)
    process_id = app_package.get_workflow_id()
    process_id = f'{process_id}_'.replace('-', '_')
    
    logging.info(f'Process id: {process_id}')
    
    # check 
    ades = Process(token)
    
    r = ades.get_process()
   
    logging.info(f'Checking if process {process_id} is deployed')
    
    if not ades.is_process_deployed(f'{process_id}'):
        
        logging.info(f'Deploy process from application package {application_package_url}')
        
        r = ades.deploy_process(application_package_url)
    
        if not check_code(r, 201):
            
            raise Exception(f'{r.status_code} - Process not deployed, see exception')
    
        if not ades.is_process_deployed(process_id):
            
            logging.info(f'Tried to deploy {process_id}, got a 201 but the process is not deployed')
            
            raise Exception(f'{r.status_code} - HTTP code 201 but the process is not deployed')
            
    else:
        
        logging.info(f'Process {process_id} is already deployed')
        
    r = ades.get_process(process_id)
    
    if not check_code(r, 200):
        
        raise Exception(f'{r.status_code} - Describe process request failed')
    
    # submit execution
    wps_inputs = r.json()['process']['inputs']
    
    execute_inputs = to_execute_inputs(wps_inputs, 
                                       _wps_params)
    
    logging.info(execute_inputs)  
    
    execution = Execution(token, process_id)
    
    r = execution.execute_process(execute_inputs)

    # status monitoring
    r = execution.get_status()
    job_id = r.json()['jobID']
    logging.info(f'Polling status at {r.url} for job id: {job_id}')
    
    #logging.info(r.status_code, r.reason, r.url)
    
    success = False
    
    while r.json()['status'] == 'running':

        r = execution.get_status()

        if r.json()['status'] == 'failed': 

            logging.info(r.json())

            break

        if r.json()['status'] == 'successful':  

            logging.info(r.json()['links'][0]['href'])

            success = True
            
            break

        else:
            progress = r.json()['progress']
            status = r.json()['status']
            
            logging.info(f'Polling - {status}, {progress} %')
            
            sleep(30)

    if not success:
        
        logging.info(r.json())
        
        sys.exit(1)    
        
    # get the results
    r = execution.get_result()

    logging.info(r.status_code, r.reason, r.url)

    if success: 
        
        results = json.loads(r.json()['outputs'][0]['value']['inlineValue'])

        #logging.info(results)

        stac_catalog_endpoint = results['stac:catalog']['href']

        logging.info(stac_catalog_endpoint)
    
        cat = Catalog.from_file(stac_catalog_endpoint)
        sub_cats = []

        try:
            next(cat.get_children())

            for thing in cat.get_children():

                try:

                    next(thing.get_children())

                except StopIteration:

                    sub_cats.append(thing)
                    continue

        except StopIteration:

            sub_cats.append(thing)
        
        for _cat in sub_cats:

            items = []

            for item in _cat.get_items():

                items.append(item)

            catalog = Catalog(id=_cat.id,
                              description=_cat.description)

            catalog.add_items(items)

            catalog.normalize_and_save(root_href=str(uuid.uuid1()),
                                       catalog_type=CatalogType.RELATIVE_PUBLISHED)

            catalog.describe()

        
    
if __name__ == '__main__':
    main()