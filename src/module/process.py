import os
import json
import requests

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
        
        if r.status_code == True:
            
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
