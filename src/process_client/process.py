import os
import sys
import json
import requests
import logging
from time import sleep

logging.basicConfig(stream=sys.stderr,
                    level=logging.INFO,
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%dT%H:%M:%S')


class Process:

    def __init__(self, token, endpoint):

        self.token = token
        self.endpoint = endpoint

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

        r = requests.post(f'{self.endpoint}/processes',
                          json=self._get_deploy_payload(cwl_url),
                          headers=self._get_deploy_headers())

        logging.info('{} - {}, {}'.format(r.status_code, r.reason, r.url))

        return r

    def get_process(self, process_id=None):

        r = None

        if process_id is None:

            r = requests.get(f'{self.endpoint}/processes',
                             headers=self._get_headers())

            logging.info('{} - {}, {}'.format(r.status_code, r.reason, r.url))

        else:

            r = requests.get(f'{self.endpoint}/processes/{process_id}',
                             headers=self._get_headers())

            logging.info('{} - {}, {}'.format(r.status_code, r.reason, r.url))

        return r

    def is_process_deployed(self, process_id):

        r = self.get_process(process_id)

        # logging.info('{} - {}, {}'.format(r.status_code, r.reason, r.url))

        if r.status_code == 200:

            return True

        else:

            return False
