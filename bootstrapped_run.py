#!/usr/local/bin/python3

import configparser
import glob
import os
import shutil
import tempfile
import sys
import subprocess
import logging
from logger import configure_logger
from io_ import load_doc, LAFDocument
import argparse
from CrfsuiteModel import CrfsuiteModel

logger = None

def bootstrappedNER(io_map, params_map):

#    print("Starting bootstrapped NER with the following parameters:\n"
#            "threshold={}\n"
#            "decrement={}\n"
#            "min_threshold={}".format(threshold_start_val, threshold_decrement, threshold_min))

    global logger
    logger = logging.getLogger()
    configure_logger(logger)
    
    working_dir=io_map['working_dir']
    downsample = float( params_map.get('downsample', 1.0 ) )
    
    if not os.path.exists(working_dir):
        os.makedirs(working_dir)

    """These directories and files are not updated"""
    BASE_LAF_DIR=io_map.get('base_laf_dir', '')   ## Bootstrapping starting point
    LTF_FEATS_DIR=io_map['ltf_feats_dir'] # directory containing LTF files with uhhmm features
    
    TEST_FILE_LIST = write_test_file_list(LTF_FEATS_DIR, working_dir)
    
    gold_laf_dir = io_map.get('gold_laf_dir', None)

    """These values, directories, and files are updated with each iteration"""
    PREV_SYS_LAF_DIR = BASE_LAF_DIR # stores location of previous iteration's output
    FEATS_FILE = None # file containing features eelcted from this iteration for the following iteration
    threshold = float(params_map['init_threshold']) # prob threshold above which NEs are retained, below which rejected
    threshold_min = float(params_map.get('end_threshold', 0.0))
    threshold_decrement = float(params_map.get('decrement', 0.1))
    
    iteration = 0 # number of bootstrapping iteration
    TRAIN_FILE_LIST = os.path.join(working_dir, str(iteration), 'training.list.txt') # file with paths to LAF files for training, one per line
    MODEL_DIR = os.path.join(working_dir, str(iteration), 'model') # directory for trained model
    NEW_NE_DIR = os.path.join(working_dir, str(iteration), 'newNEs') # directory for NEs found in a single iteration
    SYS_LAF_DIR = os.path.join(working_dir, str(iteration), 'output') # directory for tagger output (LAF files)


    changeinNEs = True
    while changeinNEs and (threshold >= threshold_min):

        if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)
        if not os.path.exists(NEW_NE_DIR): os.makedirs(NEW_NE_DIR)
        if not os.path.exists(SYS_LAF_DIR): os.makedirs(SYS_LAF_DIR)
        updateTrainingScript(PREV_SYS_LAF_DIR, TRAIN_FILE_LIST)
       
        if iteration != 0:                  # FEATS_FILE is not None
                traincmd = ["python3",
                            "./train.py", 
                            "--display_progress", 
                            "--max_iter", "50",
#                            "-F", FEATS_FILE,
                            "-S", TRAIN_FILE_LIST, 
                            "-p", str(downsample),
                            MODEL_DIR, 
                            LTF_FEATS_DIR
                           ]
                tagcmd   = ["python3",
                            "./tagger.py", 
#                            "-F", FEATS_FILE,
                            "-S", TEST_FILE_LIST, 
                            "-L", NEW_NE_DIR,
                            "-t", str(threshold),
                            MODEL_DIR
                           ]
        else:                               # FEATS_FILE is None
                traincmd = ["python3",
                            "./train.py", 
                            "--display_progress", 
                            "--max_iter", "50",
                            "-S", TRAIN_FILE_LIST, 
                            "-p", str(downsample),
                            MODEL_DIR, 
                            LTF_FEATS_DIR
                           ]
                tagcmd   = ["python3",
                            "./tagger.py", 
                            "-S", TEST_FILE_LIST, 
                            "-L", NEW_NE_DIR,
                            "-t", str(threshold),
                            MODEL_DIR
                           ]

        # Begin training     
        logger.info("######################################")
        logger.info("Starting training on documents in %s at iteration %d" % (TRAIN_FILE_LIST, iteration) )
        devnull = open(os.devnull, 'w')
        subprocess.call(traincmd, stdout=devnull, stderr=subprocess.STDOUT)

        # Begin tagging
        logger.info("######################################")
        logger.info("Starting tagging of documents in %s at iteration %d and putting in %s" % (TEST_FILE_LIST, iteration, NEW_NE_DIR) )
        subprocess.call(tagcmd)

        # Update values, directories, and files
#        if iteration != 0:
            #print(FEATS_FILE)
        logger.info("########################################")
        logger.info("Comparing previous output in %s to new output in %s and merging into %s" % 
                    (PREV_SYS_LAF_DIR, NEW_NE_DIR, SYS_LAF_DIR) )
        changeinNEs = updateNEdirs(PREV_SYS_LAF_DIR, NEW_NE_DIR, SYS_LAF_DIR)
#        else:
#            SYS_LAF_DIR = NEW_NE_DIR

        PREV_SYS_LAF_DIR = SYS_LAF_DIR

#        FEATS_FILE=os.path.join(working_dir, str(iteration), 'selected_feats.txt')
#        print(FEATS_FILE)
#        select_features(FEATS_FILE, MODEL_DIR, (1.0-threshold))

        threshold-=threshold_decrement
        iteration+=1
        
        TRAIN_FILE_LIST=os.path.join(working_dir, str(iteration), 'training.list.txt')
        MODEL_DIR=os.path.join(working_dir, str(iteration), 'model')
        NEW_NE_DIR=os.path.join(working_dir, str(iteration), 'newNEs')
        SYS_LAF_DIR=os.path.join(working_dir, str(iteration), 'output')
        
        if gold_laf_dir:
            scorecmd = ["python3",
                        "./score.py", 
                        gold_laf_dir,
                        SYS_LAF_DIR, 
                        LTF_FEATS_DIR
                       ]
            subprocess.call(scorecmd)

    print("Bootstrapping stopped after {} iterations".format(iteration))
    if not changeinNEs:
        print("No more NEs were found on the last iteration")
    elif threshold < threshold_min:
        print("Threshold dropped below the minimum")
    else:
        print("Why bootstrapping stopped is unknown")

#     if REF_LAF_DIR != '':
#         scorecmd = ["python3",
#                     "./score.py", 
#                     REF_LAF_DIR, 
#                     SYS_LAF_DIR, 
#                     LTF_FEATS_DIR
#                    ]
# 
#         subprocess.run(scorecmd)
#     else:
#         logging.info("Skipping scoring due to lack of gold LAF directory")


"""
Update TRAIN_FILE_LIST to contain LAF pathnames to be used in training in next iteration
"""
def updateTrainingScript(laf_dir, scriptfile):

    if not os.path.exists(os.path.dirname(scriptfile)):
        os.makedirs(os.path.dirname(scriptfile))

    with open(scriptfile, 'w') as outfile:
        for fn in os.listdir(laf_dir):
            if fn.endswith('laf.xml'):
                outfile.write("{}\n".format(os.path.join(laf_dir, fn)))



"""
Make featsfile for next iteration from features which did not zero out this iteration
"""
def select_features(featsfile, model_dir, fraction):

    modelfile = os.path.join(model_dir, 'tagger.crf')
    model = CrfsuiteModel(modelfile)
    
    with open(featsfile, 'w') as outfile:
        selectedFeats = model.selectFeatures(fraction)
        featstring = '\n'.join(selectedFeats)
        outfile.write(featstring)
         


"""
Add new NE mentions to old NE mentions, if any, 
"""
def updateNEdirs(prev_laf_dir, new_ne_dir, new_laf_dir):

    global logger
    
    changeinNEs = False

    ## Check to see that we have all the files from the previous laf directory in the
    ## new one.
    for fn in glob.glob(prev_laf_dir + "/*.laf.xml"):
#        logger.info("Looking at fn=%s" % (fn) )
        if fn.endswith('laf.xml'):
            prev_laf = os.path.join(prev_laf_dir, fn)
            new_laf = os.path.join(new_ne_dir, fn)
            try:
                assert os.path.exists(new_laf)
                #logger.info("Verified that %s exists" % new_laf)
            except AssertionError:
                logger.warn("{} processed last iteration but not this one".format(fn))
                print("Warning in part 1")
        else:
            logger.info("Fn had wrong file ending")
            
    ## Read all the entity annotations found this iteration and if any did not exist before
    ## this iteration add them to training set.
    print("Looking through ne dir %s" % (new_ne_dir))
    num_new_mentions = 0
    for fn in glob.glob(new_ne_dir + "/*.laf.xml"):
        #logger.info("Looking at fn=%s" % (fn) )
        if fn.endswith('laf.xml'):
            prev_laf = os.path.join(prev_laf_dir, os.path.basename(fn))
            new_laf = os.path.join(new_ne_dir, os.path.basename(fn))
            #print("Reading old LAF %s and new LAF %s" % (prev_laf, new_laf) )
            try:
                assert os.path.exists(prev_laf)
                #print("Verified that %s exists" %  (prev_laf) )
            except AssertionError:
                logger.warn("{} processed this iteration but not the last.  Skipping...".format(fn))
                print("Warning in part 2")
                continue

            prev_laf_doc = load_doc(prev_laf, LAFDocument, logger)
            new_ne_doc = load_doc(new_laf, LAFDocument, logger)
            doc_id = prev_laf_doc.doc_id

            prev_mentions = [[tag, extent, start_char, end_char, start_token, end_token] for [entity_id, tag, extent, start_char, end_char, start_token, end_token] in prev_laf_doc.mentions()]
            prev_spans = [(start_char, end_char) for [tag, extent, start_char, end_char, start_token, end_token] in prev_mentions]
            new_mentions = [[tag, extent, start_char, end_char, start_token, end_token] for [entity_id, tag, extent, start_char, end_char, start_token, end_token] in new_ne_doc.mentions()]
            
            
#            if len(new_mentions) > len(prev_mentions):
#                logger.info("Document %s has %d tagged mentions compared to only %d in the training set." % (new_laf, len(new_mentions), len(prev_mentions) ) )
                
            mentions = []
            for m in prev_mentions:
                # if the NE was found in the previous iterations, it is retained here
                mentions.append(m)
                
            for m in new_mentions:
                # if the NE was found in the previous iterations, it is not overwritten, which means that 
                # the span's label will not be changed even if it is different this iteration
                if (m[2], m[3]) not in prev_spans:
                    #logger.info("Found new mention %s" % (m) )
                    num_new_mentions += 1
                    mentions.append(m)
                    changeinNEs = True

            
            # Sort new mentions list by start_char then end_char
            mentions = sorted(mentions, key = lambda x: (int(x[2]), int(x[3])))

            ## Takes the sorted set of joint mentions and adds with new ids
            n=1
            full_mentions = []
            for tag, extent, start_char, end_char, start_token, end_token in mentions:
                entity_id = '{}-NE{}'.format(doc_id, n)
                full_mentions.append([entity_id, tag, extent, start_char, end_char, start_token, end_token])
                n+=1
                            
            laf = os.path.join(new_laf_dir, os.path.basename(fn))
            laf_doc = LAFDocument(mentions=full_mentions, lang=prev_laf_doc.lang, doc_id=doc_id)
            laf_doc.write_to_file(laf)
            
    print("Found %d _new_ mentions in all documents this iteration" % ( num_new_mentions ) )

    return changeinNEs
    

def write_test_file_list(ltf_dir, working_dir):
    test_file_name = os.path.join(working_dir, "test_file_list.txt")
    fp = open( test_file_name, 'w' )
    for ltf_file in glob.glob(ltf_dir + "/*.ltf.xml"):
        fp.write( ltf_file + "\n")
    
    fp.close()
    return test_file_name

if __name__ == '__main__':
    config = configparser.ConfigParser()

    config.read(sys.argv[1:])
#    logging.basicConfig(level=getattr(logging, "INFO"))
    

    io_map = {}
    for (key,val) in config.items('io'):
        io_map[key] = val
    
    params_map = {}
    for (key,val) in config.items('params'):
        params_map[key] = val

    out_dir = io_map['working_dir']
    with open(out_dir + "/config.ini", 'w') as configfile:
            config.write(configfile)

    if len(sys.argv) < 2:
#        parser.print_help()
        print("%s requires one argument: <config file>" % (sys.argv[0]) )
        sys.exit(1)

    bootstrappedNER(io_map, params_map)

