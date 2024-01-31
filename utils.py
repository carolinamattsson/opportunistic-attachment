#!/usr/bin/env python
# coding: utf-8


import sys
import random
import numpy as np
from scipy import stats
import networkx as nx
from collections import Counter
import infomap

def softmax(A, g=1.0):
    """
    Calculates the softmax of a distribution, modulated by a 
    precision term, g.
    
    Parameters
    ----------
    A (np.ndarray): a vector of real-valued numbers
    k (float): a factor that modulates how precise the output 
               softmaxed vector will end up being (g=1.0 is 
               standard, g=0.0 makes it uniform).

    Returns
    -------
    A (np.ndarray): a softmaxed version of the original vector

    """
    
    A = np.array(A) if not isinstance(A, np.ndarray) else A
    A = A*g
    maxA = A.max()
    A = A-maxA
    A = np.exp(A)
    A = A/np.sum(A)
    
    return A

def directed_cycle_graph(num_nodes):
    """
    Directed cycle graph with m nodes.
    """
    G = nx.DiGraph()
    for i in range(num_nodes):
        G.add_edge(i, (i+1)%num_nodes)  # The % operator makes the last node loop back to the first
    return G
 
def disconnected_sticks(num_nodes):
    """
    Two sticks.
    """
    G = nx.DiGraph()
    G.add_edge(0, 1)
    G.add_edge(1, 2)
    G.add_edge(3, 4)
    return G

def out_star(num_nodes):
    """
    Out star with m nodes.
    """
    G = nx.DiGraph()
    for i in range(1,num_nodes):
        G.add_edge(0, i)
    return G

def degree_vector_histogram(graph):
    """
    Return the degrees in both formats. max_deg is the 
    length of the histogram, to be padded with zeros.

    Parameters
    ----------
    graph (nx.Graph): the graph to get the degree histogram for.

    Returns
    -------
    vec (np.ndarray): vector of degree values.
    hist (np.ndarray): vector of histogram counts for in a range of
                       0 to the maximum degree.

    """
    
    vec = np.array(list(dict(graph.degree()).values()))
    max_deg = max(vec)
    counter = Counter(vec)
    hist = np.array([counter[v] for v in range(max_deg)])
    
    return vec, hist

def plot_degree(degree, number_of_bins=50, log_binning=False, base=2):
    """
    Plot the degree distribution with (log) binning.

    Parameters
    ----------
    degree (np.ndarray or list): degree sequence of a given graph
    number_of_bins (int): the length of the output vectors
    log_binning (bool): if True, this function will return log-binned
                        spacing between elements in the histogram
    base (float): the base of the logarithm, defaults to 2
    
    Returns
    -------
    x (np.ndarray): domain of the histogram
    y (np.ndarray): counts of the number of elements in bin_x
    
    """
    lower_bound = min(degree)
    upper_bound = max(degree)
    
    if log_binning:
        log = np.log2 if base == 2 else np.log10
        lower_bound = log(lower_bound) if lower_bound >= 1 else 0.0
        upper_bound = log(upper_bound)
        bins = np.logspace(lower_bound,upper_bound,number_of_bins, base=base)
    else:
        bins = np.linspace(lower_bound,upper_bound,number_of_bins)
    
    y, __ = np.histogram(degree, bins=bins, density=True)
    x = bins[1:] - np.diff(bins)/2.0
        
    return x, y


def infomap_communities(G):
    """
    Partition network with the Infomap algorithm.
    Annotates nodes with 'community' id and return number of communities found.
    """
    infomapWrapper = infomap.Infomap("--two-level --directed --silent")
    for e in G.edges():
        infomapWrapper.addLink(*e)
    infomapWrapper.run()
    return infomapWrapper.getModules()

def infomap_compression(G):
    """
    Partition network with the Infomap algorithm.
    Annotates nodes with 'community' id and return number of communities found.
    """
    infomapWrapper = infomap.Infomap("--directed --silent")
    for e in G.edges():
        infomapWrapper.addLink(*e)
    infomapWrapper.run()
    return infomapWrapper.getCodelength()/infomapWrapper.getOneLevelCodelength()


def midpoints(pos1,pos2,displace=True,new_length=1.5):
    """
    Find the midpoint between two position dictionaries from a graph layout function.
    If desired, displace any new nodes radially outward from its eventual position.

    Parameters
    ----------
    pos (dict): position dictionaries from a graph layout function
    
    Returns
    -------
    pos (dict): position dictionary
    
    """
    pos = {}
    new_nodes = pos2.keys() - pos1.keys()
    for node in pos1:
        pos[node] = np.mean(pos1[node],pos2[node]) if node in pos2 else pos1[node]
    for node in new_nodes:
        old_length = np.sqrt(np.sum(pos2[node]**2))
        pos[node] = pos2[node]*new_length/old_length
    return pos