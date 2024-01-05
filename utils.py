#!/usr/bin/env python
# coding: utf-8


import sys
import random
import numpy as np
from scipy import stats

def random_pwl(N, beta=1.0, loc=0, scale=1):
    '''
    Generate a vector size N with pareto distributed values 
    pwl distrs: f(x,β) = β / x^(β+1) with possible scale & shift (for details see scipy.stats.pareto)
    '''
    unif = np.random.random(N)
    pareto = stats.pareto(beta,loc=loc,scale=scale)
    pwl = pareto.ppf(unif)
    # now return
    return pwl