"""Word embedding class."""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
import os

from . import _embeddings

__all__ = ['Embedding']


class Embedding(object):
    """Class for interacting with word embeddings.

    Supports reading/writing of the following file formats:

    - word2vec (binary and text)

      Original format used by word2vec tool. First line is a header indicating
      the size of the vocabulary and number of dimensions of the embeddings as
      plain text:

      ``N_WORDS N_DIM``

      Each successive line consists of a word (in plaintext) and its embedding,
      separated by a space:

      ``WORD EMBEDDING``

      If the file is in binary word2vec format, the embedding is a sequence of
      `4*`N_DIM`` Otherwise, it is a sequence of ``N_DIM`` floats separated by
      spaces.

     - bare text

        One entry per line, each of the form:

        ``WORD EMBEDDING``


    Parameters
    ----------
    modelf : str, optional
        Path to model file containing the embeddings. If None, then embeddings
        are not loaded at class initialization, but may be loaded at a future
        point using the :meth:`load_word2vec` or :meth:`load_bare_text`
        methods.
        (Default: None)

    fmt : str, optional
        File format of ``modelf``. If ``fmt='word2vec'``, then ``modelf``
        will be treated as word2vec output. If ``fmt='bare_text'`` it
        will be treated as bare text.
        (Default: 'word2vec')

    encoding : str, optional
        Character encoding of words in ``modelf``.
        (Default: 'utf-8')

    binary : bool, optional
        If True, ``modelf`` is assumed to be stored in binary form. Only
        relevant for word2vec models.
        (Default: True)

    max_words : int, optional
        If not None, then read only the first ``max_words`` from ``modelf``.
        If None then read all words.
        (Default: None)

    Attributes
    ----------
    w2i : dict
        Dictionary mapping in vocabulary words to row indices for ``vectors``
        such that ``vectors[w2i[word]]`` is the embedding corresponding to
        ``word``.

    words_ : list of str
        Vocabulary expressed as list of words sorted in order of appearance in
        ``modelf``.

    vectors_ : ndarray, (n_words, n_dim)
        Embeddings.
    """
    def __init__(self, modelf=None, fmt='word2vec', encoding='utf-8',
                 binary=True, max_words=None):
        self.__dict__.update(locals())
        del self.self
        if modelf is not None:
            if fmt == 'word2vec':
                self.load_word2vec(modelf, encoding, binary, max_words)
            elif fmt == 'bare_text':
                self.load_bare_text(modelf, encoding, max_words)

    def load_word2vec(self, modelf, encoding='utf-8', binary=True,
                      max_words=None):
        """Load word embeddings in the same format used by the word2vec tool.

        Parameters
        ----------
        modelf : str
            Path to model file containing the embeddings.

        encoding : str, optional
            Character encoding of words in ``modelf``.
            (Default: 'utf-8')

        binary : bool, optional
            If True, model file is assumed to be stored in binary form.
            (Default: True)

        max_words : int, optional
            If not None, then read only the first ``max_words`` from
            ``modelf``. If None then read all words.
            (Default: None)
        """
        if not os.path.exists(modelf):
            raise IOError('No such file: %s' % modelf)
        max_words = 0 if max_words is None else max_words
        words, w2i, vectors = _embeddings.load_word2vec(modelf, encoding,
                                                        binary, max_words)
        self.words_ = words
        self.vocab_ = set(words)
        self.w2i_ = w2i
        self.vectors_ = vectors

    def write_word2vec(self, modelf, encoding='utf8', binary=True):
        """Write word embeddings in the format used by the word2vec tool.

        Parameters
        ----------
        modelf : str
            Output model file containing for embeddings.

        encoding : str, optional
            Character encoding of words in embeddings.
            (Default: 'utf-8')

        binary : bool, optional
            If True, store model file in binary format.
            (Default: True)
        """
        _embeddings.write_word2vec(modelf, self.words_, self.vectors_,
                                   encoding, binary)

    def load_bare_text(self, modelf, encoding='utf-8', max_words=None):
        """Load word embeddings from text file.

        Parameters
        ----------
        modelf : str
            Path to model file containing the embeddings.

        encoding : str, optional
            Character encoding of words in ``modelf``.
            (Default: 'utf-8')

        max_words : int, optional
            If not None, then read only the first ``max_words`` from
            ``modelf``. If None then read all words.
            (Default: None)
        """
        if not os.path.exists(modelf):
            raise IOError('No such file: %s' % modelf)
        max_words = 0 if max_words is None else max_words
        words, w2i, vectors = _embeddings.load_bare_text(modelf, encoding,
                                                         max_words)
        self.words_ = words
        self.vocab_ = set(words)
        self.w2i_ = w2i
        self.vectors_ = vectors

    def write_bare_text(self, modelf, encoding='utf8'):
        """Write word embeddings to text file.

        Parameters
        ----------
        modelf : str
            Output model file containing for embeddings.

        encoding : str, optional
            Character encoding of words in embeddings.
            (Default: 'utf-8')
        """
        _embeddings.write_bare_text(modelf, self.words_, self.vectors_,
                                    encoding)

    @property
    def n_dim(self):
        """Embedding dimensionality."""
        return self.vectors_.shape[1]

    @property
    def n_words(self):
        """Vocabulary size."""
        return self.vectors_.shape[0]

    @property
    def vocab(self):
        """Vocabulary expressed as a set."""
        return self.vocab_

    @property
    def words(self):
        """Vocabulary sorted in order of appearance in file embeddings were
        loaded from.
        """
        return self.words_

    def __getitem__(self, word):
        """Return a word's embedding as numpy array."""
        return self.vectors_[self.w2i_[word], ]

    def __contains__(self, word):
        return word in self.w2i_
