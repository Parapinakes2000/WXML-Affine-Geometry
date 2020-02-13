"""
Python module for finding maximum d-caps in F_q^n by maintaining the invariant that the starting cap is valid, and has a valid set of 
points which can be added to the set without breaking this invariant. Then for the set of plausible points, it adds the point, and
updates the plausible set accordingly. (For Sequential search, this is much faster than the validation)

Jaron Wang
"""
import numpy as np 
import os
import os.path as path
import pickle
import sys
import copy
from itertools import combinations, permutations
from multiprocessing import Array, Process
import time
from affine_space_core import *


""" Generates the necessary coefficients for the given d needed to eliminate all points of the d-flat."""
def generate_coeffs(d, q, n):
    l =[]
    for i in range(q):
        l += [i] * (d+1)

    good_coeffs = []
    for comb in permutations(l, d+1):
        if add_affine(q, *comb) == 1:
            good_coeffs.append(comb)
    print("Generating coefficients for d = {} , q = {}, n = {}".format(d,q,n))
    return set(good_coeffs)


if not __debug__:
    n = 3 if len(sys.argv) < 4 else int(sys.argv[3])
    q = 3 if len(sys.argv) < 4 else int(sys.argv[2])
    d = 2 if len(sys.argv) < 4 else int(sys.argv[1])
    debug_file = os.getcwd() + "\\results\\" + str(d)+ '_' + str(q) + "_" + str(n) + "_debug.txt"
    debug_log = open(debug_file, 'w+')


"""With the given cap, updates the corresponding validset. Uses multiprocessing with non-lock safe shared memory.
(operations are write only and overlap is irrelevant) Makes the assumption that the validset is correct not including 
the last addition to the cap, so only updates using the last point."""
def update_validset(cap, validset, d, q, n, coeff_list):
    sm_set = Array('i', validset, lock=False)
    processes = []
    #print("cap: {}".format(cap))
    for comb in combinations(cap[:-1], d):
        g = list(comb)
        g.append(cap[-1])
        p = Process(target=mark_visible, args=(sm_set, g, coeff_list, q, n ))
        processes.append(p)
        p.start() 
    
    for p in processes:
        p.join()
    #print ("Validset: {} | sm_set: {}".format(valid_set, sm_set[:]))
    #print("New Validset: {}".format([True if x == 1 else False for x in sm_set]))
    return [True if x == 1 else False for x in sm_set]


"""Updates validset with the assumption that it has not been updated for any sub-cap of the cap. """
def complete_update_validset(cap, validset, d, q, n, coeff_list):
    sm_set = Array('i', validset, lock=False)
    processes = []
    for i in range(1, d+1):
        for comb in combinations(cap, i + 1):
            p = Process(target=mark_visible, args=(sm_set, list(comb), coeff_list, q, n))
            processes.append(p)
            p.start()
    
    for p in processes:
        p.join()
        p.close()
    # Clones to allow for easier backtracking.
    return [True if x == 1 else False for x in sm_set]


"""Takes a set of points and marks every point which lies on the d-flat which is constructed by the (d+1) points
    and marks the corresponding index in shared_memory_set as False.
    
    points: list of d+1 points which make a d-flat.
    shared_memory_set: multiprocessing.Array(b, validset)
"""
def mark_visible(shared_memory_set, points, coeff_list, q=3, n=3): 
    for coeff in coeff_list:
        dotprod = [a * b for a,b in zip(coeff, points)]
        point = add_affine(q, *dotprod)
        index = vector_to_index(point, q, n)
        shared_memory_set[index] = 0


""" Finds the maximum cap using the given parameters. Specifically finding d-caps in F_q^n."""
def find_maximum_cap(n, q, d, coeff_list, current_cap=[], current_index=1, hashset=None, maximum_caps=[], cache=[], depth = []):
    if not __debug__:
        debug_log.write("current cap: {} \nCurrent validset: {}\n".format(current_cap, hashset))

    maximum_cap = current_cap
    for i in range(current_index, q ** n):
        if cache[i] is None:
            current_vec = index_to_vector(n, q, i)
            cache[i] = current_vec
        else:
            current_vec = cache[i]
        print("Currently Searching (depth, index):", end='')
        for dep in enumerate(depth):
            print(" {} |".format(dep), end='')
        print("", end='\r')    
        if hashset[i]:
            current_cap.append(current_vec)
            if len(current_cap) > d:
                vs_new = update_validset(current_cap, hashset, d, q, n, coeff_list=coeff_list)
            else:
                vs_new = complete_update_validset(current_cap, hashset, len(current_cap), q, n, coeff_list=coeff_list)
            maximal_cap, _ = find_maximum_cap(n, q, d, current_cap=current_cap.copy(), current_index=i + 1, hashset=vs_new, coeff_list=coeff_list, cache=cache, depth=depth + [i])
            current_cap.pop()
            if len(maximal_cap) > len(maximum_cap):
                maximum_caps = []
                maximum_cap = maximal_cap
            if len(maximal_cap) >= len(maximum_cap):
                maximum_caps.append(maximal_cap)
    if len(depth) == 0 and maximum_caps == []:
        maximum_caps.append(maximum_cap)
    return maximum_cap, maximum_caps

"""The main method. Given the params d,q,n, runs the search and saves all the caps found to a solution file under logs. """
def save_caps(d, q, n):
    print("--------------------------------Starting search for {}-cap in F_{}^{}----------------------------".format(d,q,n))
    valid_set = [True] * (q ** n)
    coeff_list = generate_coeffs(d, q, n)
    cache = [None] * (q ** n)
    previous_sol = os.getcwd() + "\\results\\" + str(d)+ '_' + str(q) + "_" + str(n - 1) + ".dat"
    current_sol = os.getcwd() + "\\results\\" + str(d)+ '_' + str(q) + "_" + str(n) + ".dat"
    complete_log = os.getcwd() + "\\results\\" + str(d)+ '_' + str(q) + "_" + str(n) + "_all.dat"
    if path.exists(complete_log):
        print("Solution previously found.")
        with open(complete_log, 'rb') as f:
            maximum_caps = pickle.load(f)
    else:
        if d == n:
            maximum_cap = [np.zeros(n, dtype=int)] + [generate_basis(n, i) for i in range(n)]
            maximum_caps = [maximum_cap]
            print("d = n, so any {} points is a cap.".format(d + 1))
        else:
            if path.exists(previous_sol):
                print("Continuing search using lower dimensional embedded cap")
                with open(previous_sol, 'rb') as f:
                    initial_cap = pickle.load(f)
                for i, vec in enumerate(initial_cap):
                    initial_cap[i] = np.concatenate((vec, np.zeros(1)), axis = None).astype(int)
            initial_cap = [np.zeros(n, dtype=int)]
            for i in range(n):
                initial_cap.append(generate_basis(n,i))
            print("Starting Search...")
            starter_hashset = complete_update_validset(initial_cap, valid_set, d, q, n, coeff_list)
            maximum_cap, maximum_caps = find_maximum_cap(n, q, d, current_cap=initial_cap, hashset= starter_hashset, coeff_list=coeff_list, cache=cache)
            print()

        with open(current_sol,'wb') as file:
            pickle.dump(maximum_cap, file)
        with open(complete_log, "wb") as file:
                pickle.dump(maximum_caps, file)
    print("{} caps of size {} were found.".format(len(maximum_caps), len(maximum_caps[0])))
    print("Example Cap: {}".format(maximum_caps[0]))
    return maximum_caps
    

if __name__ == '__main__':
    # Running with debug flag forces a re-run of the search, even if a cap has already been found. 
    if not __debug__:
        if d > n:
            d = n
        coeff_list = generate_coeffs(d, q, n)
        valid_set = [True] * (q ** n)
        cache = [None] * (q ** n)
        print("Generating debug results")
        start_time = time.time()
        initial_cap = [np.zeros(n, dtype=int)]
        for i in range(n):
            initial_cap.append(generate_basis(n,i))
        starter_hashset = complete_update_validset(initial_cap, valid_set,d,q,n, coeff_list)
        maximum_cap, maximum_caps = find_maximum_cap(n, q, d, current_cap=initial_cap, hashset= starter_hashset, coeff_list=coeff_list, cache=cache)
        debug_log.close()   
        print("This took {} seconds".format(time.time() - start_time))
        response = "A maximum cap for d = {}, F = {}^{}, has size {} and is: {}".format(d, q, n, len(maximum_cap), maximum_cap)
        print(response)
    else:
        if len(sys.argv) != 2:
            if len(sys.argv) == 4:
                n = int(sys.argv[3])
                q = int(sys.argv[2])
                d = int(sys.argv[1])
                if d > n:
                    d = n
            else:
                d = 1
                q = 3
                n = 2 
            maximum_cap = save_caps(d,q,n)
        else:
            n = int(sys.argv[1])
            q = 3
            if n <= 0:
                n = 0
                while(True):
                    n += 1
                    for d in range(n, 0, -1):
                        max_caps = save_caps(d,q,n)
                        print()
            else:
                for d in range(n, 0, -1):
                    max_caps = save_caps(d,q,n)
                    print()

            
    