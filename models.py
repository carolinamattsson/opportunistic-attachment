#!/usr/bin/env python
# coding: utf-8

import os
import random
import numpy as np
import networkx as nx

from .base import Endogenous
from .utils import random_pwl

class InOneOutOne(Endogenous):

    name = "i1o1"
    label = "Endogenous growth model (in-one-out-one)"
    # Defaults, can be overridden by kwargs in __init__
    m = 3

    def initialize(self):
        self.G = nx.cycle_graph(self.m)
        self.nodes = self.G.nodes()
        return self.G.copy()

    def update(self,node=None):
        # If no node is specified, consider possibilities among all nodes
        if node is None:
            # Protest if there are already potential nodes in G
            assert self.G.nodes() - self.nodes == set()
            # Populate the adjacent possible
            sources = self.nodes
            targets = self.nodes
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
            alters = self.nodes - set([node])
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
    label = "Random growth model (in-one-out-one)"

    def explore(self):
        V = self.G.nodes() - self.nodes
        return V

    def select(self,V):
        node = random.choice(list(V))
        return node

class InOneOutOne_Optimal(InOneOutOne):

    name = "i1o1_optimal"
    label = "Optimal attachment (in-one-out-one)"
    # Additional defaults, can be overridden by kwargs in __init__
    alpha = 0.95

    def score(self,G):
        scores = nx.pagerank(G,alpha=self.alpha)
        return scores

    def select(self,V):
        # Find the maximum score
        max_score = max(V.values())
        # Get all nodes with the maximum score
        max_nodes = [k for k, v in V.items() if v == max_score]
        # Select a random node with the maximum score
        node = random.choice(max_nodes)
        return node
    
class InOneOutOne_Strategic(InOneOutOne_Optimal):

    name = "i1o1_strategic"
    label = "Strategic attachment (in-one-out-one)"
    # Additional defaults, can be overridden by kwargs in __init__
    gamma = 1

    def select(self,V):
        # Adjust the scores by the factor provided
        if self.gamma != 1:
            for node in V:
                V[node] = V[node] ** self.gamma
        # Calculate the sum of all scores
        total = sum(V.values())
        # Turn the scores into probabilities
        probabilities = [v / total for v in V.values()]
        # Sample a key from V with the probabilities
        node = random.choices(list(V.keys()), weights=probabilities, k=1)[0]
        return node