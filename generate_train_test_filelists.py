#!/usr/bin/python
import os
import sys
from os.path import join 


def main(args):

    if len(args) != 4:
        print("Usage: "+sys.argv[0]+" [full laf dir path] [full ltf dir path] [laf training filename] [ltf testing filename]")
        exit(1)

    laf_dir=args[0]
    ltf_dir=args[1]
    laf_training_file=args[2]
    ltf_testing_file=args[3]

    ltf_filenames = []
    ltf_list = ""
    laf_list = ""
    for ltf in os.listdir(ltf_dir):
      if ltf.endswith("ltf.xml"):
        ltf_filenames.append(ltf)

    for i, ltf in enumerate(ltf_filenames):
      if i % 10 == 0:
        ltf_list+=join(ltf_dir, ltf)+'\n'
      else:
        laf_list+=join(laf_dir, ltf.replace('ltf.xml','laf.xml'))+'\n'

    with open(ltf_testing_file, "w") as ltf_script:
      ltf_script.write(ltf_list)
      
    with open(laf_training_file, "w") as laf_script:
      laf_script.write(laf_list)
              
        

if __name__ == '__main__':
    main(sys.argv[1:])
