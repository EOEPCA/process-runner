import os
import yaml
import tempfile
import subprocess
import json
import requests
from urllib.parse import urlparse

endpoint = 'http://ades-dev.eoepca.terradue.com' 

namespace = 'terradue'

cwltool = '/opt/anaconda/bin/cwltool'

class Workflow():
    
    def __init__(self, cwl_uri):

        parsed = urlparse(cwl_uri)
    
        if parsed.scheme.startswith('http'):
            
            r = requests.get(cwl_uri)
            
            cwl = yaml.safe_load(r.content.decode())

        else: 
            
            cwl = self._read_cwl(cwl_uri)
        
        self.cwl = cwl
        self.cwl_uri = cwl_uri
        self.result = None

        
    def _read_cwl(self, cwl_file):
    
        with open(cwl_file) as file:

            cwl = yaml.load(file,
                        Loader=yaml.FullLoader)

        return cwl
        
    def get_workflow_class(self):

        cwl_workflow = None

        for block in self.cwl['$graph']:

            if block['class'] == 'Workflow':

                cwl_workflow = block

                break

        return cwl_workflow

    def get_workflow_id(self):
        
        if self.get_workflow_class() is not None:
            
            return self.get_workflow_class()['id']
    
        else:
            
            return None

    def get_workflow_inputs(self):

        wf = self.get_workflow_class()
        
        if wf is not None:
        
            return wf['inputs']
        
        else:
            
            return None

    def process_worflow(self, params):

        temp_params_file = os.path.join('/tmp', next(tempfile._get_candidate_names()))
        temp_cwl_file = os.path.join('/tmp', next(tempfile._get_candidate_names()))
        
        with open(temp_params_file, 'w') as yaml_file:

            yaml.dump(params,
                      yaml_file, 
                      default_flow_style=False)

        
        with open(temp_cwl_file, 'w') as yaml_file:

            yaml.dump(self.cwl,
                      yaml_file, 
                      default_flow_style=False)

        # invoke cwltool
        cmd_args = [cwltool, 
                    '--no-read-only',
                    '--no-match-user',
                    '{}#{}'.format(temp_cwl_file, 
                                   self.get_workflow_id()), 
                    temp_params_file]

        print(' '.join(cmd_args))

        pipes = subprocess.Popen(cmd_args, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)

        std_out, std_err = pipes.communicate()

        os.remove(temp_params_file)

        self.result = json.loads(std_out.decode())
        
        return std_out, std_err

    def get_catalog(self):

        if self.result == None:
            
            return None
        
        if type(self.result['wf_outputs']) is list and self.result['wf_outputs'][0] is None:

            raise ValueError('Empty results')

        stac_catalog = None

        staged_stac_catalogs = []


        if type(self.result['wf_outputs']) is dict:

            for index, listing in enumerate(self.result['wf_outputs']['listing']):

                if listing['class'] == 'File':

                    if (listing['basename']) == 'catalog.json':

                        stac_catalog = listing['location']

                    break

        elif type(self.result['wf_outputs']) is list:

            for index, listing in enumerate(self.result['wf_outputs']):

                for sublisting in listing['listing']:

                    if (sublisting['basename']) == 'catalog.json':
                        stac_catalog = sublisting['location']

                        break

        return stac_catalog

class Process:
    
    def __init__(self, token):
        
        self.endpoint = 'http://ades-dev.eoepca.terradue.com' 
        self.namespace = 'terradue'
        
        self.token = token
        
    def _get_deploy_payload(self, url):

        deploy_payload = {'inputs': [{'id': 'applicationPackage',
                                  'input': {'format': {'mimeType': 'application/cwl'},
                                            'value': {'href': '{}'.format(url)}}}],
                      'outputs': [{'format': {'mimeType': 'string',
                                              'schema': 'string',
                                              'encoding': 'string'},
                                   'id': 'deployResult',
                                   'transmissionMode': 'value'}],
                      'mode': 'auto',
                      'response': 'raw'}

        return deploy_payload

    def _get_headers(self):

        headers = {'Authorization': f'Bearer {self.token}',
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'}
        
        return headers

    def _get_deploy_headers(self):

        deploy_headers = self._get_headers()
        
        deploy_headers['Prefer'] = 'respond-async'

        return deploy_headers

    def deploy_process(self, cwl_url):

        r = requests.post(f'{self.endpoint}/{self.namespace}/wps3/processes',
                          json=self._get_deploy_payload(cwl_url),
                          headers=self._get_deploy_headers())

        return r

    def get_process(self, process_id=None):

        r = None
        
        if process_id is None:

            r = requests.get(f'{self.endpoint}/{self.namespace}/wps3/processes',
                                headers=self._get_headers())

        else:

            r = requests.get(f'{self.endpoint}/{self.namespace}/wps3/processes/{process_id}',
                                headers=self._get_headers())
        
        return r
    
    def is_process_deployed(self, process_id):
        
        r = self.get_process(process_id)
        
        if r.status_code == 200:
            
            return True
        
        else:
            
            return False

class Execution:
    
    def __init__(self, token, process_id):
        
        self.endpoint = 'http://ades-dev.eoepca.terradue.com' 
        self.namespace = 'terradue'
        
        self.token = token
        self.process_id = process_id
        self._job_location = None
        
    def execute_process(self, execute_inputs):
    
        execution_headers = {'Authorization': f'Bearer {self.token}',
                           'Content-Type': 'application/json',
                           'Accept': 'application/json', 
                           'Prefer': 'respond-async'}

        execute_request = {'inputs': execute_inputs,
                           'outputs': [{'format': {'mimeType': 'string',
                                                   'schema': 'string',
                                                   'encoding': 'string'},
                                        'id': 'wf_output',
                                        'transmissionMode': 'value'}],
                           'mode': 'async',
                           'response': 'raw'}

        r = requests.post(f'{self.endpoint}/{self.namespace}/wps3/processes/{self.process_id}/jobs',
                             json=execute_request,
                             headers=execution_headers)

        if r.status_code == 201:
            
            self._job_location = r.headers['Location']
 
        return r
        
    def get_job_location(self):
        
        return f'{self.endpoint}{self._job_location}'
    
    def _get_headers(self, token):

        headers = {'Authorization': f'Bearer {self.token}',
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'}
    
    def get_status(self):

        if self._job_location is None:
            
            return None
        
        r = requests.get(f'{self.endpoint}{self._job_location}',
                         headers=self._get_headers(self.token))
        
        return r

    def get_result(self):
        
        if self._job_location is None:
            
            return None

        r = requests.get(f'{self.endpoint}/{self._job_location}/result',
                         headers=self._get_headers(self.token))
        
        return r
