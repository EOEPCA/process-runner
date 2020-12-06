import os
import yaml
import tempfile
import subprocess
import json
import requests
import lxml.etree as etree
from urllib.parse import urlparse
from .conf import read_configuration
from .doi import doi_resolver


class Workflow:

    def __init__(self, cwl_uri, conf):

        configuration = read_configuration(conf)

        self.zenodo_token = configuration['zenodo']['token']
        self.cwltool = configuration['cwltool']

        parsed = urlparse(cwl_uri)

        if parsed.scheme.startswith('http'):

            r = requests.get(cwl_uri, stream=True)

            if r.headers['Content-Type'] == 'application/atom+xml':

                namespaces = {'atom': 'http://www.w3.org/2005/Atom',
                              'owc': 'http://www.opengis.net/owc/1.0'}

                offering_code = 'http://www.opengis.net/eoc/applicationContext/cwl'

                xml = etree.parse(r.raw)

                raw_cwl = xml.xpath(f'/atom:feed/atom:entry/owc:offering[@code="{offering_code}"]/owc:content',
                                    namespaces=namespaces)[0].text

                cwl = yaml.safe_load(raw_cwl)

            else:

                cwl = yaml.safe_load(r.content.decode())

        else:

            cwl = self._read_cwl(cwl_uri)

        self.cwl = cwl
        self.cwl_uri = cwl_uri
        self.result = None

    def _read_cwl(self, cwl_file):

        if os.path.isfile(cwl_file):

            with open(cwl_file) as file:

                cwl = yaml.load(file,
                                Loader=yaml.FullLoader)

        else:

            r = requests.get(doi_resolver(cwl_file, self.zenodo_token),
                             params={'access_token': self.zenodo_token})

            cwl = yaml.safe_load(r.text)

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
        cmd_args = [self.cwltool,
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
        os.remove(temp_cwl_file)

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
