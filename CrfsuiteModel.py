import re
import sys
import os
from collections import defaultdict
import shutil
import tempfile
import operator

class CrfsuiteModel:

    def __init__(self, modelfile, write_dump=True):
        self.fileheader = {}
        self.labels = []
        self.attributes = []
        self.transitions = defaultdict(dict)
        self.state_features = defaultdict(dict)
        self.feats = set()

        if not write_dump:
            dump_dir = tempfile.mkdtemp()
        else:
            dump_dir = os.path.dirname(modelfile)
        dumpfile = os.path.join(dump_dir, 'dump.txt')

        cmd = "crfsuite dump {} > {}".format(modelfile, dumpfile)
        os.system(cmd)

        with open(dumpfile, 'r') as model:
            for line in model:
                try:
                    line = line.strip()
                    if "FILEHEADER" in line:
                        section = "FILEHEADER"
                    elif "LABELS" in line:
                        section = "LABELS"
                    elif "ATTRIBUTES" in line:
                        section = "ATTRIBUTES"
                    elif "TRANSITIONS" in line:
                        section = "TRANSITIONS"
                    elif "STATE_FEATURES" in line:
                        section = "STATE_FEATURES"
                    elif ":" in line:

                        key, val = line.split(':')

                        if section == "FILEHEADER":
                            self.fileheader[key.strip()] = val.strip()

                        elif section == "LABELS":
                            self.labels.append(val.strip())

                        elif section == "ATTRIBUTES":
                            self.attributes.append(val.strip())
                            pattern = re.compile(r"F[0-9]+")
                            match = re.search(pattern, val)
                            self.feats.update([match.group()])

                        elif section == "TRANSITIONS":
                            t0, t1 = [x.strip() for x in key.replace('(0)','').strip().split('-->')]
                            self.transitions[t0][t1] = float(val.strip())

                        elif section == "STATE_FEATURES":
                            state, token = [x.strip() for x in key.replace('(1)','').strip().split('-->')]
                            self.state_features[state][token] = float(val.strip())

                        else:
                            print("Something went wrong parsing the model dump file.")
                            sys.exit(1)
                    else:
                        continue
                except:
                    continue

        if not write_dump:
            shutil.rmtree(dump_dir)


    def selectFeatures(self, fractionOfFeats=0.5):

        numFeats = int(len(self.feats) * fractionOfFeats)
        if numFeats < 1:
            numFeats = 1

        featureCoeffs = defaultdict(float)

        for state in self.state_features:
            try:
                pattern = re.compile(r"F[0-9]+")
                match = re.search(pattern, state)
                feat = match.group() 
                for token in self.state_features[state]:
                    featureCoeffs[feat] += abs(self.state_features[state][token])
            except:
                continue

        sortedCoeffs = sorted(featureCoeffs.items(), key=operator.itemgetter(1), reverse=True)
        selectedFeats = [i[0] for i in sortedCoeffs[:(numFeats+1)]]
        return selectedFeats 
