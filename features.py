"""Feature extraction classes.
"""
from functools import wraps;
import re;
import random;

from chunk import BILOUChunkEncoder;
from io_ import LTFDocument, LAFDocument;

__all__ = ['OrthographicEncoder'];


class Encoder(object):
    """Abstract base class for feature encoders.

    Inputs
    ------
    n_left : int, optional
        Number of tokens of left context to include.
        (Default: 2)

    n_right : int, optional
        Number of tokens of right context to include.
        (Default: 2)

    Attributes
    ----------
    chunker : chunk.ChunkEncoder
        ChunkEncoder instance used to generate tags.
    """
    def __init__(self, n_left=2, n_right=2):
        self.chunker = BILOUChunkEncoder();
        self.n_left = n_left;
        self.n_right = n_right;

    def get_feats_for_token(self, token):
        """Return features for token.

        Inputs
        ------
        token : str
            Token.

        Outputs
        -------
        feats : tuple of str
            Features vector.
        """
        raise NotImplementedError;

    def get_feats(self, tokens, token_nums, token_As=None, token_Bs=None, token_Gs=None, token_Fs=None, token_Js=None, A_vals=None, B_vals=None, G_vals=None):
        """Return features corresponding to token sequence.

        Inputs
        ------
        tokens : list of str
            Token sequence.

        Outputs
        -------
        feats : lsit of tuples
            Feature vector sequence.
        """

#        feats = [self.get_feats_for_token(token) for token in tokens];
        feats = []

        for ii, token in enumerate(tokens):

######################################################################################################
###### Changes to inclusion of features in feature sets can be made here #############################

            token_feats = []

            """ Add prefix, suffix feats """
            token_feats.extend( self.get_feats_for_token(token) )

            """ Add word feats """
            token_feats.extend( word_type(token) )

            """ Add A-B-G triple as non-binary feature """
#            if token_As != None and token_Bs != None and token_Gs != None:
#                token_feats.append("{}-{}-{}".format(str(token_As[ii]), str(token_Bs[ii]), str(token_Gs[ii])))
            """ Add A-B double as non-binary feature """
#            if token_As != None and token_Bs != None:
#                token_feats.append("{}-{}".format(str(token_As[ii]), str(token_Bs[ii])))
            """ Add A as non-binary feature """
#            if token_As != None:
#                token_feats.append(token_As[ii])
            """ Add B as non-binary feature """
#            if token_Bs != None:
#                token_feats.append(token_Bs[ii])
            """ Add G as non-binary feature """
#            if token_Gs != None:
#                token_feats.append(token_Gs[ii])

            """ Add random A values as features (use in order to check for performance at chance) """
#            if A_vals != None:
#                pseudo = random.choice(list(A_vals))
#                for v in A_vals:
#                    token_feats.append(pseudo == v)

            """ Add random B values as features (use in order to check for performance at chance) """
#            if B_vals != None:
#                pseudo = random.choice(list(B_vals))
#                for v in B_vals:
#                    token_feats.append(pseudo == v)

            """ Add random G values as features (use in order to check for performance at chance) """
#            if G_vals != None:
#                pseudo = random.choice(list(G_vals))
#                for v in G_vals:
#                    token_feats.append(pseudo == v)

            """ Add random F values as features (use in order to check for performance at chance) """
#            pseudo = random.choice([-1, 0, 1])
#            for v in [-1, 0, 1]:
#                token_feats.append(pseudo == v)

            """ Add random J values as features (use in order to check for performance at chance) """
#            pseudo = random.choice([-1, 0, 1])
#            for v in [-1, 0, 1]:
#                token_feats.append(pseudo == v)

            """ Add A as binary feature (True or False for each possible value) """
            if token_As != None and A_vals != None:
                for v in A_vals:
                    token_feats.append(token_As[ii] == v)

            """ Add B as binary feature (True or False for each possible value) """
            if token_Bs != None and B_vals != None:
                for v in B_vals:
                    token_feats.append(token_Bs[ii] == v)

            """ Add G as binary feature (True or False for each possible value) """
            if token_Gs != None and G_vals != None:
                for v in G_vals:
                    token_feats.append(token_Gs[ii] == v)

            """ Add F as binary feature (True or False for each possible value) """
#             if token_Fs != None:
#                 for v in [-1, 0, 1]:
#                     token_feats.append(token_Fs[ii] == v)

            """ Add J as binary feature (True or False for each possible value) """
#             if token_Js != None:
#                 for v in [-1, 0, 1]:
#                     token_feats.append(token_Js[ii] == v)

            """ Add whether token is first token as feature (may be useful for case where f = j = -1) """
            token_feats.append(token_nums[ii] == 0)

            """ Add whether token is second token as feature (may be useful for case where f = j = -1) """
            token_feats.append(token_nums[ii] == 1)

            feats.append(token_feats)

        feats = zip(*feats);
        new_feats = [];
        for ii, feats_ in enumerate(feats):
            for pos in range(-self.n_left, self.n_right+1):
                feat_id = 'F%d[%d]' % (ii, pos);
                k = -pos;
                new_feats.append(['%s=%s' % (feat_id, val) if val is not None else val for val in roll(feats_, k)]);
        new_feats = list(zip(*new_feats))

        # Filter out None vals in rows where they occur.
        for ii, row in enumerate(new_feats):
            new_row = [v for v in row if not v is None];
            new_feats[ii] = new_row;
        return new_feats;

    def get_targets(self, tokens, mentions):
        """Return tag sequence to train against.

        Inputs
        ------
        tokens : list of str
            Token sequence.

        mentions : list of list
            List of mention tuples, each of the form (tag, start_token_index,
            enc_token_index).

        Outputs
        -------
        targets : list of str
            Target label sequence.
        """
        tags = ['O' for token in tokens];
        for tag, bi, ei in mentions:
            chunk = tokens[bi:ei+1];
            tags[bi:ei+1] = self.chunker.chunk_to_tags(chunk, tag);
        return tags;

    def get_feats_targets(self, tokens, mentions, token_nums, token_As=None, token_Bs=None, token_Gs=None, token_Fs=None, token_Js=None, A_vals=None, B_vals=None, G_vals=None):
        """Return features/tag sequence to train against.

        Inputs
        ------
        tokens : list of str
            Token sequence.

        mentions : list of list
            List of mention tuples, each of the form (tag, start_token_index,
            enc_token_index).

        Outputs
        -------
        feats : list of tuples
            Feature vector sequence.

        targets : list of str
            Target label sequence.
        """
        feats = self.get_feats(tokens, token_nums, token_As, token_Bs, token_Gs, token_Fs, token_Js, A_vals, B_vals, G_vals);
        targets = self.get_targets(tokens, mentions);
        return feats, targets;


class OrthographicEncoder(Encoder):
    """Encoder that assigns to each token a feature vector consisting of a
    basic set of lexical and orthographic features.

    Inputs
    ------
    n_left : int, optional
        Number of tokens of left context to include.
        (Default: 2)

    n_right : int, optional
        Number of tokens of right context to include.
        (Default: 2)

    max_prefix_len : int, optional
        Maximum length, in characters, of prefix features.
        (Default: 4)

    max_suffix_len : int, optional
        Maximum length, in characters, of suffic features.
        (Default: 4)

    Attributes
    ----------
    chunker : chunk.ChunkEncoder
        ChunkEncoder instance used to generate tags.

    prefix_lengths : list of int
        List of lengths of prefixes to be considered.

    suffix_lengths : list of int
        List of lengths of suffixes to be considered.
    """
    def __init__(self, n_left=2, n_right=2, max_prefix_len=4, max_suffix_len=4):
        super(OrthographicEncoder, self).__init__(n_left, n_right);
        self.prefix_lengths = range(1, max_prefix_len+1);
        self.suffix_lengths = range(1, max_suffix_len+1);

    @wraps(Encoder.get_feats_for_token)
    def get_feats_for_token(self, token):
        feats = [token];
        feats.append(token.lower()); # Lowercase feature

        # Prefix features n=1,...,4 .
        n_char = len(token);
        for prefix_len in self.prefix_lengths:
            if prefix_len <= n_char:
                feats.append(token[:prefix_len]);
            else:
                feats.append(None);

        # Suffix features n=1,...,4 .
        for suffix_len in self.suffix_lengths:
            if suffix_len <= n_char:
                feats.append(token[-suffix_len:]);
            else:
                feats.append(None);

#        feats.extend(word_type(token));

        return feats;


ALL_DIGITS_REO = re.compile(r'\d+$');
ALL_NONLETTERS_REO = re.compile(r'[^a-zA-Z]+$');

def word_type(word):
    """Determine word type of token.

    Inputs
    ------
    word : str
        A word token.

    Outputs
    -------
    begins_cap : bool
        Boolean indicating whether word begins with a capitalized letter.

    all_capitalized : bool
        Boolean indicating whether or not all letters of word are capitalized.

    all_digits : bool
        Boolean indicating whether word is composed entirely of digits.

    all_nonletters : bool
        Boolean indicating whether word is composed entirely of nonletters.

    contains_period : bool
        Boolean indicating whether word contains period.
    """
    begins_cap = word[0].isupper();
    all_capitalized = word.isupper();
    all_digits = word.isdigit();
    all_nonletters = ALL_NONLETTERS_REO.match(word) is not None;
    contains_period = '.' in word;

    return begins_cap, all_capitalized, all_digits, all_nonletters, contains_period;


def roll(feats, k=0):
    """Roll elements of list.

    Elements that rolle beyond the last position are NOT re-introduced at the
    first as with numpy.roll. Rather, they are replaced by None.

    Inputs
    ------
    feats : list of tuples                                                  
        Feature vector sequence.   

    k : int, optional
        Number of places by which elements are shifted.
        (Default: 0)
    """
    if k == 0:
        new_feats = list(feats);
    elif k>0:
        new_feats = [None]*k;
        new_feats.extend(feats[:-k]);
    else:
        new_feats = list(feats[-k:]);
        new_feats.extend([None]*-k);
    return new_feats;
