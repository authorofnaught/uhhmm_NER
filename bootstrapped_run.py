import os
import shutil
import tempfile
import sys
import subprocess
import logging
from logger import configure_logger
from io_ import load_doc, LAFDocument



def main(args):
    if len(args) != 4:
        print("Usage: "+sys.argv[0]+" [language] [working directory] [threshold value] [threshold change step value]")
        exit(1)

    lang=args[0]
    working_dir=os.path.join("/Users/tmill/Projects/LORELEI/NER/WORKING/", os.path.basename(args[1]))
    if not os.path.exists(working_dir):
        os.mkdir(working_dir)
    
    threshold = args[2]
    threshold_step = args[3]
    logger = logging.getLogger()
    configure_logger(logger)
    temp_dir = tempfile.mkdtemp()

    """These directories and files are not updated"""
    GAZ_LAF_DIR="/Users/tmill/Projects/LORELEI/NER/NI-LAF/"+lang+"/" # directory containing gold standard LAF files
    #REF_LAF_DIR="/Users/tmill/Projects/LORELEI/NER/REF-LAF/"+lang+"/" # directory containing gold standard LAF files
    LTF_DIR_ABG="/Users/tmill/Projects/LORELEI/NER/LTF-ABG/"+lang+"/" # directory containing LTF files with uhhmm features
    TEST_SCP="/Users/tmill/Projects/LORELEI/NER/TEST-SCP/"+lang+"/ALL.txt" # file with paths to LTF files for tagging, one per line


    """These directories and files are updated with each iteration"""
    iteration = 0
    MODEL_DIR=os.path.join(working_dir, str(iteration), 'model') # directory for trained model
    SYS_LAF_DIR=os.path.join(working_dir, str(iteration), 'sys_laf') # directory for tagger output (LAF files)
    TRAIN_SCP=os.path.join(temp_dir, 'trainingfiles') # file with paths to LAF files for training, one per line
    updateTrainingScript(GAZ_LAF_DIR, TRAIN_SCP) # initialize TRAIN_SCP to contain paths to all gazetteer-generated LAFs

        
    traincmd = ["./train.py", 
                "--display_progress", # Display crfsuite output of model iterations, if desired. 
#                "-t", "0.4",
#                "--max_iter", "5",
                "-S", TRAIN_SCP, 
                MODEL_DIR, 
                LTF_DIR_ABG
                ]
    tagcmd = ["./tagger.py", 
                "-S", TEST_SCP, 
                "-L", SYS_LAF_DIR, 
                MODEL_DIR
                ]
#     scorecmd = ["./score.py", 
#                 REF_LAF_DIR, 
#                 SYS_LAF_DIR, 
#                 LTF_DIR]

    changeinNEs = True

    while changeinNEs:
        if not os.path.exists(MODEL_DIR):
            os.makedirs(MODEL_DIR)
            
        if not os.path.exists(SYS_LAF_DIR):
            os.makedirs(SYS_LAF_DIR)
            
        logger.info("Starting training on documents in %s at iteration %d" % (TRAIN_SCP, iteration) )
        subprocess.call(traincmd)
        logger.info("Starting tagging of documents in %s at iteration %d" % (TEST_SCP, iteration) )
        subprocess.call(tagcmd)
        
        temp_laf_dir = os.path.join(temp_dir, 'temp_laf_dir')
        if not os.path.exists(temp_laf_dir):
            os.mkdir(temp_laf_dir)
            
        if iteration != 0:
            SYS_LAF_DIR, changeinNEs = updateNEdirs(PREV_SYS_LAF_DIR, temp_laf_dir, SYS_LAF_DIR)
        iteration+=1
        PREV_SYS_LAF_DIR = SYS_LAF_DIR 
        MODEL_DIR = os.path.join(working_dir, str(iteration), 'model')
        SYS_LAF_DIR = os.path.join(working_dir, str(iteration), 'sys_laf')
        updateTrainingScript(PREV_SYS_LAF_DIR, TRAIN_SCP)
        # TODO: update threshold for each iteration

    print("Bootstrapping stopped after {} iterations".format(iteration))
#    subprocess.call(scorecmd)
    shutil.rmtree(temp_dir)



"""
Update TRAIN_SCP to contain LAF pathnames to be used in training in next iteration
"""
def updateTrainingScript(laf_dir, scriptfile):
    with open(scriptfile, 'w') as outfile:
        for fn in os.listdir(laf_dir):
            if fn.endswith('laf.xml'):
                outfile.write("{}\n".format(os.path.join(laf_dir, fn)))



"""
Add new NE mentions to old NE mentions, if any, 
"""
def updateNEdirs(prev_laf_dir, temp_laf_dir, new_laf_dir):

    changeinNEs = False

    for fn in prev_laf_dir:
        if fn.endswith('laf.xml'):
            prev_laf = os.path.join(prev_laf_dir, fn)
            temp_laf = os.path.join(temp_laf_dir, fn)
            try:
                assert os.path.exists(temp_laf)
            except AssertionError:
                logging.warn("{} processed last iteration but not this one".format(fn))
    for fn in temp_laf_dir:
        if fn.endswith('laf.xml'):
            prev_laf = os.path.join(prev_laf_dir, fn)
            temp_laf = os.path.join(temp_laf_dir, fn)
            try:
                assert os.path.exists(prev_laf)
            except AssertionError:
                logging.warn("{} processed this iteration but not the last.  Skipping...".format(fn))
                continue
            
            prev_laf_doc = load_doc(prev_laf, LAFDocument, logger)
            temp_laf_doc = load_doc(temp_laf, LAFDocument, logger)
            doc_id = prev_laf_doc.doc_id

            prev_mentions = [[tag, extent, start_char, end_char] for [entity_id, tag, extent, start_char, end_char] in prev_laf_doc.mentions()]
            prev_spans = [(start_char, end_char) for [tag, extent, start_char, end_char] in prev_mentions]
            temp_mentions = [[tag, extent, start_char, end_char] for [entity_id, tag, extent, start_char, end_char] in temp_laf_doc.mentions()]
            mentions = []
            for m in prev_mentions:
                mentions.append(m)
            for m in temp_mentions:
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

    return new_laf_dir, changeinNEs
    




if __name__ == '__main__':
    main(sys.argv[1:])
