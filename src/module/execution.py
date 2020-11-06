import os
import json
import requests

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
