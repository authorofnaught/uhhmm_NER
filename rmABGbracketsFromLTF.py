import re, sys, glob, os

def replaceABGinLTF(inltf, outltf):
    with open(inltf, 'r') as infile:
        with open(outltf, 'w') as outfile:
            outfile.write(re.sub(r'([abgfj]=")\[(-?[0-9]+)\](")',r'\1\2\3',infile.read()))

if __name__ == '__main__':

    files=glob.glob(sys.argv[1]+"/*.ltf.xml")
    for fn in files:
        replaceABGinLTF(fn, os.path.join(sys.argv[2], os.path.basename(fn)))
