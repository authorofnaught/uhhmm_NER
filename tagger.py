#!/usr/bin/env python3.4
import argparse;
import pickle;
import logging;
import os;
import os.path
import shutil;
import subprocess;
import sys;
import tempfile;
import traceback

from joblib.parallel import Parallel, delayed;

from align import Aligner;
from chunk import BILOUChunkEncoder;
from features import OrthographicEncoder;
from io_ import load_doc, LTFDocument, LAFDocument, write_crfsuite_file;
from logger import configure_logger;
from util import get_ABG_value_sets

from math import log;

logger = logging.getLogger();
configure_logger(logger);


def tag_file(ltf, aligner, enc, chunker, modelf, tagged_dir, tagged_ext, threshold, A_vals, B_vals, G_vals):
    """Extract features for tokenization in LTF file and tag named entities.

    Inputs
    ------
    ltf : str
        LTF file.

    aligner : align.Aligner
        Aligner instance used to obtain character onsets/offsets of discovered
        mentions.

    enc : features.Encoder
        Encoder instance for feature extraction.

    chunker : chunk.ChunkEncoder
        ChunkEncoder instance for obtaining token onsets/offsets of discovered
        mentions from tag sequences.

    modelf : str
        CRFSuite model file.

    tagged_dir : str
        Directory to which to output LAF files.

    tagged_ext : str
        Extension to used for output LAF files.
    """

    # Create working directory.                                              
#    temp_dir = tempfile.mkdtemp();
    temp_dir = os.path.dirname(modelf)

    # Load LTF.
    ltf_doc = load_doc(ltf, LTFDocument, logger);
    if ltf_doc is None:
        shutil.rmtree(temp_dir);
        return;

    # Attempt tagging.
    try:
        # Extract tokens.
        try:
            tokens, token_ids, token_onsets, token_offsets, token_nums, token_As, token_Bs, token_Gs, token_Fs, token_Js = ltf_doc.tokenizedWithABG();
        except:
            tokens, token_ids, token_onsets, token_offsets, token_nums = ltf_doc.tokenized();
            token_As = token_Bs = token_Gs = token_Fs = token_Js = None
        txt = ltf_doc.text();
        spans = aligner.align(txt, tokens);

        # Extract features
        featsf = os.path.join(temp_dir, 'feats.txt');
#        feats = enc.get_feats(tokens, token_As, token_Bs, token_Gs);
        feats = enc.get_feats(tokens, token_nums, token_As, token_Bs, token_Gs, token_Fs, token_Js, A_vals, B_vals, G_vals);
        write_crfsuite_file(featsf, feats);

        shutil.copy(featsf, "featuresfile") #DEBUG

        # Tag.
        tagsf = os.path.join(temp_dir, 'tags.txt');
        cmd = ['crfsuite', 'tag',
               '--marginal',           # outputs probability of each tag as extra field in tagsfile
#               '--probability',        # outputs probability of tag sequence at top of tagsfile
               '-m', modelf,
               featsf];
        with open(tagsf, 'w') as f:
            subprocess.call(cmd, stdout=f);

        shutil.copy(tagsf, "taggingprobs") #DEBUG

        # Look for NEs in the tagfile with marginal probs.
        # If the tag is 'O', keep it.
        # If the tag is anything else, keep if marginal prob is above threshold.

        tagsf2 = os.path.join(temp_dir, 'tags2.txt');

        
        """
        Helper method for checking the tag sequence output in the section below. 
        Checks for full BI*L sequence, returning that seqeunce if mean logprob exceeds 
        threshold logprob - returns sequence of O's of equal length otherwise.
        If the seqeuence contains only one tag, that tag is returned as a U tag.
        
        """
        def _check_BIL_sequence(tags, probs, threshold):

            nextpart = ''

            if len(tags) < 1:

                logging.warn("Empty tag sequence submitted as BI*L sequence.")

            elif len(tags) == 1:

                logging.warn("Tag sequence of length 1 submitted as BI*L sequence.")

                if probs[0] >= threshold:   # compare probs, not abs vals of logprobs, hence >= and not <=

                    nextpart = 'U{}'.format(tags[0][1:])

                else: 

                    nextpart = 'O\n'

            else:

                try:

                    assert tags[0][0] == 'B' and tags[-1][0] == 'L'

                except AssertionError:

                    logging.warn('Incomplete BI*L sequence submitted.')
                    tags[0] = 'B{}'.format(tags[0][1:])
                    tags[-1] = 'L{}'.format(tags[-1][1:])

#                NElogProb = reduce(lambda x, y: (log(x) * -1) + (log(y) * -1), probs)/len(probs)
#                if NElogProb <= (log(threshold) * -1): # compare abs vals of logprobs, hence <= and not >=
                count = 0
                for prob in probs:
                    if prob >= threshold:
                        count+=1

                if count >= len(probs)/2.0:

                    nextpart = ''.join(tags)

                else:

                    nextpart = 'O\n'*len(NEtags)

            return nextpart


        """ Retain or reject NE hypotheses based on probs and write new tags file """
        with open(tagsf2, 'w') as f_out:
            with open(tagsf, 'r') as f_in:
                NEtags = None
                NEprobs = None
                for line in f_in.read().split('\n'):

                    try:

                        assert ':' in line

                        tag, prob = line.strip().split(':')


                        if tag[0] == 'O':
                        # if seq in play, check seq
                        # write tag

                            if NEtags:

                                f_out.write(_check_BIL_sequence(NEtags, NEprobs, threshold))
                                NEtags = None
                                NEprobs = None
                                
                            f_out.write(tag+'\n')


                        elif tag[0] == 'U':
                        # if seq in play, check seq
                        # if prob >= threshold, write tag
                        # else, write tag = O

                            if NEtags:

                                f_out.write(_check_BIL_sequence(NEtags, NEprobs, threshold))
                                NEtags = None
                                NEprobs = None
                            
                            if float(prob) >= threshold: # compare probs, not abs vals of logprobs, hence >= and not <=

                                f_out.write(tag+'\n')

                            else:

                                f_out.write('O\n')


                        elif tag[0] == 'B':
                        # if seq in play, check seq
                        # start new seq with tag

                            if NEtags:

                                f_out.write(_check_BIL_sequence(NEtags, NEprobs, threshold))

                            NEtags = [tag+'\n']
                            NEprobs = [float(prob)]


                        elif tag[0] == 'I':
                        # if seq in play, add tag to seq
                        # else, start new seq with tag = B

                            if NEtags:

                                NEtags.append(tag+'\n')
                                NEprobs.append(float(prob))

                            else:

                                logging.warn("Found an out of sequence I tag.")
                                tag = 'B{}'.format(tag[1:])
                                NEtags = [tag+'\n']
                                NEprobs = [float(prob)]


                        elif tag[0] == 'L':
                        # if seq in play, add tag to seq and check seq
                        # else, start new seq with tag = B

                            if NEtags:

                                NEtags.append(tag+'\n')
                                NEprobs.append(float(prob))
                                f_out.write(_check_BIL_sequence(NEtags, NEprobs, threshold))
                                NEtags = None
                                NEprobs = None

                            else:

                                logging.warn("Found an out of sequence L tag.")
                                tag = 'B{}'.format(tag[1:])
                                NEtags = [tag+'\n']
                                NEprobs = [float(prob)]
                                

                    except AssertionError:

                        pass
#                        logging.warn('No ":" in line {}'.format(line))  #DEBUG

                if NEtags: # Necessary if tagsf ends with an incomplete BI*L sequence

                    f_out.write(_check_BIL_sequence(NEtags, NEprobs, threshold))
                    NEtags = None
                    NEprobs = None


        tagsf = tagsf2  # Set the checked tag file as the new tag file
        # Continue 

        shutil.copy(tagsf, "tagsfile") #DEBUG

        # Load tagged output.
        with open(tagsf, 'r') as f:
            tags = [line.strip() for line in f];
            tags = tags[:len(tokens)];

        # Chunk tags.
        chunks = chunker.tags_to_chunks(tags);

        # Construct mentions.
        doc_id = ltf_doc.doc_id;
        mentions = [];
        n = 1;
        for token_bi, token_ei, tag in chunks:
            if tag == 'O':
                continue;

            # Assign entity id.
            entity_id = '%s-NE%d' % (doc_id, n);

            # Determine char onsets/offset for mention extent.
            start_char = token_onsets[token_bi];
            end_char = token_offsets[token_ei];
            
            if start_char == None or end_char == None:
                start_char = -1
                end_char = -1

            # Finally, determine text of extent and append.
            extent_bi = spans[token_bi][0];
            extent_ei = spans[token_ei][1];
            extent = txt[extent_bi:extent_ei+1];
            
            id_onset = token_ids[token_bi]
            id_offset = token_ids[token_ei]
            
            mentions.append([entity_id,           # entity id
                             tag,                 # NE type
                             extent,              # extent text
                             start_char,          # extent char onset
                             end_char,            # extent char offset
                             id_onset,
                             id_offset
                            ]);

            n += 1;

        # Write detected mentions to LAF file.
        bn = os.path.basename(ltf);
        laf = os.path.join(tagged_dir, bn.replace('.ltf.xml', tagged_ext));
        laf_doc = LAFDocument(mentions=mentions, lang=ltf_doc.lang, doc_id=doc_id);
        laf_doc.write_to_file(laf);
    except Exception as e:
        logger.warn('Problem with %s is %s. Skipping.' % (os.path.basename(ltf), e))
        traceback.print_exc(file=sys.stdout)


    # Clean up.
    #shutil.rmtree(temp_dir);


##########################
# Ye olde' main
##########################
if __name__ == '__main__':
    # parse command line args
    parser = argparse.ArgumentParser(description='Perform named entity tagging.',
                                     add_help=False,
                                     usage='%(prog)s [options] model ltfs');
    parser.add_argument('model_dir', nargs='?',
                        help='Model dir');
    parser.add_argument('ltfs', nargs='*',
                        help='LTF files to be processed');
    parser.add_argument('-S', nargs='?', default=None,
                        metavar='fn', dest='scpf',
                        help='Set script file (Default: None)');
    parser.add_argument('-L', nargs='?', default='./',
                        metavar='dir', dest='tagged_dir',
                        help="Set output mentions dir (Default: current)");
    parser.add_argument('-X', nargs='?', default='.laf.xml',
                        metavar='ext', dest='ext',
                        help="Set output mentions file extension (Default: .laf.xml)");
    parser.add_argument('-j', nargs='?', default=1, type=int,
                        metavar='n', dest='n_jobs',
                        help='Set num threads to use (default: 1)');
    parser.add_argument('-t', nargs='?', default=(2**-149), type=float,
                        metavar='t', dest='threshold',
                        help='Set threshold for NE probability (default: 2**-149)');
    parser.add_argument('-d', '--debug', action='store_true', default=False)
    
    args = parser.parse_args();

    if len(sys.argv) == 1:
        parser.print_help();
        sys.exit(1);
   
    # Determine ltfs to process.
    if not args.scpf is None:
        with open(args.scpf, 'r') as f:
            args.ltfs = [l.strip() for l in f.readlines()];

    # Initialize chunker, aligner, and encoder.
    chunker = BILOUChunkEncoder();
    aligner = Aligner();
    encf = os.path.join(args.model_dir, 'tagger.enc');
    with open(encf, 'rb') as f:
        enc = pickle.load(f);

    # Get values of A, B, and G now to pass to each call of tag_file.
    A_vals, B_vals, G_vals = get_ABG_value_sets(args.ltfs, logger)
    print("A_Vals=%s, B_vals=%s, G_vals=%s" % (A_vals, B_vals, G_vals) )

    # Perform tagging in parallel, dumping results to args.tagged_dir.
    n_jobs = min(len(args.ltfs), args.n_jobs);
    modelf = os.path.join(args.model_dir, 'tagger.crf');
    
    if args.debug:
        for ltf in args.ltfs:
            tag_file(ltf, aligner, enc, chunker,
                                         modelf,
                                         args.tagged_dir,
                                         args.ext, 
                                         args.threshold,
                                         A_vals, B_vals, G_vals)
    else:
        f = delayed(tag_file);
        Parallel(n_jobs=n_jobs, verbose=0)(f(ltf, aligner, enc, chunker,
                                         modelf,
                                         args.tagged_dir,
                                         args.ext, 
                                         args.threshold,
                                         A_vals, B_vals, G_vals) for ltf in args.ltfs);
