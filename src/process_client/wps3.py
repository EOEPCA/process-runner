import click
import os
import sys
import json

import logging
from .execution import Execution
from .workflow import Workflow
from .process import Process
from .stac import stac_read_method
from .wps3_helpers import to_execute_inputs, poll_status
from .conf import read_configuration
from pystac import *
import requests
import uuid
from time import sleep

logging.basicConfig(stream=sys.stderr,
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

STAC_IO.read_text_method = stac_read_method


def check_code(r, http_status):
    if r.status_code == http_status:

        return True

    else:

        return False


@click.command(name='process', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option('--application_package_url')
@click.option('--process_endpoint')
@click.option('--result_method', default='by-reference')
@click.option('--conf', default=None)
@click.pass_context
def entry(ctx, application_package_url, process_endpoint, result_method, conf):
    process_params = {ctx.args[i][2:]: ctx.args[i + 1] for i in range(0, len(ctx.args), 2)}

    main(process_params, application_package_url, process_endpoint, result_method, conf)


def main(process_params, application_package_url, process_endpoint, result_method, conf):
    configuration = read_configuration(conf)

    os.environ['STAGEIN_USERNAME'] = configuration['stage-in']['username']
    os.environ['STAGEIN_PASSWORD'] = configuration['stage-in']['password']
    token = os.environ['TOKEN']

    # get process id
    app_package = Workflow(application_package_url, conf)
    #process_id = app_package.get_workflow_id()
    process_id = app_package.get_identifier()
    #process_id = f'{process_id}_'.replace('-', '_')

    logging.info(f'Process id: {process_id}')

    # check is the WPS endpoint provided is ok
    ades = Process(token=token,
                   endpoint=process_endpoint)

    try:

        r = ades.get_process()

    except requests.exceptions.ConnectionError:

        logging.info(f'Could not contact the WPS endpoint at {process_endpoint}')

        sys.exit(1)

    logging.info(f'Checking if process {process_id} is deployed')

    if not ades.is_process_deployed(f'{process_id}'):

        logging.info(f'Deploy process from application package {application_package_url}')

        r = ades.deploy_process(application_package_url)

        if not check_code(r, 201):
            raise Exception(f'{r.status_code} - Process not deployed, see exception')

            sys.exit(1)

        poll_status(process_endpoint, r.headers['Location'], 3)

        if not ades.is_process_deployed(process_id):
            logging.info(f'Tried to deploy {process_id}, got a 201 but the process is not deployed')

            raise Exception(f'{r.status_code} - HTTP code 201 but the process is not deployed')

            sys.exit(1)

    else:

        logging.info(f'Process {process_id} is deployed')

    # describe process
    r = ades.get_process(process_id)

    if not check_code(r, 200):
        raise Exception(f'{r.status_code} - Describe process request failed')

        sys.exit(1)

    # submit execution
    process_inputs = r.json()['process']['inputs']

    # _process_params = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}

    execute_inputs = to_execute_inputs(process_inputs,
                                       process_params)

    logging.info(execute_inputs)

    execution = Execution(token=token,
                          process_id=process_id,
                          endpoint=process_endpoint)

    r = execution.execute_process(execute_inputs)

    if not check_code(r, 201):
        raise Exception(f'{r.status_code} - Execute request failed')

        sys.exit(1)

    # status monitoring
    success = execution.monitor(30)

    if not success:
        logging.info('Processing failed')

        sys.exit(1)

        # get the results

    results = execution.get_results()

    if 'StacCatalogUri' not in results.keys():
        logging.info('The job didn\'t produce a STAC catalog')

        sys.exit(1)

    # stage-in the STAC catalog(s)    
    stac_catalog_endpoint = results['StacCatalogUri']

    logging.info(stac_catalog_endpoint)

    cat = Catalog.from_file(stac_catalog_endpoint)
    print(cat)
    sub_cats = []

    thing = None

    try:
        next(cat.get_children())
        for thing in cat.get_children():

            try:

                next(thing.get_children())

            except StopIteration:

                sub_cats.append(thing)
                continue

    except StopIteration:

        sub_cats.append(cat)

    if result_method == 'by-reference':

        results = []
        # pass the catalog href 
        for index, _cat in enumerate(sub_cats):
            results.append(f'result_{index}.stac')

            with open(f'result_{index}.stac', 'w') as text_file:
                text_file.write(_cat.get_self_href())

        return results

    elif result_method == 'by-value':

        results = []
        # stage the STAC catalogs locally leaving the assets remote
        for index, _cat in enumerate(sub_cats):

            items = []

            for item in _cat.get_items():
                items.append(item)

            catalog = Catalog(id=_cat.id,
                              description=_cat.description)

            catalog.add_items(items)

            if len(sub_cats) == 1:

                catalog.normalize_and_save(root_href='./',
                                           catalog_type=CatalogType.RELATIVE_PUBLISHED)
            else:

                catalog.normalize_and_save(root_href=str(uuid.uuid1()),
                                           catalog_type=CatalogType.RELATIVE_PUBLISHED)

            catalog.describe()

            results.append(catalog.get_self_href())

        return results

    else:

        raise Exception(f'method method {result_method} not supported')

        sys.exit(1)


if __name__ == '__main__':
    entry()
