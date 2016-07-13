#!/usr/bin/env python3

import argparse;
import pickle;
import glob;
import logging;
import os;
import shutil;
import subprocess;
import sys;
import tempfile;
import traceback
from joblib.parallel import Parallel, delayed

from features import OrthographicEncoder;
from io_ import load_doc, LTFDocument, LAFDocument, write_crfsuite_file;
from logger import configure_logger;
from util import convert_extents, convert_indices, sort_mentions, get_ABG_value_sets;

logger = logging.getLogger();
configure_logger(logger);


def write_train_data(lafs, ltf_dir, enc, trainf, featsfile, prob=1.0):
    """Extract features and target labels for each LTF/LAF pair and write to
    disk in CRFSuite data format.

    For details regarding this format, consult

    http://www.chokkan.org/software/crfsuite/manual.html

    Inputs
    ------
    lafs: list of str
        Paths to LAF files.

    ltf_dir : str
        Directory to search for LTF files.

    enc : features.Encoder
        Feature encoder.

    trainf : str
        CRFsuite training file.
    """
    with open(trainf, 'w') as f:
        logger.info("Writing training file %s" % (trainf) )
        A_vals = set()
        B_vals = set()
        G_vals = set()
        ltfs = []

        for laf in lafs:
            # Check that the LTF and LAF are valid.
            bn = os.path.basename(laf);
            ltf = os.path.join(ltf_dir, bn.replace('.laf.xml', '.ltf.xml'));
            ltfs.append(ltf)

        A_vals, B_vals, G_vals, F_vals, J_vals = get_ABG_value_sets(ltfs, logger)
        print("A_Vals=%s, B_vals=%s, G_vals=%s F_vals=%s J_vals=%s" % (A_vals, B_vals, G_vals, F_vals, J_vals) )


#            laf_doc = load_doc(laf, LAFDocument, logger);
#            ltf_doc = load_doc(ltf, LTFDocument, logger);
#            if laf_doc is None or ltf_doc is None:
#                continue;
            
            # Extract features/targets.
#            try:
                # Extract tokens.
#                try:
#                    tokens, token_ids, token_onsets, token_offsets, token_As, token_Bs, token_Gs = ltf_doc.tokenizedWithABG();
#                except:
#                    tokens, token_ids, token_onsets, token_offsets = ltf_doc.tokenized();
#                    token_As = token_Bs = token_Gs = None;
#                if token_As != None:
#                    A_vals.update(token_As)
#                if token_Bs != None:
#                    B_vals.update(token_Bs)
#                if token_Gs != None:
#                    G_vals.update(token_Gs)
#            except:
#                logger.warn('ABG values not found for %s. Skipping.' % laf);
#                continue;

        print("Found the following number of values for ABG:\nA: {}\nB: {}\nG: {}\nF: {}\nJ: {}\n".format(len(A_vals), len(B_vals), len(G_vals), len(F_vals), len(J_vals)))

        for laf in lafs:
            # Check that the LTF and LAF are valid.
            bn = os.path.basename(laf);
            ltf = os.path.join(ltf_dir, bn.replace('.laf.xml', '.ltf.xml'));
            laf_doc = load_doc(laf, LAFDocument, logger);
            ltf_doc = load_doc(ltf, LTFDocument, logger);
            #print("Writing features for ltf file %s with label file %s" % (ltf, laf))
            
            if laf_doc is None or ltf_doc is None:
                print("File not found")
                continue;
            
            # Extract features/targets.
            try:
                # Extract tokens.
                try:
                    tokens, token_ids, token_onsets, token_offsets, token_nums, token_As, token_Bs, token_Gs, token_Fs, token_Js = ltf_doc.tokenizedWithABG();
                except:
                    tokens, token_ids, token_onsets, token_offsets, token_nums = ltf_doc.tokenized();
                    token_As = token_Bs = token_Gs = token_Fs = token_Js = None;
                
                # Convert mentions to format expected by the encoder; that is,
                # (tag, token_onset, token_offset).
                mentions = laf_doc.mentions();
                if len(mentions) == 0:
                    mentions_ = [];
                else:
                    # Map to the minimal enclosing span of tokens in the
                    # supplied LTF.
                    entity_ids, tags, extents, char_onsets, char_offsets, entity_token_onsets, entity_token_offsets = zip(*mentions);
                    if token_onsets[0] != -1:
                        mention_onsets, mention_offsets = convert_extents(char_onsets, char_offsets,
                                                                      token_onsets, token_offsets)
                    else:
                        mention_onsets, mention_offsets = convert_indices(token_ids, entity_token_onsets, entity_token_offsets)
                        
                    mentions_ = list(zip(tags, mention_onsets, mention_offsets));
                    
                # Eliminate overlapping mentions, retaining whichever
                # is first when sorted in ascending order by (onset, offset).
                sort_mentions(mentions_);
                prev_mention_offset = -1;
                temp_mentions_ = [];
                for tag, mention_onset, mention_offset in mentions_:
                    if mention_onset > prev_mention_offset:
                        temp_mentions_.append([tag, mention_onset, mention_offset]);
                    prev_mention_offset = mention_offset;
                mentions_ = temp_mentions_;

                feats, targets = enc.get_feats_targets(tokens, mentions_, token_nums, 
                                                        token_As, token_Bs, token_Gs, token_Fs, token_Js, 
                                                        A_vals, B_vals, G_vals, F_vals, J_vals,
                                                        featsfile);

            except Exception as e:
                logger.warn('Feature extraction failed for %s with exception %s with info %s. Skipping.' % (laf, e, sys.exc_info()[0]) );
                traceback.print_exc(file=sys.stdout)
                continue;

            # Write to file.
            #if len(set(targets)) > 1 or targets[0] != 'O':
            write_crfsuite_file(f, feats, targets, prob);

            
##########################
# Ye olde' main
##########################
if __name__ == '__main__':
    # Parse command line arguments.
    parser = argparse.ArgumentParser(description='Train CRF-based named entity tagger using Passive Aggresive algorithm.',
                                     add_help=False,
                                     usage='%(prog)s [options] model_dir laf_dir lafs');
    parser.add_argument('model_dir', nargs='?',
                        help='Model output dir');
    parser.add_argument('ltf_dir', nargs='?',
                        help='.ltf.xml file dir');
    parser.add_argument('lafs', nargs='*',
                        help='.ltf.xml files to be processed');
    parser.add_argument('-S', nargs='?', default=None,
                        metavar='fn', dest='scpf',
                        help='Set script file (Default: None)');
    parser.add_argument('--n_left', nargs='?', default=2,
                        type=int, metavar='n',
                        help='Length of left context (Default: %(default)s)');
    parser.add_argument('--n_right', nargs='?', default=2,
                        type=int, metavar='n',
                        help='Length of right context (Default: %(default)s)');
    parser.add_argument('--max_prefix_len', nargs='?', default=4,
                        type=int, metavar='n',
                        help='Length of largest prefix (Default: %(default)s)');
    parser.add_argument('--max_suffix_len', nargs='?', default=4,
                        type=int, metavar='n',
                        help='Length of largest suffix (Default: %(default)s)');
    parser.add_argument('--update', nargs='?', default=1, choices=[0,1,2],
                        type=int, metavar='n',
                        help='Feature weight update strategy. 0=without slack variables, 1=type1, 2=type. (Default: %(default)s)');
    parser.add_argument('--disable_averaging', action='store_false',
                        dest="use_averaging", default=True,
                        help='Disable feature weight averaging.')
    parser.add_argument('--aggressiveness', nargs='?', default=1,
                        type=float, metavar='x',
                        help='Aggressiveness parameter. (Default: %(default)s)');
    parser.add_argument('--epsilon', nargs='?', default=1e-5,
                        type=float, metavar='x',
                        help='Used to test for convergence. (Default: %(default)s)');
    parser.add_argument('--max_iter', nargs='?', default=50,
                        type=int, metavar='n',
                        help='Maximum # of training iterations (Default: %(default)s)');
    parser.add_argument('--display_progress', action='store_true',
                        default=False,
                        help='Display training progress.')
    parser.add_argument('-F', nargs='?', default=None, dest='featsfile',
                        help='file with features to be retained, one per line, format=F[0-9]+') 
    parser.add_argument('-p', type=float, default=1.0, dest="prob", help="Probability of keeping a negative ('O') instance")
    
    args = parser.parse_args();

    if len(sys.argv) == 1:
        parser.print_help();
        sys.exit(1);

    # Determine ltfs/lafs to process.
    if not args.scpf is None:
        with open(args.scpf, 'r') as f:
            args.lafs = [l.strip() for l in f.readlines()];

    # Exit with error if model directory already exists.
#    if not os.path.exists(args.model_dir):
#        os.makedirs(args.model_dir);
#    else:
#        logger.error('Model directory %s already exists. Exiting.' % args.model_dir);
#        sys.exit(1);

    # Create working directory.
    temp_dir = tempfile.mkdtemp();

    # Initialize and save encoder.
    enc = OrthographicEncoder(args.n_left, args.n_right,
                              args.max_prefix_len, args.max_suffix_len);
    encf = os.path.join(args.model_dir, 'tagger.enc');
    with open(encf, 'wb') as f:
        pickle.dump(enc, f);

    # Train.
    trainf = os.path.join(temp_dir, 'train.txt')
    write_train_data(args.lafs, args.ltf_dir, enc, trainf, args.featsfile, args.prob);

    shutil.copyfile(trainf, os.path.join(args.model_dir, 'train.txt') ) #DEBUG

    def is_empty(fn):
        return os.stat(fn).st_size == 0;
    if not is_empty(trainf):
        modelf = os.path.join(args.model_dir, 'tagger.crf');

        """
        Select the algorithm to be used in training by uncommenting it.
        What parameters are used with each algorithm can be found in the CRFSuite documentation at 
        http://www.chokkan.org/software/crfsuite/manual.html

        Leave all '-p' parameters commented to use default values.

        """

#        # Train with passive aggressive algorithm
#        cmd = ['crfsuite', 'learn',
#               '-m', modelf,
#               '-a', 'pa', # Train with passive aggressive algorithm.
#               '-p', 'type=%d' % args.update,
#               '-p', 'c=%f' % args.aggressiveness,
#               '-p', 'error_sensitive=%d' % True,
#               '-p', 'averaging=%d' % args.use_averaging,
#               '-p', 'max_iterations=%d' % args.max_iter,
#               '-p', 'epsilon=%f' % args.epsilon,
#               '-p', 'feature.possible_transitions=0',
#               trainf];
        # Train with gradient descent using L-BFGS method
        cmd = ['crfsuite', 'learn',
              # '-g', '5',
              # '--log-to-file',
              # '--split=5',
              # '-x',
               '-m', modelf,
               '-a', 'lbfgs', # Train with gradient descent using L-BFGS method
               '-p', 'c1=1.0',
               '-p', 'c2=1.0',
               #'-p', 'max_iterations=%d' % args.max_iter,
               #'-p', 'num_memories=6',
               #'-p', 'epsilon=%f' % args.epsilon,
               #'-p', 'stop=10',
               #'-p', 'delta=1e-5',
               #'-p', 'linesearch=MoreThuente',
               #'-p', 'max_linesearch=20',
               trainf];
#        # Train with stochastic gradient descent with L2 regularization term
#        cmd = ['crfsuite', 'learn',
#               '-m', modelf,
#               '-a', 'l2sgd', # Train with stochastic gradient descent with L2 regularization term
#               '-p', 'c2=1',
#               #'-p', 'type=%d' % args.update,
#               #'-p', 'c=%f' % args.aggressiveness,
#               #'-p', 'error_sensitive=%d' % True,
#               #'-p', 'averaging=%d' % args.use_averaging,
#               '-p', 'max_iterations=%d' % args.max_iter,
#               #'-p', 'epsilon=%f' % args.epsilon,
#               #'-p', 'feature.possible_transitions=0',
#               trainf];
#        # Train with averaged perceptron
#        cmd = ['crfsuite', 'learn',
#               '-m', modelf,
#               '-a', 'ap', # Train with averaged perceptron 
#               '-p', 'max_iterations=%d' % args.max_iter,
#               '-p', 'epsilon=%f' % args.epsilon,
#               trainf];
#        # Train with adaptive regularization of weight vector
#        cmd = ['crfsuite', 'learn',
#               '-m', modelf,
#               '-a', 'arow', # Train with adaptive regularization of weight vector
#               '-p', 'max_iterations=%d' % args.max_iter,
#               '-p', 'epsilon=%f' % args.epsilon,
#               trainf];
        with open(os.devnull, 'w') as f:
            if args.display_progress:
                subprocess.call(cmd, stderr=f);
            else:
                subprocess.call(cmd, stderr=f, stdout=f);
    else:
        logger.error('Training file contains no features/targets. Exiting.');

    # Clean up.
    shutil.rmtree(temp_dir);
    
