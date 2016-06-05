"""Utility functions.
"""
__all__ = ['convert_extents', 'sort_mentions'];

from bisect import bisect, bisect_left;
from io_ import load_doc, LTFDocument

def convert_extents(char_onsets, char_offsets, token_onsets, token_offsets):
    """Convert from char onset/offset extends to token onset/offset extents.

    Maps to the minimal enclosing span of tokens in the supplied tokenization.
    All onsets/offsets assume zero-indexing.

    Inputs
    ------
    char_onsets : list
        Character onsets of mentions.
        
    char_offsets : list
        Character offsets of mentions

    token_onsets : list
        Character onsets of tokens in supplied tokenization.
    
    token_offsets : list
        Character offsets of tokens in supplied tokenization.
    """
    mention_token_onsets = [bisect(token_onsets, char_onset) - 1 for char_onset in char_onsets];
    mention_token_offsets = [bisect_left(token_offsets, char_offset) for char_offset in char_offsets];
    return mention_token_onsets, mention_token_offsets;


def sort_mentions(mentions):
    """Sort mentions in place in ascending order of token_onset, then
    token_offset.

    Inputs
    ------
    mentions : list of tuples
        List of mentions, each represented as a tuple of form (tag, token_onset, token_offset).
    """
    mentions.sort(key=lambda x: (x[1], x[2]));

def get_ABG_value_sets(ltfs, logger):
    """
    Scan through all LTF files in a directory and return the lists
    of values found for each of A, B, and G.
    Since uhhmm determines the number of values for each of this categories
    at runtime, it is not possible to know before retrieving the output of the system.
    
    """
    
    A_vals = set()
    B_vals = set()
    G_vals = set()

    for ltf in ltfs:
        # Check that the LTF is valid.
        ltf_doc = load_doc(ltf, LTFDocument, logger);
        if ltf_doc is None:
            continue;
        
        # Extract features/targets.
        try:
            # Extract tokens.
            try:
                tokens, token_ids, token_onsets, token_offsets, token_nums, token_As, token_Bs, token_Gs, token_Fs, token_Js = ltf_doc.tokenizedWithABG();
            except:
                tokens, token_ids, token_onsets, token_offsets, token_nums = ltf_doc.tokenized();
                token_As = token_Bs = token_Gs = None;
            if token_As != None:
                A_vals.update(token_As)
            if token_Bs != None:
                B_vals.update(token_Bs)
            if token_Gs != None:
                G_vals.update(token_Gs)
        except:
            logger.warn('ABG values not found for %s. Skipping.' % ltf);
            continue;

    return A_vals, B_vals, G_vals
