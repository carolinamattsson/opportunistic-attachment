#!/usr/bin/env python
# coding: utf-8

import os
import random
import numpy as np
import networkx as nx

from src.utils import directed_cycle_graph, disconnected_sticks, out_star

class Endogenous():

    name = "base"
    model = "Endogenous features growth model"
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
        # Return the node ID
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
    
class Exogenous():

    name = "base_pref"
    model = "Exogenous features growth model"
    specs = {}

    def __init__(self):
        self.G = nx.DiGraph()
        self.nodes = set()            
        self.networks = []
        return None

    def appraise(self):
        V = nx.degree_centrality(self.G)
        return V

    def select(self,V):
        max_score = max(V.values())
        # Adjust the scores by the factor provided
        if self.specs['gamma'] is None:
            alters = random.choices(list(V.keys()), k=2)
        else:
            for node in V:
                    V[node] = (V[node]/max_score) ** self.specs['gamma']
            # Turn the scores into probabilities
            total = sum(V.values())
            probabilities = [v / total for v in V.values()]
            # Sample a node from V with the given weights
            alters = np.random.choice(list(V.keys()), size=2, replace=False, p=probabilities)
        return alters
    
    def join(self,alters):
        # Add the new node to the graph
        node = self.G.number_of_nodes()
        self.G.add_node(node)
        # Add the edges to the alter
        self.G.add_edge(node, alters[0])
        self.G.add_edge(alters[1], node)
        # Update the set of existing nodes
        self.nodes.add(node)
        # Return the new node
        return node
    
    def add_node(self):
        # Appraise the existing nodes
        V = self.appraise()
        # Select nodes to connect with
        alters = self.select(V)
        node = self.join(alters)
        # Return the node ID
        return node
    
    def grow(self,N):
        # Grow the network until it reaches size N
        node = None 
        for n in range(N-len(self.nodes)):
            # Grow the network
            node = self.add_node()
            # Score and store the snapshot
            H = self.G.subgraph(self.nodes).copy()
            nx.set_node_attributes(H, nx.degree_centrality(H), 'score')
            self.networks.append(H)
        return None

    def __init__(self,m=2,select="random",gamma=1):
        # Specify the specifications
        self.specs["init"] = "cycle graph (m)"
        self.specs["score"] = "degree"
        self.specs["select"] = "exponential factor (gamma)" if select == "preferential" else select
        # Record the parameters
        self.specs["m"] = m
        self.specs["gamma"] = gamma if select == "preferential" else None
        # Create the initial network
        self.G = directed_cycle_graph(self.specs["m"])
        self.nodes = set(self.G.nodes())
        # Score and store the initial snapshots
        nx.set_node_attributes(self.G, nx.degree_centrality(self.G), 'score')
        self.networks = [self.G.copy()] * self.G.number_of_nodes()
        return None