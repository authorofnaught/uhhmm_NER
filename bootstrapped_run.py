#!/usr/local/bin/python3
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


def bootstrappedNER(lang, working_dir_name, 
                    threshold_start_val, threshold_decrement, threshold_min, 
                    max_iterations=sys.maxsize):

    print("Starting bootstrapped NER with the following parameters:\n"
            "threshold={}\n"
            "decrement={}\n"
            "min_threshold={}".format(threshold_start_val, threshold_decrement, threshold_min))

    logger = logging.getLogger()
    configure_logger(logger)
    working_dir=os.path.join("/Users/authorofnaught/Projects/LORELEI/NER/WORKING/", os.path.basename(working_dir_name))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)

    """These directories and files are not updated"""
    REF_LAF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/REF-LAF/"+lang+"335/" # directory containing gold standard LAF files
    LTF_DIR="/Users/authorofnaught/Projects/LORELEI/NER/LTF-ABG/"+lang+"/" # directory containing LTF files with uhhmm features
    TEST_SCP="/Users/authorofnaught/Projects/LORELEI/NER/TEST-SCP/"+lang+"335.txt" # file with paths to LTF files for tagging, one per line

    """These values, directories, and files are updated with each iteration"""
    PREV_SYS_LAF_DIR = REF_LAF_DIR # stores location of previous iteration's output
    FEATS_FILE = None # file containing features eelcted from this iteration for the following iteration
    threshold = threshold_start_val # prob threshold above which NEs are retained, below which rejected
    iteration = 0 # number of bootstrapping iteration
    TRAIN_SCP = os.path.join(working_dir, str(iteration), 'training.list.txt') # file with paths to LAF files for training, one per line
    MODEL_DIR = os.path.join(working_dir, str(iteration), 'model') # directory for trained model
    NEW_NE_DIR = os.path.join(working_dir, str(iteration), 'newNEs') # directory for NEs found in a single iteration
    SYS_LAF_DIR = os.path.join(working_dir, str(iteration), 'output') # directory for tagger output (LAF files)


    changeinNEs = True
    while changeinNEs and (threshold >= threshold_min):

        if not os.path.exists(MODEL_DIR): os.makedirs(MODEL_DIR)
        if not os.path.exists(NEW_NE_DIR): os.makedirs(NEW_NE_DIR)
        if not os.path.exists(SYS_LAF_DIR): os.makedirs(SYS_LAF_DIR)
        updateTrainingScript(PREV_SYS_LAF_DIR, TRAIN_SCP)
       
        if iteration != 0:                  # FEATS_FILE is not None
                traincmd = ["python3",
                            "./train.py", 
                            "--display_progress", 
                            "--max_iter", "5",
                            "-F", FEATS_FILE,
                            "-S", TRAIN_SCP, 
                            MODEL_DIR, 
                            LTF_DIR
                           ]
                tagcmd   = ["python3",
                            "./tagger.py", 
                            "-F", FEATS_FILE,
                            "-S", TEST_SCP, 
                            "-L", NEW_NE_DIR,
                            "-t", str(threshold),
                            MODEL_DIR
                           ]
        else:                               # FEATS_FILE is None
                traincmd = ["python3",
                            "./train.py", 
                            "--display_progress", 
                            "--max_iter", "5",
                            "-S", TRAIN_SCP, 
                            MODEL_DIR, 
                            LTF_DIR
                           ]
                tagcmd   = ["python3",
                            "./tagger.py", 
                            "-S", TEST_SCP, 
                            "-L", NEW_NE_DIR,
                            "-t", str(threshold),
                            MODEL_DIR
                           ]

        # Begin training     
        logger.info("Starting training on documents in %s at iteration %d" % (TRAIN_SCP, iteration) )
        subprocess.run(traincmd)

        # Begin tagging
        logger.info("Starting tagging of documents in %s at iteration %d" % (TEST_SCP, iteration) )
        subprocess.run(tagcmd)

        # Update values, directories, and files
        if iteration != 0:
            print(FEATS_FILE)
            changeinNEs = updateNEdirs(PREV_SYS_LAF_DIR, NEW_NE_DIR, SYS_LAF_DIR)
        else:
            SYS_LAF_DIR = NEW_NE_DIR
        PREV_SYS_LAF_DIR = SYS_LAF_DIR
        FEATS_FILE=os.path.join(working_dir, str(iteration), 'selected_feats.txt')
        print(FEATS_FILE)
        select_features(FEATS_FILE, MODEL_DIR, (1.0-threshold))
        threshold-=threshold_decrement
        iteration+=1
        TRAIN_SCP=os.path.join(working_dir, str(iteration), 'training.list.txt')
        MODEL_DIR=os.path.join(working_dir, str(iteration), 'model')
        NEW_NE_DIR=os.path.join(working_dir, str(iteration), 'newNEs')
        SYS_LAF_DIR=os.path.join(working_dir, str(iteration), 'output')

    print("Bootstrapping stopped after {} iterations".format(iteration))
    if not changeinNEs:
        print("No more NEs were found on the last iteration")
    elif threshold < threshold_min:
        print("Threshold dropped below the minimum")
    else:
        print("Why bootstrapping stopped is unknown")

    scorecmd = ["python3",
                "./score.py", 
                REF_LAF_DIR, 
                SYS_LAF_DIR, 
                LTF_DIR
               ]

    subprocess.run(scorecmd)



"""
Update TRAIN_SCP to contain LAF pathnames to be used in training in next iteration
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

    changeinNEs = False

    for fn in prev_laf_dir:
        if fn.endswith('laf.xml'):
            prev_laf = os.path.join(prev_laf_dir, fn)
            new_laf = os.path.join(new_ne_dir, fn)
            try:
                assert os.path.exists(new_laf)
            except AssertionError:
                logging.warn("{} processed last iteration but not this one".format(fn))
    for fn in new_ne_dir:
        if fn.endswith('laf.xml'):
            prev_laf = os.path.join(prev_laf_dir, fn)
            new_laf = os.path.join(new_ne_dir, fn)
            try:
                assert os.path.exists(prev_laf)
            except AssertionError:
                logging.warn("{} processed this iteration but not the last.  Skipping...".format(fn))
                continue
            
            prev_laf_doc = load_doc(prev_laf, LAFDocument, logger)
            new_ne_doc = load_doc(new_laf, LAFDocument, logger)
            doc_id = prev_laf_doc.doc_id

            prev_mentions = [[tag, extent, start_char, end_char] for [entity_id, tag, extent, start_char, end_char] in prev_laf_doc.mentions()]
            prev_spans = [(start_char, end_char) for [tag, extent, start_char, end_char] in prev_mentions]
            new_mentions = [[tag, extent, start_char, end_char] for [entity_id, tag, extent, start_char, end_char] in new_ne_doc.mentions()]
            mentions = []
            for m in prev_mentions:
                # if the NE was found in the previous iterations, it is retained here
                mentions.append(m)
            for m in new_mentions:
                # if the NE was found in the previous iterations, it is not overwritten, which means that 
                # the span's label will not be changed even if it is different this iteration
                if (m[2], m[3]) not in prev_spans:
                    mentions.append(m)
                    changeinNEs == True

            # Sort new mentions list by start_char then end_char
            mentions = sorted(mentions, key = lambda x: (int(x[2]), int(x[3])))

            n=1
            for tag, extent, start_char, end_char in mentions:
                entity_id = '{}-NE{}'.format(doc_id, n)
                mentions.append([entity_id, tag, extent, start_char, end_char])
                n+=1
                            
            laf = os.path.join(new_laf_dir, fn)
            laf_doc = LAFDocument(mentions=mentions, lang=ltf_doc.lang, doc_id=doc_id)
            laf_doc.write_to_file(laf)

    return changeinNEs
    




if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Bootstrapped training and tagger system for NE recognition",
                                        add_help=False,
                                        usage="%(prog)s [options] language working_dir")
    parser.add_argument('language', nargs='?', 
                        help="language of data")
    parser.add_argument('working_dir', nargs='?', 
                        help="subdirectory inside designated working directory")
    parser.add_argument('--threshold', nargs='?', default=0.4, type=float, 
                        help='threshold above which NEs are retained')
    parser.add_argument('--decrement', nargs='?', default=0.1, type=float, 
                        help='value by which threshold is decremented each iteration')
    parser.add_argument('--min_threshold', nargs='?', default=0.2, type=float, 
                        help='minimum value of threshold at which iterations continue')
    parser.add_argument('--max_iters', nargs='?', default=sys.maxsize, type=int, 
                        help='maximum number of iterations used in bootstrapping if stopping conditions are not met')
    args = parser.parse_args()

    if len(sys.argv) < 3:
        parser.print_help()
        sys.exit(1)

    bootstrappedNER(args.language, args.working_dir, args.threshold, args.decrement, args.min_threshold, args.max_iters)

