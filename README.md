# uhhmm_NER

# To run an experiment, use the following command:
#       ./run.sh [language]
# But this should be done after the directories have been configured inside run.sh.
# Also, the features to be used should be properly configured inside features.py, starting on line 70.

# All paths in run.sh should be changed to the directories or files containing the necessary data.

# The commented experiments inside run.sh can be uncommented to be repeated.  However, when running any experiment from 
# run.sh, it is important to ensure that features.py (l.70 and below) has been configured to include those features 
# and only those features which the experiment expects to be a part of its model.
# Experiments will not produce errors if this is not the case; however, the results will not be accurate 
# since the features reported to have been used were not.

# Any TRAIN_SCP and TEST_SCP text files will have to be created.

# When training on all data, bash commands which concatenate the paths to the LAF and LTF files respectively are useful.
# When training on all data, the following command could be used to create the TRAIN_SCP:
# for fn in $(ls [LAF-DIR]); do echo "[LAF-DIR]${fn}" >> [TRAIN_SCP]; done
# When testing on all data, the following command could be used to create the TEST_SCP:
# for fn in $(ls [LTF-DIR]); do echo "[LTF-DIR]${fn}" >> [TEST_SCP]; done

# When splitting into training and testing sets, generate_train_test_filelists.py will be helpful. 

