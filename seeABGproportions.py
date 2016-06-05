#!/usr/local/bin/python

import sys
import csv


NEtypes = ['NonNE','LOC','NAM','NOM','ORG','PER','PRO','TTL']
dictkeys = ['count']+NEtypes
outfields_1 = ['A','B','G']+dictkeys
outfields_2 = ['capitalized','allUpper','allDigits','allNonLetters','containsPeriod']+dictkeys

def main(args):

    if len(args) != 2:
        print("Usage: {} [NE triples text file] [NE other attrs text file]".format(sys.argv[0]))
        exit(1)

    NEtripleProportions_fn = "NEtripleProportions.tsv"
    NEattrProportions_fn = "NEattrProportions.tsv"
    
    tripleCounts = {}
    with open(args[0],'r') as triplefile:
        for line in triplefile:
            entry = line.split()
            triple = (entry[1], entry[2], entry[3])
            if triple not in tripleCounts:
                tripleCounts[triple]={key:0 for key in dictkeys}
            tripleCounts[triple]['count']+=1
            tripleCounts[triple][entry[0]]+=1

    attrCounts = {}
    with open(args[1],'r') as attrfile:
        for line in attrfile:
            entry = line.split()
            attrs = (entry[1], entry[2], entry[3], entry[4], entry[5])
            if attrs not in attrCounts:
                attrCounts[attrs]={key:0 for key in dictkeys}
            attrCounts[attrs]['count']+=1
            attrCounts[attrs][entry[0]]+=1

    tripleProportions = []
    for triple in tripleCounts.keys():
        tripledict = {'count':tripleCounts[triple]['count']}
        tripledict['A'] = triple[0]
        tripledict['B'] = triple[1]
        tripledict['G'] = triple[2]
        for NEtype in NEtypes:
            tripledict[NEtype] = (float(tripleCounts[triple][NEtype])/float(tripleCounts[triple]['count']))
        tripleProportions.append(tripledict)

    attrProportions = []
    for attrs in attrCounts.keys():
        attrdict = {'count':attrCounts[attrs]['count']}
        attrdict['capitalized'] = attrs[0]
        attrdict['allUpper'] = attrs[1]
        attrdict['allDigits'] = attrs[2]
        attrdict['allNonLetters'] = attrs[3]
        attrdict['containsPeriod'] = attrs[4]
        for NEtype in NEtypes:
            attrdict[NEtype] = (float(attrCounts[attrs][NEtype])/float(attrCounts[attrs]['count']))
        attrProportions.append(attrdict)

    csv.register_dialect('tabdelim',delimiter='\t')
    with open(NEtripleProportions_fn,'w') as outfile:
        writer = csv.DictWriter(outfile, dialect='tabdelim', fieldnames=outfields_1)
        writer.writeheader()
        for tripledict in tripleProportions:
            writer.writerow(tripledict)
            
    with open(NEattrProportions_fn, 'w') as outfile:
        writer = csv.DictWriter(outfile, dialect='tabdelim', fieldnames=outfields_2)
        writer.writeheader()
        for attrdict in attrProportions:
            writer.writerow(attrdict)

    print("Output written to {} and {}".format(NEtripleProportions_fn, NEattrProportions_fn))


            
if __name__ == '__main__':
    main(sys.argv[1:])                
