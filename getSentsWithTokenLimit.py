import sys
import os
import logging
import xml.etree.ElementTree as ET
from logger import configure_logger
from io_ import load_doc, Tree, LTFDocument, LAFDocument

def getSentsWithTokenLimit(ltf_path, laf_path, out_ltf_path, out_laf_path, logger, tokenLimit=10):

    # Process ltf and write new ltf retaining only SEG elements with TOKEN elements at or below the token limit.
    ltf = load_doc(ltf_path, LTFDocument, logger)
    text = ltf.tree.getroot().find('.//TEXT')

    chars2keep = []
    tokens2keep = []

    for seg in text.findall('SEG'):
        tokenCount = 0
        # First case for ltfs whose TOKENs include char info
        try:
            start_char = int(seg.get('start_char'))
            end_char = int(seg.get('end_char'))
            for tok in seg.findall('TOKEN'):
                tokenCount+=1
            if tokenCount <= tokenLimit:
                chars2keep += range(start_char, end_char+1)
            else:
                text.remove(seg)
        # Second case for ltfs whose TOKENs include only token ids
        except:
            tokens = []
            for tok in seg.findall('TOKEN'):
                tokenCount+=1
                tokens.append(tok.get('id'))
            if tokenCount <= tokenLimit:
                tokens2keep += tokens
            else:
                text.remove(seg)

    ltf.write_to_file(out_ltf_path)

    # Process laf and write new laf retaining only those mentions found in the sentences retained in the new ltf
    laf = load_doc(laf_path, LAFDocument, logger)
    doc = laf.tree.getroot().find('.//DOC')

    for ann in doc.findall('ANNOTATION'):
        # First case checks chars 
        if len(chars2keep) > 0:
            ext = ann.find('EXTENT')
            if ext == None:
                doc.remove(ann)
                continue
            start_char = int(ext.get('start_char'))
            end_char = int(ext.get('end_char'))
            assert start_char != -1 and end_char != -1
            if start_char in chars2keep and end_char in chars2keep:
                continue
            else:
                doc.remove(ann)
        # Second case checks token ids
        elif len(tokens2keep) > 0:
            start_token = ann.get('start_token')
            end_token = ann.get('end_token')
            assert start_token != None and end_token != None
            if start_token in tokens2keep and end_token in tokens2keep:
                continue
            else:
                doc.remove(ann)

    laf.write_to_file(out_laf_path)



def main(args):

    try:
        ltf_dir = args[0]
        laf_dir = args[1]
        assert os.path.exists(ltf_dir)
        assert os.path.exists(laf_dir)
        ltf_out_dir = args[2]
        laf_out_dir = args[3]
        tokenLimit = int(args[4])
    except:
        print("Usage: {} [input ltf dir] [input laf dir] [output ltf dir] [output laf dir] [integer token limit]".format(sys.argv[0]))
        sys.exit(1)

    if not os.path.exists(ltf_out_dir):
        os.makedirs(ltf_out_dir)
    if not os.path.exists(laf_out_dir):
        os.makedirs(laf_out_dir)

    logger = logging.getLogger();
    configure_logger(logger);

    for fn in os.listdir(ltf_dir):
        if fn.endswith('ltf.xml'):
            ltf = os.path.join(ltf_dir, fn)
            ltf_out = os.path.join(ltf_out_dir, fn)
            laf = os.path.join(laf_dir, fn.replace('ltf.xml', 'laf.xml'))
            laf_out = os.path.join(laf_out_dir, fn.replace('ltf.xml', 'laf.xml'))
            try:
                assert os.path.exists(laf)
            except AssertionError:
                logger.info("An entity annotated laf does not exist for {}.  Skipping...".format(fn))
                continue
            getSentsWithTokenLimit(ltf, laf, ltf_out, laf_out, logger, tokenLimit)



if __name__ == '__main__':
    main(sys.argv[1:])
