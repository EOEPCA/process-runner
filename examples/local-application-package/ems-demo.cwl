
$graph:
   
- baseCommand: wps3tool
  class: CommandLineTool
  hints:
    DockerRequirement:
      dockerPull: wps3-runner:0.1
  
  id: wps3_vegetation_index
  
  inputs:
    inp1:
      inputBinding:
        position: 1
        prefix: --application_package_url
      type: File
    inp2:
      inputBinding:
        position: 2
        prefix: --wps_endpoint
      type: string
    inp3:
      inputBinding:
        position: 3
        prefix: --conf
      type: File
    inp4:
      inputBinding:
        position: 4
        prefix: --input_reference
      type: string
    inp5:
      inputBinding:
        position: 5
        prefix: --aoi
      type: string
    inp6:
      type: string
  outputs:
    results:
      outputBinding:
        glob: '*.stac'
      type: File
  
  requirements:
    EnvVarRequirement:
      envDef:
        PATH: /srv/conda/envs/env_wps3/bin/:/opt/anaconda/envs/env_wps3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        TOKEN: $(inputs.inp5)
    ResourceRequirement: {}

- class: Workflow
  label: EMS vegetation index
  doc: EMS vegetation index
  id: main

  inputs:
    aoi:
      doc: Area of interest in WKT
      label: Area of interest
      type: string
    input_reference:
      doc: Sentinel-2 Level-2 acquisition catalog reference
      label: Sentinel-2 Level-2 catalog reference
      type: string
    application_package:
      type: File
    wps_endpoint:
      type: string  
    token: 
      type: string
    conf: 
      type: File
  outputs:
  - id: wf_outputs
    outputSource:
    - step_1/results
    type: File
  
  steps:
  
    step_1:
    
      in:
        inp1: application_package
        inp2: wps_endpoint
        inp3: conf
        inp4: input_reference
        inp5: aoi
        inp6: token
        
      out:
      - results
      
      run: '#wps3_vegetation_index'
      
cwlVersion: v1.0
