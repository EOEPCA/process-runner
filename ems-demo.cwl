
$graph:

- baseCommand: wps3
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
  
  outputs:
    results:
      outputBinding:
        glob: .
      type: Directory
  
  requirements:
    EnvVarRequirement:
      envDef:
        PATH: /opt/anaconda/envs/env_wps3/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
        TOKEN: 'eyJhbGciOiJIUzI1NiIsImtpZCI6IlJTQTEifQ.eyJhY3RpdmUiOnRydWUsImV4cCI6MTU5MzUxNTU2NSwiaWF0IjoxNTkzNTExOTY1LCJuYmYiOm51bGwsInBlcm1pc3Npb25zIjpbeyJyZXNvdXJjZV9pZCI6ImI3Y2FkZTVjLTM3MmYtNGM4Ny1iZTgyLWE3OTU2NDk4ZTcyOSIsInJlc291cmNlX3Njb3BlcyI6WyJBdXRoZW50aWNhdGVkIiwib3BlbmlkIl0sImV4cCI6MTU5MzUxNTU2NCwicGFyYW1zIjpudWxsfV0sImNsaWVudF9pZCI6IjYxY2UyOGQ1LWFhMTYtNGRkYy04NDJmLWZjYzE1OGQzMTVmYSIsInN1YiI6bnVsbCwiYXVkIjoiNjFjZTI4ZDUtYWExNi00ZGRjLTg0MmYtZmNjMTU4ZDMxNWZhIiwiaXNzIjpudWxsLCJqdGkiOm51bGwsInBjdF9jbGFpbXMiOnsiYXVkIjpbIjYxY2UyOGQ1LWFhMTYtNGRkYy04NDJmLWZjYzE1OGQzMTVmYSJdLCJzdWIiOlsiZWIzMTQyMWUtMGEyZS00OTBmLWJiYWYtMDk3MWE0ZTliNzhhIl0sInVzZXJfbmFtZSI6WyJyZGlyaWVuem8iXSwiaXNzIjpbImh0dHBzOi8vZW9lcGNhLWRldi5kZWltb3Mtc3BhY2UuY29tIl0sImV4cCI6WyIxNTkzNTE1NTY0Il0sImlhdCI6WyIxNTkzNTExOTY0Il0sIm94T3BlbklEQ29ubmVjdFZlcnNpb24iOlsib3BlbmlkY29ubmVjdC0xLjAiXX19.A8a-SL0mqmQ-tP0lGQN6QIKAcT4l2LcHoIF5avaD4Yk'
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
      type: string
    wps_endpoint:
      type: string  
  
  outputs:
  - id: wf_outputs
    outputSource:
    - node_1/results
    type: Directory
  
  steps:
  
    node_1:
    
      in:
        inp1: application_package
        inp2: wps_endpoint
        inp3: input_reference
        inp4: aoi
            
      out:
      - results
      
      run: '#wps3'
      
cwlVersion: v1.0
