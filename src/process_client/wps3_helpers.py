import sys
import logging
import requests
from time import sleep
from urllib.parse import urlparse

logging.basicConfig(stream=sys.stderr,
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')


def to_execute_inputs(process_inputs, process_params):
    execute_inputs = []

    for _input in process_inputs:
        execute_inputs.append({'id': _input['id'],
                               'input': {'dataType': _input['input']['literalDataDomains'][0]['dataType'],
                                         'value': process_params[_input['id']]}})

    return execute_inputs


def poll_status(endpoint, location, interval=30):
    parsed = urlparse(endpoint)

    _endpoint = f'{parsed[0]}://{parsed[1]}'

    r = requests.get(f'{_endpoint}/{location}')

    success = False

    while r.json()['status'] == 'running':

        r = requests.get(f'{_endpoint}/{location}')

        if r.json()['status'] == 'failed':
            logging.info(r.json())

            break

        if r.json()['status'] == 'done':

            success = True

            break

        else:

            logging.info(f'Sleep {interval} seconds')

            sleep(interval)

    return success
