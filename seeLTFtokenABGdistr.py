#!/usr/local/bin/python3

import sys
import os
import codecs
import shutil
import tempfile
from collections import defaultdict, Counter
from os.path import join
from lxml import etree


def see_LTF_token_ABG_distr(args):

    if not 4 <= len(args) <= 5:
        print("Usage: {} [ltf directory] [A filename] [B filename] [G filename] [optional num most frequent tokens]".format(sys.argv[0]))
        exit(1)


#    def _numeric_sorted(thelist):
#        try:
#            returnlist=sorted([int[i] for i in thelist])
#        except:
#            returnlist=[]
#            otherlist=[]
#            for i in thelist:
#                try:
#                    returnlist.append(int(i))
#                except:
#                    otherlist.append(i)
#            returnlist=sorted([i for i in returnlist])
#            returnlist+=otherlist
#        return returnlist


    ltf_dir=args[0]
    Aoutfn=args[1]
    Boutfn=args[2]
    Goutfn=args[3]
    try:
        num_most_freq=int(args[4])
    except:
        num_most_freq=20
    

    temp_dir=tempfile.mkdtemp()
    Afn=join(temp_dir,'A')
    Bfn=join(temp_dir,'B')
    Gfn=join(temp_dir,'G')

    missing = set()
    with codecs.open(Afn,'w',encoding='utf-8') as A_tempfile: 
        with codecs.open(Bfn,'w',encoding='utf-8') as B_tempfile:
            with codecs.open(Gfn,'w',encoding='utf-8') as G_tempfile:

                for fn in os.listdir(ltf_dir):
                    if fn.endswith('ltf.xml'):
                        tree = etree.parse(join(ltf_dir, fn))
                        root = tree.getroot()
                        for token in root.iter('TOKEN'):
                            A_cat = token.get('a')
                            B_cat = token.get('b')
                            G_cat = token.get('g')
                            word = token.text.lower()
                            if A_cat == None or B_cat == None or G_cat == None:
                                missing = missing.union([fn])
                            A_tempfile.write("{} {}\n".format(A_cat, word))
                            B_tempfile.write("{} {}\n".format(B_cat, word))
                            G_tempfile.write("{} {}\n".format(G_cat, word))

    print("ABG values missing in the following files:\n\t{}".format('\n\t'.join(missing)))

    for out,temp in [ (Aoutfn,Afn), (Boutfn,Bfn), (Goutfn,Gfn) ]:
        with codecs.open(out,'w',encoding='utf-8') as outfile:
            with codecs.open(temp,'r',encoding='utf-8') as tokenfile:

                categories = defaultdict(Counter)
                for line in tokenfile:
                    categories[line.split()[0]][line.split()[1]]+=1
                for category in sorted(list(categories.keys())):
                    for key in categories[category]:
                        if isinstance(categories[category][key], str):
                            print(categories[category][key])
                    tuples=categories[category].most_common(num_most_freq)
                    tokens=[t[0] for t in tuples]
                    outfile.write("{} {}\n".format(category, ' '.join(tokens)))

    shutil.rmtree(temp_dir)



if __name__ == '__main__':
    see_LTF_token_ABG_distr(sys.argv[1:])
