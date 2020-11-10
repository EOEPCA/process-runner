import os
import requests
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth
from pystac import STAC_IO

def stac_read_method(uri):
    
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
