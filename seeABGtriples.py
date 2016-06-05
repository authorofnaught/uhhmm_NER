#!/usr/local/bin/python3

import sys
import os
import codecs
import re
from os.path import join
from lxml import etree as ET


ALL_NONLETTERS_REO = re.compile(r'[^a-zA-Z]+$')

def main(args):
    
    if len(args) != 2:
        print("Usage: {} [directory of LTFs with ABG features from uhhmm] [directory of LAFs with NE mentions]".format(sys.argv[0]))
        exit(1)

    ltf_dir = args[0]
    laf_dir = args[1]
    NEtriples = ""
    nonNEtriples = ""
    NEotherattrs = ""
    NEtokencount = 0
    tokencount = 0
    NEtriples_fn = "NEtriples.txt"
    NEotherattrs_fn = "NEotherattrs.txt"

    class _Token:
        def __init__(self, start_char, end_char, A, B, G, text, num, entityType=""):
            self.start_char = start_char
            self.end_char = end_char
            self.A = A
            self.B = B
            self.G = G
            self.text = text
            self.num = num
            self.entityType = entityType
            self.capitalized = self.text[0].isupper()
            self.allcaps = self.text.isupper()
            self.alldigits = self.text.isdigit()
            self.allnonletters = ALL_NONLETTERS_REO.match(self.text) is not None
            self.periodinword = '.' in self.text


    for fn in os.listdir(ltf_dir):
        if fn.endswith("ltf.xml"):

            tokens = []
            tokens_by_start_char = {}
            token_num = 0
            ltf_tree = ET.parse(join(ltf_dir, fn))
            ltf_root = ltf_tree.getroot()
            try:
                laf_tree = ET.parse(join(laf_dir, fn.replace("ltf.xml", "laf.xml")))
            except:
                print("WARNING: No corresponding LAF for {}".format(fn))
                continue
            laf_root = laf_tree.getroot()

            for token in ltf_root.iter('TOKEN'):
                new_token = (_Token(
                              token.get('start_char'),
                              token.get('end_char'),
                              token.get('a'),
                              token.get('b'),
                              token.get('g'),
                              token.text,
                              token_num
                            ))
                token_num+=1
                tokens.append(new_token)
                tokens_by_start_char[new_token.start_char] = new_token

            for annot in laf_root.iter('ANNOTATION'):
                try:

                    try:
                        tag = annot.xpath('TAG')[0].text;
                    except:
                        tag = annot.get('type');

                    extent = annot.xpath('EXTENT')[0];

                    start_char = extent.get('start_char');
                    end_char = extent.get('end_char');

                    current_token = tokens_by_start_char[start_char]
                    current_token.entityType = tag
                    while current_token.end_char != end_char:
                        current_token = tokens[current_token.num+1]
                        current_token.entityType = tag

                except:
                    continue

            for token in tokens:
                if token.G != None:
                    if token.entityType != "" and token.entityType != None:
                        NEtriples+="{} {} {} {}\n".format(token.entityType, token.A, token.B, token.G)
                        NEotherattrs+="{} {} {} {} {} {}\n".format(token.entityType, token.capitalized, token.allcaps, token.alldigits, token.allnonletters, token.periodinword)
                        NEtokencount+=1
                        tokencount+=1
                    elif token.entityType == "":
                        NEtriples+="{} {} {} {}\n".format("NonNE", token.A, token.B, token.G)
                        NEotherattrs+="{} {} {} {} {} {}\n".format("NonNE", token.capitalized, token.allcaps, token.alldigits, token.allnonletters, token.periodinword)
                        NEotherattrs
                        tokencount+=1

    with codecs.open(NEtriples_fn,"w",encoding="utf-8") as outfile:
        outfile.write(NEtriples)

    with codecs.open(NEotherattrs_fn,"w",encoding="utf-8") as outfile:
        outfile.write(NEotherattrs)

    print("{} total tokens".format(tokencount))
    print("{} NE tokens".format(NEtokencount))
    print("{} proportion of tokens which are NonNE".format((tokencount-NEtokencount)/tokencount))

    print("\nABG triples written to {} and other attrs written to {}".format(NEtriples_fn, NEotherattrs_fn))
    print("Now run the following in the command line:\npython3 seeABGproportions.py {} {}".format(NEtriples_fn, NEotherattrs_fn))



if __name__ == '__main__':
    main(sys.argv[1:])
