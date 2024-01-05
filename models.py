#!/usr/bin/env python
# coding: utf-8

import os
import random
import numpy as np
import networkx as nx

from base import Endogenous
from utils import random_pwl

class InOneOutOne(Endogenous):

    name = "i1o1"
    specs = {"update":"in-one-out-one",
             "initialize":None,
             "score":None,
             "select":None}

    def update(self,node=None):
        # If no node is specified, consider possibilities among all nodes
        if node is None:
            # If there are not already potential nodes in G
            if self.G.nodes() - self.nodes == set():
                # Populate the adjacent possible
                sources = set(self.nodes)
                targets = set(self.nodes)
                for source in sources:
                    for target in targets:
                        if source != target:
                            pos = self.G.number_of_nodes()
                            self.G.add_edge(source,pos)
                            self.G.add_edge(pos,target)
        # Otherwise, only consider possibilities involving the specified node
        else:
            # Protest if the node is outside the network
            assert node in self.G
            assert node in self.nodes
            # Get the alters of the node
            alters = set(self.nodes) - set([node])
            for alter in alters:
                # Add downstream positions
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(pos,alter)
                # Add upstream positions
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter,pos)
                self.G.add_edge(pos,node)
        return None
    
class InOneOutOne_Random(InOneOutOne):

    name = "i1o1_random"
    specs = {"update":"in-one-out-one",
             "init":"cycle graph (m)",
             "score":"equal",
             "select":"random"}

    def __init__(self,m=3):
        # Create the initial network
        self.specs["m"] = m
        self.G = nx.cycle_graph(m)
        self.nodes = set(self.G.nodes())
        # Score and store the initial snapshots
        nx.set_node_attributes(self.G, self.score(self.G), 'score')
        self.networks = [self.G.copy()] * self.G.number_of_nodes()
        return None

    def score(self,G):
        # Calculate the scores
        n = G.number_of_nodes()
        scores = {node:1/n for node in G.nodes()}
        return scores

    def explore(self):
        # Set of positions in the adjacent possible
        V = set(self.G.nodes()) - set(self.nodes)
        return V

    def select(self,V):
        # Select a random position from the adjacent possible
        node = random.choices(list(V),k=1)[0]
        return node

class InOneOutOne_Optimal(InOneOutOne):

    name = "i1o1_optimal"
    specs = {"update":"in-one-out-one",
             "initial":"cycle graph (m)",
             "score":"pagerank (alpha)",
             "select":"max"}

    def __init__(self,**kwargs):
        # Record the parameters
        self.specs["m"] = kwargs.get("m",3)
        self.specs["alpha"] = kwargs.get("alpha",0.95)
        self.specs["gamma"] = kwargs.get("gamma",1)
        # Create the initial network
        self.G = nx.cycle_graph(self.specs["m"])
        self.nodes = set(self.G.nodes())
        # Score and store the initial snapshots
        nx.set_node_attributes(self.G, self.score(self.G), 'score')
        self.networks = [self.G.copy()] * self.G.number_of_nodes()
        return None
    
    def score(self,G):
        # Calculate the PageRank scores
        scores = nx.pagerank(G,alpha=self.specs["alpha"])
        return scores

    def explore(self):
        V = {}
        possibilities = self.G.nodes() - self.nodes
        for pos in possibilities:
            H = self.G.subgraph(self.nodes | {pos})
            V[pos] = self.score(H)[pos]
        return V

    def select(self,V):
        # Select randomly among the nodes with the maximum score
        max_score = max(V.values())
        max_nodes = [k for k, v in V.items() if v == max_score]
        node = random.choices(max_nodes,k=1)[0]
        return node
    
class InOneOutOne_Strategic(InOneOutOne_Optimal):

    name = "i1o1_strategic"
    specs = {"update":"in-one-out-one",
             "initial":"cycle graph (m)",
             "score":"pagerank (alpha)",
             "select":"exponential factor (gamma)"}

    def select(self,V):
        # Adjust the scores by the factor provided
        if self.specs['gamma'] != 1:
            for node in V:
                V[node] = V[node] ** self.specs['gamma']
        # Turn the scores into probabilities
        total = sum(V.values())
        probabilities = [v / total for v in V.values()]
        # Sample a node from V with the probabilities
        node = random.choices(list(V.keys()), weights=probabilities, k=1)[0]
        return node