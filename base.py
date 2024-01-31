#!/usr/bin/env python
# coding: utf-8

import os
import random
import numpy as np
import networkx as nx

class Endogenous():

    name = "base"
    model = "Endogenous growth model"
    specs = {}

    def __init__(self):
        self.G = nx.DiGraph()
        self.nodes = set()            
        self.networks = []
        return None
    
    def update(self,node=None): 
        raise NotImplementedError

    def score(self,G): 
        raise NotImplementedError

    def explore(self):
        raise NotImplementedError

    def select(self,V):
        raise NotImplementedError
    
    def join(self,pos):
        # Add the new node to the graph
        node = self.G.number_of_nodes()
        self.G.add_node(node)
        # Get all the edges of the given position
        for source, target in set(self.G.in_edges(pos)):
            # Add an edge from the source node to the new node
            self.G.add_edge(source, node)
        for source, target in set(self.G.out_edges(pos)):
            # Add an edge from the new node to the target node
            self.G.add_edge(node, target)
        # Update the set of existing nodes
        self.nodes.add(node)
        # Return the new node
        return node
    
    def add_node(self):
        # Explore the adjacent possible
        V = self.explore()
        # Select a position to join the network
        pos = self.select(V)
        node = self.join(pos)
        # Return the network snapshot
        return node
    
    def grow(self,N):
        # Grow the network until it reaches size N
        node = None 
        for n in range(N-len(self.nodes)):
            # Update the adjacent possible
            self.update(node=node)
            # Grow the network
            node = self.add_node()
            # Score and store the snapshot
            H = self.G.subgraph(self.nodes).copy()
            nx.set_node_attributes(H, self.score(H), 'score')
            self.networks.append(H)
        return None