import requests
from urllib.parse import urlparse

def doi_resolver(doi, token):
    
    asset_href = None
    
    endpoint = 'https://www.doi.org'
    
    handle = f'{endpoint}/api/handles/{doi}'
    
    r = requests.get(url=handle)

    if r.status_code == 404:
        
        return None
    
    deposition_url = r.json()['values'][1]['data']['value']
    
    if urlparse(deposition_url)[1] == 'zenodo.org':
        
        deposition = r.json()['values'][1]['data']['value'].split('/')[-1]
        
        r = requests.get(f'https://zenodo.org/api/deposit/depositions/{deposition}/files',
                 params={'access_token': token})
        
        if r.status_code == 401:
        
            return None
    
        file_id = r.json()[0]['id']
        
        r = requests.get(f'https://zenodo.org/api/deposit/depositions/{deposition}/files/{file_id}',
                 params={'access_token': token})
        
        asset_href = r.json()['links']['download']
        
    return asset_href