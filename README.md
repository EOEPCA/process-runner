# process-runner

## Build the docker image

```console
docker build -f .docker/Dockerfile -t process-runner:0.1 .
```

## Run the s-expression example

Create the YAML parameter file and update the parameter values according to the deployment. 

The template is:

```yaml
# deployment parameters
application_package: 'https://raw.githubusercontent.com/EOEPCA/app-s-expression/main/app-s-expression.dev.0.0.2.cwl'
process_endpoint: 'http://ades-ref.eoepca.terradue.com/terradue/wps3'  
token: 
access_key: 
secret_key: 

# application parameters
input_reference: 
  - "https://catalog.terradue.com/sentinel2/search?uid=S2A_MSIL2A_20191216T004701_N0213_R102_T53HPA_20191216T024808&do=[terradue]"
cbn: 'ndvi'
s_expression: '(/ (- nir red) (+ nir red))'
```

