#!/usr/bin/env python
# coding: utf-8

import os
import random
import numpy as np
import networkx as nx

class Endogenous():

    name = "base"
    label = "Endogenous growth model"

    def __init__(self,**kwargs):
        self.G = nx.DiGraph()
        self.nodes = set()            
        self.kwargs = kwargs
        return None
    
    def initialize(self):
        raise NotImplementedError
    
    def update(self,node=None): 
        raise NotImplementedError

    def score(self,G): 
        raise NotImplementedError

    def explore(self):
        V = {}
        possibilities = self.G.nodes() - self.nodes
        for node in possibilities:
            H = self.G.subgraph(self.nodes + [node])
            V[node] = self.score(H)[node]
        return V

    def select(self,V):
        raise NotImplementedError
    
    def join(self,node):
        # Add the new node to the graph
        node_copy = self.G.number_of_nodes()
        self.G.add_node(node_copy)
        # Get all the edges of the existing node
        for node_from, node_to in self.G.edges(node):
            # If the existing node is the source of the edge
            if node_from == node:
                # Add an edge from the new node to the target node
                self.G.add_edge(node_copy, node_to)
            else:
                # Add an edge from the source node to the new node
                self.G.add_edge(node_from, node_copy)
        # Return the new list of existing nodes
        return self.nodes + [node_copy]
    
    def grow(self):
        # Explore the adjacent possible
        V = self.explore()
        # Select a position to join the network
        node = self.select(V)
        node = self.join(node)
        # Return the network snapshot
        return self.G.subgraph(self.nodes).copy()
    
    def run(self,N):
        # Initialize the graph
        H = self.initialize()
        # Store the initial network snapshots
        networks = [H] * H.number_of_nodes()
        # Grow the network until it reaches size N
        node = None 
        for n in range(N-len(self.nodes)):
            # Update the adjacent possible
            self.update(node=node)
            # Grow the network
            H = self.grow()
            # Compute the realized scores
            scores = self.score(H)
            nx.set_node_attributes(H, scores, 'score')
            # Store the network snapshot
            networks.append(H)
        return self.networks