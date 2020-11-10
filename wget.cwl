$graph:


- baseCommand: wget
  class: CommandLineTool
  id: stub
  
  requirements:
    - class: InlineJavascriptRequirement
  
  inputs:
    datafile:
        type: File
        inputBinding:
          position: 1
          loadContents: true
          valueFrom: $(inputs.datafile.contents)  
      
  outputs:
    processedoutput:
      type: Any
      
      
cwlVersion: v1.0