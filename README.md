# uhhmm_NER

# Use run.sh to run and score experiments with A, B, and G as their own features or in combination.
# Only those experiments should be uncommented which expect the features which features.py has currently been configured to produce.

# To make changes to the kinds of ABG features included in feature sets, edit features.py.
# Experiments will not correctly unless features.py has been edited to include only those features which are expected.

# All paths in run.sh should be changed to the directories or files containing the necessary data.

# Any TRAIN_SCP and TEST_SCP text files will have to be created using bash commands which concatenate the paths to the LAF and LTF files respectively.
# The following command could be used to create the TRAIN_SCP:
# for fn in $(ls [LAF-DIR]); do echo "[LAF-DIR]${fn}" >> [TRAIN_SCP]; done
# The following command could be used to create the TEST_SCP:
# for fn in $(ls [LTF-DIR]); do echo "[LTF-DIR]${fn}" >> [TEST_SCP]; done

