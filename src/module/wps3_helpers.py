import sys
import logging
from time import sleep

logging.basicConfig(stream=sys.stderr, 
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')

def to_execute_inputs(wps_inputs, wps_params):
    
    execute_inputs = []

    for _input in wps_inputs:

        execute_inputs.append({'id': _input['id'], 
                              'input': {'dataType': _input['input']['literalDataDomains'][0]['dataType'],
                                        'value': wps_params[_input['id']]}})

    return execute_inputs


def poll_status(r, interval=30):
    
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
            
            sleep(interval)

    return success