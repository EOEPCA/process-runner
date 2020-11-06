import click
import os
import json
from time import sleep
from .execution import Execution
from .workflow import Workflow
from .process import Process

def to_execute_inputs(wps_inputs, wps_params):
    
    execute_inputs = []

    for _input in wps_inputs:

        execute_inputs.append({'id': _input['id'], 
                              'input': {'dataType': _input['input']['literalDataDomains'][0]['dataType'],
                                        'value': wps_params[_input['id']]}})

    return execute_inputs


@click.command(name='wps3', context_settings=dict(
    ignore_unknown_options=True,
    allow_extra_args=True,
))
@click.option('--application_package_url')
@click.option('--wps_endpoint')
@click.pass_context
def main(ctx, application_package_url, wps_endpoint):
    
    _wps_params = {ctx.args[i][2:]: ctx.args[i+1] for i in range(0, len(ctx.args), 2)}
    
    token = os.environ['TOKEN']
    
    # get process id
    app_package = Workflow(application_package_url)
    process_id = app_package.get_workflow_id()
    process_id = f'{process_id}_'.replace('-', '_')
    print(process_id)
    
    # check 
    ades = Process(token)
    
    r = ades.get_process()
    
    print(r.status_code, r.reason, r.url)
    
    if not True: #is_process_deployed(f'{process_id}_'):
        
        print('Deploy process')
        
        r = ades.deploy_process(application_package_url)
    
        if r.status_code is not 201:
            
            raise Exception('Process not deployed')
        
    r = ades.get_process(process_id)
    
    print(r.status_code, r.reason, r.url)
    
    # submit execution
    wps_inputs = r.json()['process']['inputs']
    
    execute_inputs = to_execute_inputs(wps_inputs, 
                                       _wps_params)
    
    print(execute_inputs)  
    
    execution = Execution(token, process_id)
    
    r = execution.execute_process(execute_inputs)

    print(r.status_code, r.reason, r.url)
    
    # status monitoring
    print('polling')
    r = execution.get_status()
    
    print(r.status_code, r.reason, r.url)
    
    success = False
    
    while r.json()['status'] == 'running':

        r = execution.get_status()

        if r.json()['status'] == 'failed': 

            print(r.json())

            break

        if r.json()['status'] == 'successful':  

            print(r.json()['links'][0]['href'])

            success = True
            
            break

        else:

            print('Polling - {}'.format(r.json()['status']))

            sleep(30)

    if not success:
        
        print(r.json())
        
        sys.exit(1)    
        
    # get the results
    r = execution.get_result()

    print(r.status_code, r.reason, r.url)

    if success: 
        
        results = json.loads(r.json()['outputs'][0]['value']['inlineValue'])

        print(results)

        stac_catalog_endpoint = results['stac:catalog']['href']

        print(stac_catalog_endpoint)
    
    
if __name__ == '__main__':
    main()