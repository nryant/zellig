# cython: boundscheck=False, wraparound=False, initializedcheck=False

import numpy as np
cimport numpy as np
cimport cython
from libc.stdio cimport *

cdef extern from 'stdlib.h':
    double atof(char*)

cdef extern from 'string.h':
    char* strtok(char*, char*)


def load_word2vec(fn, encoding='utf-8', binary=True, unsigned int max_words=0):
    cdef:
        FILE *f
        unsigned int n_words, n_dim, ii, jj
        char word[500]
        unicode word2
        char ch
        char vec[10000]
        char* x 

    f = fopen(fn, 'rb')

    # Read header.
    fscanf(f, "%lld", &n_words)
    fscanf(f, "%lld", &n_dim)
    if max_words > 0:
        n_words = min(max_words, n_words)

    # Copy.
    X = np.zeros((n_words, n_dim), dtype='float32')
    cdef float[:, :] X_mv = X
    words = []
    word_2_index = {}
    for ii in xrange(n_words):
        # word2vec tool truncates strings if they exceed MAX_STR, which
        # can cause problems here, so ignore decoding errors.
        fscanf(f, "%s%c", &word, &ch)
        word2 = word.decode(encoding, 'ignore')
        words.append(word2)
        word_2_index[word2] = ii
        if binary:
            for jj in xrange(n_dim):
                fread(&X_mv[ii, jj], 4, 1, f)
        else:
            fgets(vec, 10000, f)
            x = strtok(vec, ' ')
            for jj in xrange(n_dim):
                X_mv[ii, jj] = atof(x)
                x = strtok(NULL, ' ')

    fclose(f)

    return words, word_2_index, X


def write_word2vec(fn, words, float [:, :] X,
                   encoding='utf-8', binary=True):
    cdef:
        FILE *f
        unsigned int n_words, n_dim, ii, jj
        bytes word
        char* word2

    f = fopen(fn, 'wb')

    # write header
    n_words = X.shape[0]
    n_dim = X.shape[1]
    fprintf(f, "%lld %lld\n", n_words, n_dim)

    # copy
    for ii in xrange(n_words):
        word = words[ii].encode(encoding)
        word2 = word
        fprintf(f, '%s ', word2)
        if binary:
            for jj in xrange(n_dim):
                fwrite(&X[ii, jj], 4, 1, f)
        else:
            for jj in xrange(n_dim):
                fprintf(f, '%lf ', X[ii, jj])
        fprintf(f, '\n')

    fclose(f)


def load_bare_text(fn, encoding='utf8', unsigned int max_words=0):
    cdef:
        FILE *f
        unsigned int n_words, n_dim, ii, jj
        char word[500]
        unicode word2
        char ch
        char vec[10000]
        char* x
        
    # Determine n_dim.
    with open(fn, 'rb') as g:
        line = g.readline()
        n_dim = len(line.split()) - 1

    # Determine max number of lines to scan.
    if max_words == 0:
        max_words = int(2e9)

    # Process file line by line, parsing into word, embedding pairs.
    words = []
    word_2_index = {}
    n_words = 0
    vectors = []

    f = fopen(fn, 'rb')
    while fscanf(f, "%s%c", &word, &ch) != -1:
        word2 = word.decode(encoding, 'ignore')
        words.append(word2)
        word_2_index[word2] = n_words
        fgets(vec, 10000, f)
        vectors.append(vec)
        n_words += 1
        if n_words >= max_words:
            break
    fclose(f)

    # Efficiently parse the individual embedding strings and store in X.
    X = np.empty([n_words, n_dim], dtype='float32')
    cdef float [:, :] X_mv = X
    for ii in xrange(n_words):
        x = strtok(vectors[ii], ' ')
        for jj in xrange(n_dim):
            X_mv[ii, jj] = atof(x)
            x = strtok(NULL, ' ')

    return words, word_2_index, X


def write_bare_text(fn, words, float [:, :] X, encoding='utf8'):
    cdef:
        FILE *f
        unsigned int n_words, n_dim, ii, jj
        bytes word
        char* word2

    n_words = X.shape[0]
    n_dim = X.shape[1]

    f = fopen(fn, 'wb')
    for ii in xrange(n_words):
        word = words[ii].encode(encoding)
        word2 = word
        fprintf(f, '%s ', word2)
        for jj in xrange(n_dim):
            fprintf(f, '%lf ', X[ii, jj])
        fprintf(f, '\n')
    fclose(f)
