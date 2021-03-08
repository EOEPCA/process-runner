$graph:

- baseCommand: process-runner
  class: CommandLineTool
  
  hints:
    DockerRequirement:
      dockerPull: process-runner:0.1
  
  arguments:
        - position: 1
          prefix: --result_method
          valueFrom: 'by-reference'
          
  id: process_s_expression
  
  inputs:
    inp1:
      inputBinding:
        position: 1
        prefix: --application_package_url
      type: string
    inp2:
      inputBinding:
        position: 2
        prefix: --process_endpoint
      type: string
    inp3:
      inputBinding:
        position: 3
        prefix: --input_reference
      type: string
    inp4:
      inputBinding:
        position: 4
        prefix: --s_expression
      type: string
    inp5:
      inputBinding:
        position: 5
        prefix: --cbn
      type: string
    inp6:
      type: string
    inp7:
      type: string
    inp8:
      type: string

  outputs:
    results:
      outputBinding:
        glob: .
      type: Directory
  
  requirements:
    EnvVarRequirement:
      envDef:
        PATH: /srv/conda/envs/env_process/bin:/opt/anaconda/envs/env_process/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        TOKEN: $(inputs.inp6)
        AWS_SECRET_ACCESS_KEY: $(inputs.inp7)
        AWS_ACCESS_KEY_ID: $(inputs.inp8)
    ResourceRequirement: {}
    InlineJavascriptRequirement: {}

- class: Workflow
  label: EMS s expression
  doc: EMS s expression
  id: main

  inputs:
    cbn:
      doc: Common band name for s-expression result 
      label: Common band name
      type: string
    input_reference:
      doc: EO optical acquisition
      label: EO optical acquisition
      type: string[]
    s_expression:
      doc: S expression
      label: S expression
      type: string
    application_package:
      type: string
    process_endpoint:
      type: string  
    token: 
      type: string
    s3k1:
      type: string
    s3k2:
      type: string   
  outputs:
  - id: wf_outputs
    outputSource:
    - step_s_expression/results
    type: 
      items: Directory
      type: array
  
  requirements:
  - class: ScatterFeatureRequirement
  - class: MultipleInputFeatureRequirement
  
  steps:
  
    step_s_expression:
    
      in:
        inp1: application_package
        inp2: process_endpoint
        inp3: input_reference
        inp4: s_expression
        inp5: cbn   
        inp6: token
        inp7: s3k1
        inp8: s3k2 
      
      out:
      - results
      
      scatter: inp3
      scatterMethod: dotproduct
      
      run: '#process_s_expression'
      
cwlVersion: v1.0
