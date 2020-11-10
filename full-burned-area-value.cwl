$graph:
- baseCommand: burned-area-delineation
  class: CommandLineTool
  hints:
    DockerRequirement:
      dockerPull: terradue/nb-burned-area-delineation:latest
  id: delineation
  inputs:
    inp1:
      inputBinding:
        position: 1
        prefix: --pre_event
        valueFrom: $(inputs.inp1[0])
      type: Directory[]
    inp2:
      inputBinding:
        position: 2
        prefix: --post_event
        valueFrom: $(inputs.inp2[1])
      type: Directory[]
    inp3:
      inputBinding:
        position: 3
        prefix: --ndvi_threshold
      type: string
    inp4:
      inputBinding:
        position: 4
        prefix: --ndwi_threshold
      type: string
  outputs:
    results:
      outputBinding:
        glob: .
      type: Directory
  requirements:
    InlineJavascriptRequirement: {}
    EnvVarRequirement:
      envDef:
        PATH: /opt/anaconda/envs/env_burned_area_delineation/bin:/opt/anaconda/envs/env_burned_area_delineation/bin:/opt/anaconda/envs/env_default/bin:/opt/anaconda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        PREFIX: /opt/anaconda/envs/env_burned_area_delineation
    ResourceRequirement: {}
  stderr: std.err
  stdout: std.out
  
- baseCommand: wps3tool
  class: CommandLineTool
  hints:
    DockerRequirement:
      dockerPull: wps3-runner:0.1
  arguments:
        - position: 1
          prefix: --result_method
          valueFrom: 'by-value'
  id: wps3_vegetation_index
  
  inputs:
    inp1:
      inputBinding:
        position: 2
        prefix: --application_package_url
      type: string
    inp2:
      inputBinding:
        position: 3
        prefix: --wps_endpoint
      type: string
    inp3:
      inputBinding:
        position: 4
        prefix: --input_reference
      type: string
    inp4:
      inputBinding:
        position: 5
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
    ndvi_threshold:
      doc: NDVI difference threshold
      label: NDVI difference threshold
      type: string
    ndwi_threshold:
      doc: NDWI difference threshold
      label: NDWI difference threshold
      type: string
    application_package_vi:
      type: string
    wps_endpoint:
      type: string  
    token: 
      type: string
  
  outputs:
  - id: wf_outputs
    outputSource:
    - delineation/results
    type: Directory
  
  requirements:
  - class: ScatterFeatureRequirement
  - class: MultipleInputFeatureRequirement
  
  steps:
  
    vegetation-index:
    
      in:
        inp1: application_package_vi
        inp2: wps_endpoint
        inp3: input_reference
        inp4: aoi
        inp5: token    
      
      out:
      - results
      
      scatter: inp3
      scatterMethod: dotproduct
      
      run: '#wps3_vegetation_index'
      
      
    delineation:
    
      in:
        inp1: vegetation-index/results
        inp2: vegetation-index/results
        inp3: ndvi_threshold
        inp4: ndwi_threshold
    
      out:
      - results
      
      run: '#delineation'
      
cwlVersion: v1.0
