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

def convert_indices(token_ids, entity_token_onsets, entity_token_offsets):
    onsets = []
    offsets = []
    ind = 0
    
    for token_ind,token_id in enumerate(token_ids):
        if len(onsets) == len(offsets):
            ## Look for start of entity
            if entity_token_onsets[ind] == token_id:
                onsets.append(token_ind)
        
        ## don't do an else -- even if we just created the start we could see an end on the 
        ## same token. Need to check length again.
        if len(onsets) != len(offsets):
            ## we've started an entity but haven't finished it: look for the end.
            if entity_token_offsets[ind] == token_id:
                offsets.append(token_ind)
                ind += 1    
        
        if ind >= len(entity_token_onsets):
            break
            
    return onsets, offsets

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
    F_vals = set()
    J_vals = set()

    for ltf in ltfs:
        # Check that the LTF is valid.
        ltf_doc = load_doc(ltf, LTFDocument, logger);
        if ltf_doc is None:
            print("Document %s is None!" % ltf)
            continue;
        
        # Extract features/targets.
        try:
            # Extract tokens.
            try:
                tokens, token_ids, token_onsets, token_offsets, token_nums, token_As, token_Bs, token_Gs, token_Fs, token_Js = ltf_doc.tokenizedWithABG();
            except Exception as e:
                print("Exception (%s) thrown trying to extract ABG -- resorting to normal tokenization" % e)
                tokens, token_ids, token_onsets, token_offsets, token_nums = ltf_doc.tokenized();
                token_As = token_Bs = token_Gs = None;
            if token_As != None:
                A_vals.update(token_As)
            if token_Bs != None:
                B_vals.update(token_Bs)
            if token_Gs != None:
                G_vals.update(token_Gs)
            if token_Fs != None:
                F_vals.update(token_Fs)
            if token_Js != None:
                J_vals.update(token_Js)

        except Exception as e:
            logger.warn('ABG values not found for %s. Skipping with exception %s' % (ltf, e) );
            continue;

    return A_vals, B_vals, G_vals, F_vals, J_vals
