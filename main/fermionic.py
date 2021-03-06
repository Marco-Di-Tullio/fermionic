#fermionic.py

import time
import numpy as np
from scipy import sparse

#start_time = time.time()

def splitter(x):
    '''This function creates an numpy array where each
    element is a digit from the original number
    '''

    vectorized = []
    for i in str(x):
        vectorized.append(int(i))
    vectorized = np.array(vectorized)
    return vectorized


def integer_digits(n):
    '''integer_digits(n) creates a fermionic basis for dimension n
    '''

    rowb = []
    colb = []
    data = []

    for i in range(2**n):
        binary_base = format(i, 'b')
        bin_vector = splitter(binary_base)
        while len(bin_vector) < n:
            bin_vector = np.insert(bin_vector,0,0)
        for j in range(n):
            if bin_vector[j] == 1:
                rowb.append(i+1)
                colb.append(j)
                data.append(1)
    basis = sparse.csr_matrix((data, (rowb, colb)))
    return rowb, colb, basis

def operators(n):
    '''operators generates all the destruction and creation
    operators in dimension n stacked in a sparse matrix
    '''

    rowb, colb, basis = integer_digits(n)
    l = 2**n
    lb = len(rowb)
    row = []
    col = []
    data = []
    for i in range(lb):
        j = rowb[i]-2**(n-1-colb[i])
        sign = (-1)**(basis[rowb[i],0:colb[i]].sum())
        row.append(j-1)
        col.append(rowb[i]-1+colb[i]*l)
        data.append(sign)
    cm_tot = sparse.csr_matrix((data, (row, col)),shape=(l, n*l))
    cd_tot = sparse.csr_matrix.transpose(cm_tot)
    base = basis[1:(l+1),:] 
    return cm_tot, cd_tot, l, base

'''
----------------Operators----------------------

I can write this part in a different file.
When importing an external module, jupyter requests a
different addres than regular python interpreters

If you would like to use this in a separate file:
for running this script in jupyter, use main.fermionic
for runnin this script in regular python, use fermionic

from main.fermionic import *

'''


class Operator(object):
    def __init__(self, n):
        self.n = n
        self.cm_tot, self.cd_tot, self.l, self.base = operators(n)
        
    def cm(self, i):
        '''cm(i) cuts the big cm_tot sparse matrix to the
        corresponding mode i
        '''
        cm_tot = self.cm_tot
        l = self.l
        return cm_tot[:,l*i:l*(i+1)]

    def cd(self, i):
        '''cd(i) cuts the big cd_tot sparse matrix to the
        corresponding mode i
        '''
        cd_tot = self.cd_tot
        l = self.l
        return cd_tot[l*i:l*(i+1),:]
    
    def cdcm(self, i, j):
        cdi = self.cd(i)
        cmj = self.cm(j)
        return cdi.dot(cmj)
    
    def cmcd(self, i, j):
        cmi = self.cm(i)
        cdj = self.cd(j)
        return cmi.dot(cdj)
    
    def cmcm(self, i, j):
        cmi = self.cm(i)
        cmj = self.cm(j)
        return cmi.dot(cmj)
    
    def cdcd(self, i, j):
        cdi = self.cd(i)
        cdj = self.cd(j)
        return cdi.dot(cdj)
    
    def basis(self):
        ''' this method is for displaying the base'''
        
        base = self.base
        return base.todense()
    
    def vacuum(self):
        ''' this method is for working with the vacuum state'''
        
        vacio = [0 for i in range(2**(self.n))]
        vacio[0] = 1
        return np.array(vacio)

'''
----------------Class state----------------------
I can write this part in a different file.
When importing an external module, jupyter requests a
different addres than regular python interpreters

If you would like to use this in a separate file:
for running this script in jupyter, use main.fermionic
for runnin this script in regular python, use fermionic

from main.operators import *
'''



class State(object):
    '''state must be a numpy array 
    and operator an instance of the class Operator'''
    
    
    def __init__(self, state, operator):
        self.state = state 
        assert self.state.dot(self.state) == 1, "state is not normalized to 1"
        n = int(np.log2(len(self.state)))
        self.dimension = n
        self.operator = operator
        
        
    def rhosp(self):
        '''rhosp is the one body density matrix
        '''

        n = self.dimension
        state = self.state
        rhosp = np.zeros((n,n))
        for i in range(n):
            for j in range(n):
                rhosp[i,j] = state.dot((self.operator.cdcm(j,i)).dot(state))
        return rhosp

    def eigensp(self):
        '''eigen are the eigenvalues of the one body density matrix
        '''
        eigens = np.linalg.eigvalsh(self.rhosp())
        return eigens

    def ssp(self):
        '''ssp is the one body entropy
        '''
        
        eigens = self.eigensp()
        lene = len(eigens)
        s = 0
        for i in range(lene):
           if eigens[i] != 0 and eigens[i] != 1:
               s = s -(eigens[i]*np.log(eigens[i]) + (1-eigens[i])*np.log(1-eigens[i]))
        return s
