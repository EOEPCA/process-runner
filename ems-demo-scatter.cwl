
$graph:

- baseCommand: wps3tool
  class: CommandLineTool
  hints:
    DockerRequirement:
      dockerPull: eoepca/wps3-runner:0.1
  
  id: wps3
  
  inputs:
    inp1:
      inputBinding:
        position: 1
        prefix: --application_package_url
      type: string
    inp2:
      inputBinding:
        position: 2
        prefix: --wps_endpoint
      type: string
    inp3:
      inputBinding:
        position: 3
        prefix: --input_reference
      type: string
    inp4:
      inputBinding:
        position: 4
        prefix: --aoi
      type: string
    inp5:
      type: string
  
  outputs:
    results:
      outputBinding:
        glob: .
      type: Directory
  
  requirements:
    EnvVarRequirement:
      envDef:
        PATH: /opt/anaconda/envs/env_wps3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
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
      type: string[]
    application_package:
      type: string
    wps_endpoint:
      type: string  
    token: 
      type: string
  outputs:
  - id: wf_outputs
    outputSource:
    - node_1/results
    type: Directory[]
  
  requirements:
  - class: ScatterFeatureRequirement
  
  steps:
  
    node_1:
    
      in:
        inp1: application_package
        inp2: wps_endpoint
        inp3: input_reference
        inp4: aoi
        inp5: token    
      out:
      - results
      
      scatter: inp3
      scatterMethod: dotproduct
      
      run: '#wps3'
      
cwlVersion: v1.0
