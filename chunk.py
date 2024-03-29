"""Chunk encoders.
"""
from functools import wraps;

__all__ = ['DummyChunkEncoder', 'BILOUChunkEncoder'];


class ChunkingFailedException(Exception): pass


class ChunkEncoder(object):
    """Abstract base class for chunk encoders.

    A ChunkEncoder mediates the translation between chunks, represented as
    sequences of labels, and sequences of chunk position-label pairs.
    """
    def chunk_to_tags(self, chunk, label, outside=False):
        """Tag tokens of chunk according to given scheme.

        Inputs
        ------
        chunk : list
            List of tokens correponding to THIS chunk.

        label : str
            Label attached to chunk.

        outside: bool, optional
            Indicates whether chunk should be represented as Outside.
        """
        raise NotImplementedError;

    def tags_to_chunks(self, tags):
        """Convert sequence of tags to sequence of chunks according to
        given scheme.

        Inputs
        ------
        tags : list
            List of tags.
        """
        raise NotImplementedError;


class DummyChunkEncoder(ChunkEncoder):
    """Implements dummy chunker in which each token = a chunk.
    """
    @wraps(ChunkEncoder.chunk_to_tags)
    def chunk_to_tags(self, chunk, label, outside=False):
        return [label for token in chunk];

    @wraps(ChunkEncoder.tags_to_chunks)
    def tags_to_chunks(self, tags):
        chunks = [];
        for ii, tag in enumerate(tags):
            chunks.append([ii, ii, tag]);
        return chunks;


class BILOUChunkEncoder(ChunkEncoder):
    """Implements representation of text chunks using the BILOU scheme.

    The BILOU scheme classifies each token as being the Beginning, Inside,
    or Last token of a multi-token chunk, a Unit chunk, or Outside.
    """
    @wraps(ChunkEncoder.chunk_to_tags)
    def chunk_to_tags(self, chunk, label, outside=False):
        n_tokens = len(chunk);
        tags = [];
        if outside:
            tags = ['O' for ii in xrange(n_tokens)];
        elif n_tokens == 1:
            tags.append('U');
        else:
            tags = ['B'];
            for ii in xrange(n_tokens-2):
                tags.append('I');
            tags.append('L');
        tags = ['%s_%s' % (tag, label) for tag in tags];
        return tags;

    @wraps(ChunkEncoder.tags_to_chunks)
    def tags_to_chunks(self, tags):
#        print(tags)
        positions = [self.get_position(tag) for tag in tags];
#        print('1')
        positions = self.fix_positions(positions);
#        print('2')
        labels = [self.get_label(tag) for tag in tags];
#        print('3')
        begin_pos = set(['B', 'U', 'O']);
#        print('4')
        end_pos = set(['L', 'U', 'O']);
#        print('5')
        begin_ind = [ii for ii, pos in enumerate(positions) if pos in begin_pos];
#        print('6')
        end_ind = [ii for ii, pos in enumerate(positions) if pos in end_pos];
#        print('7')
        if len(begin_ind) != len(end_ind):
            raise ChunkingFailedException;
#        print('8')
        chunks = [];
        for bi, ei in zip(begin_ind, end_ind):
            if ei < bi:
                raise ChunkingFailedException;
            chunks.append([bi, ei, labels[bi]]);
#        print("exiting tags_to_chunks")
        return chunks;

    def get_position(self, extended_tag):
        """Return position encoded in extended tag.

        Inputs
        ------
        extended_tag : str
           Extended tag for token in form {Position}_{Label}.
        """
        return extended_tag.split('_')[0];

    def get_label(self, extended_tag):
        """Return label encoded in extended tag.

        Inputs
        ------
        extended_tag : str
           Extended tag for token in form {Position}_{Label}.
        """
        if extended_tag == 'O':
            label = 'O';
        else:
            fields = extended_tag.split('_');
            label = '_'.join(fields[1:]);
        return label;

    def fix_positions(self, positions):
        """Fix some pathologies present in tag sequences output by CRFSuite.

        Namely, this fixes illegal sequences such as [O, I], [U, I], [I, U],
        [I, O], etc.

        Inputs
        ------
        positions : list
            List of positions.
        """
        outside_edges = set(['O', 'U', None]);
        n_tags = len(positions);
        new_positions = [];
        for ii, position in enumerate(positions):
            position = position;
            if position == 'I':
                prev_position = positions[ii-1] if ii > 0 else None;
                is_begin = prev_position in outside_edges;
                next_position = positions[ii+1] if ii < n_tags else None;
                is_end = next_position in outside_edges;
                if is_begin and is_end:
                    position = 'U';
                elif is_begin:
                    position = 'B';
                elif is_end:
                    position = 'L';
            new_positions.append(position);
        return new_positions;
