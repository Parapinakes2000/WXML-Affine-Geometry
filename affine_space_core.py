"""
Core functions for operations in affine space. 

Jaron Wang
"""

import numpy as np


"""Adds all of args assuming F_q"""
def add_affine(q, *args):
    return np.mod(np.sum(np.array(args), axis=0), q)


"""Generates a standard basis vector in n-dim"""
def generate_basis(n, index):
    arr = np.zeros(n, dtype = int)
    arr[index] = 1
    return arr

"""Takes an index and params q,n (F_q^n) and returns the corresponding vector. Inverse of vector_to_index()"""
def index_to_vector(n, q, index):
    vec = np.zeros(n, dtype=int)
    for i in range(n):
        vec[n - 1 - i] = index // (q ** (i)) % q
    return vec


'''Takes the vector and converts it to the unique index under F_{fieldsize}^{n}. Inverse of index_to_vector()'''
def vector_to_index(vector, q, n):
    assert(n == len(vector))
    index = 0
    for i in range(0, n):
        index += vector[n - 1 - i] * (q ** i)
    return int(index)