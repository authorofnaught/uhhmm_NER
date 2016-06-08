
import os, sys, StringIO, re
from os.path import join
from lxml import etree

def parseTokenID(tokenID):
  regex = re.compile(r'token-([0-9]+)-([0-9]+)')
  match = re.match(regex, tokenID)
  return int(match.group(1)), int(match.group(2))


def makeRightBranchingBaseline(ltf, blaf):

  with open(ltf,'r') as xmlfile:
    ltf_tree = etree.parse(xmlfile)

  root = ltf_tree.getroot()
  sents = []
  for seg in root.iter('SEG'):
    sent = []
    for token in seg.iter('TOKEN'):
      token_id = token.get('id')
      start_char = token.get('start_char')
      end_char = token.get('end_char')
      sent.append({'id':token_id,'start_char':start_char,'end_char':end_char})
    sents.append(sent)

  base_xml = """<?xml version='1.0' encoding='UTF-8'?>
                <!DOCTYPE LCTL_ANNOTATIONS SYSTEM "laf.v1.2.dtd">
                <LCTL_ANNOTATIONS/>
             """;

  # Create and set attributes on root node.
  tree = etree.parse(StringIO.StringIO(base_xml));
  root = tree.getroot();

  # Create and set attributes on doc node.
  doc = etree.SubElement(root, 'DOC');
  for sent in sents:
    for token in range(len(sent)-1):
      annotation = etree.SubElement(doc, 'ANNOTATION');
      extent_elem = etree.SubElement(annotation, 'EXTENT');
      ## right branching part
      extent_elem.set('start_char', sent[token]['start_char']);
      extent_elem.set('end_char', sent[-1]['end_char']);
      ## add single token as proposed span
      if token != 0:
        annotation = etree.SubElement(doc, 'ANNOTATION');
        extent_elem = etree.SubElement(annotation, 'EXTENT');
        extent_elem.set('start_char', sent[token]['start_char']);
        extent_elem.set('end_char', sent[token]['end_char']);

  tree.write(blaf, encoding="utf-8", pretty_print=True, xml_declaration=True)


def makeLeftBranchingBaseline(ltf, blaf):

  with open(ltf,'r') as xmlfile:
    ltf_tree = etree.parse(xmlfile)

  root = ltf_tree.getroot()
  sents = []
  for seg in root.iter('SEG'):
    sent = []
    for token in seg.iter('TOKEN'):
      token_id = token.get('id')
      start_char = token.get('start_char')
      end_char = token.get('end_char')
      sent.append({'id':token_id,'start_char':start_char,'end_char':end_char})
    sents.append(sent)

  base_xml = """<?xml version='1.0' encoding='UTF-8'?>
                <!DOCTYPE LCTL_ANNOTATIONS SYSTEM "laf.v1.2.dtd">
                <LCTL_ANNOTATIONS/>
             """;

  # Create and set attributes on root node.
  tree = etree.parse(StringIO.StringIO(base_xml));
  root = tree.getroot();

  # Create and set attributes on doc node.
  doc = etree.SubElement(root, 'DOC');
  for sent in sents:
    for token in range(len(sent)-1):
      annotation = etree.SubElement(doc, 'ANNOTATION');
      extent_elem = etree.SubElement(annotation, 'EXTENT');
      ## left branching part
      extent_elem.set('start_char', sent[0]['start_char']);
      extent_elem.set('end_char', sent[token]['end_char']);
      ## add single token as proposed span
      if token != 0:
        annotation = etree.SubElement(doc, 'ANNOTATION');
        extent_elem = etree.SubElement(annotation, 'EXTENT');
        extent_elem.set('start_char', sent[token]['start_char']);
        extent_elem.set('end_char', sent[token]['end_char']);

  tree.write(blaf, encoding="utf-8", pretty_print=True, xml_declaration=True)


if __name__ == '__main__':

  ltf_dir = "/Users/authorofnaught/Projects/LORELEI/BOLT_Hausa/tools/ne-tagger/LTF-DIR/hausa"
  rbbl_dir = "/Users/authorofnaught/Projects/LORELEI/BOLT_Hausa/tools/ne-tagger/SYS-LAF/hausa-rightbranching"
  lbbl_dir = "/Users/authorofnaught/Projects/LORELEI/BOLT_Hausa/tools/ne-tagger/SYS-LAF/hausa-leftbranching"

  for fn in os.listdir(ltf_dir):
    if fn.endswith('ltf.xml'):
      ltf = join(ltf_dir, fn)
      rbbl = join(rbbl_dir, fn.replace('ltf.xml','laf.xml'))
      lbbl = join(lbbl_dir, fn.replace('ltf.xml','laf.xml'))
      makeRightBranchingBaseline(ltf, rbbl)
      makeLeftBranchingBaseline(ltf, lbbl)
