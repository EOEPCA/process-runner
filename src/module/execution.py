import os
import sys
import logging
import json
import requests
from urllib.parse import urlparse
from time import sleep

logging.basicConfig(stream=sys.stderr, 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

class Execution:
    
    def __init__(self, token, endpoint, process_id):
        
        self.endpoint = endpoint  
        self.token = token
        self.process_id = process_id
        self._job_location = None
        self.results = None
        
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

        r = requests.post(f'{self.endpoint}/processes/{self.process_id}/jobs',
                             json=execute_request,
                             headers=execution_headers)

        logging.info('{} - {}, {}'.format(r.status_code, r.reason, r.url))
        
        if r.status_code == 201:
            
            parsed = urlparse(self.endpoint)
        
            _endpoint = f'{parsed[0]}://{parsed[1]}'
            
            location = r.headers['Location']
            
            self._job_location = f'{_endpoint}/{location}'
 
        return r
        
    def get_job_location(self):
       
        return self._job_location
    
    def _get_headers(self, token):

        headers = {'Authorization': f'Bearer {self.token}',
                   'Content-Type': 'application/json',
                   'Accept': 'application/json'}
    
    def get_status(self):

        if self._job_location is None:
            
            return None
        
        r = requests.get(f'{self._job_location}',
                         headers=self._get_headers(self.token))
        
        logging.info('{} - {}, {}'.format(r.status_code, r.reason, r.url))
        
        return r

    def get_result(self):
        
        if self._job_location is None:
            
            return None

        r = requests.get(f'{self._job_location}/result',
                         headers=self._get_headers(self.token))
        
        logging.info('{} - {}, {}'.format(r.status_code, r.reason, r.url))
        
        return r

    def get_job_id(self):
        
        r = self.get_status()
    
        return r.json()['jobID']
    
    def get_results(self):
        
        return self.results
    
    def monitor(self, interval):
        
        r = self.get_status()
    
        logging.info(f'Polling status at {r.url} for job id: {self.get_job_id()}')
    
        success = False
    
        while r.json()['status'] == 'running':

            r = self.get_status()

            if r.json()['status'] == 'failed': 

                logging.info(r.json())

                break

            if r.json()['status'] == 'successful':  
                
                logging.info(r.json()['links'][0]['href'])

                success = True
                
                r = self.get_result()
                
                if len(r.json()['outputs']) == 1: 
                    
                    if 'value' in r.json()['outputs'][0].keys():
                                                
                        if 'inlineValue' in r.json()['outputs'][0]['value'].keys():
                            
                            self.results = json.loads(r.json()['outputs'][0]['value']['inlineValue'])
                
                break

            else:
                progress = r.json()['progress']
                status = r.json()['status']

                logging.info(f'Polling - {status}, {progress} %')

                sleep(interval)

        return success