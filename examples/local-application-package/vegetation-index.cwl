$graph:
- baseCommand: vegetation-index
  class: CommandLineTool
  hints:
    DockerRequirement:
      dockerPull: terradue/nb-vegetation-index:latest
  id: vegetation
  inputs:
    inp1:
      inputBinding:
        position: 1
        prefix: --input_reference
      type: Directory
    inp2:
      inputBinding:
        position: 2
        prefix: --aoi
      type: string
  outputs:
    results:
      outputBinding:
        glob: .
      type: Directory
  requirements:
    EnvVarRequirement:
      envDef:
        PATH: /opt/anaconda/envs/env_vegetation_index/bin:/opt/anaconda/envs/env_vegetation_index/bin:/opt/anaconda/envs/env_default/bin:/opt/anaconda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        PREFIX: /opt/anaconda/envs/env_vegetation_index
    ResourceRequirement: {}
  stderr: std.err
  stdout: std.out
- class: Workflow
  label: Vegetation index
  doc: Vegetation index
  id: nb-vegetation-index
  inputs:
    input_reference:
      doc: Sentinel-2 Level-2 acquisition catalog reference
      label: Sentinel-2 Level-2 catalog reference
      type: Directory[]
    aoi:
      doc: Area of interest in WKT
      label: Area of interest
      type: string
  outputs:
  - id: wf_outputs
    outputSource:
    - vegetation-index/results
    type:
      items: Directory
      type: array
  requirements:
  - class: ScatterFeatureRequirement
  steps:
    vegetation-index:
      in:
        inp1: input_reference
        inp2: aoi
      out:
      - results
      run: '#vegetation'
      scatter: inp1
      scatterMethod: dotproduct
cwlVersion: v1.0 
