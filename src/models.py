#!/usr/bin/env python
# coding: utf-8

import os
import random
import numpy as np
import networkx as nx
import itertools

from src.base import Endogenous
from src.utils import softmax, directed_cycle_graph, disconnected_sticks, out_star

class InOneOutOne(Endogenous):

    name = "i1o1"
    specs = {"update":"in-one-out-one"}

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
    
    def score(self,G):
        # Calculate the PageRank scores
        scores = nx.pagerank(G,alpha=self.specs["alpha"],max_iter=1000)
        return scores

    def explore_random(self):
        # Set of positions in the adjacent possible
        V = set(self.G.nodes()) - set(self.nodes)
        return V

    def select_random(self,V):
        # Select a random position from the adjacent possible
        node = random.choices(list(V),k=1)[0]
        return node

    def explore_opportunistic(self):
        V = {}
        possibilities = self.G.nodes() - self.nodes
        for pos in possibilities: # TODO: experiment
            H = self.G.subgraph(self.nodes | {pos})
            V[pos] = self.score(H)[pos]
        return V

    def select_opportunistic(self,V):
        max_score = max(V.values())
        # Adjust the scores by the factor provided
        if self.specs['gamma'] != 1:
            for node in V:
                V[node] = (V[node]/max_score) ** self.specs['gamma']
        # Turn the scores into probabilities
        total = sum(V.values())
        probabilities = [v / total for v in V.values()]
        # Sample a node from V with the probabilities
        node = random.choices(list(V.keys()), weights=probabilities, k=1)[0]
        return node
    
    def select_optimal(self,V):
        # Select randomly among the nodes with the maximum score
        max_score = max(V.values())
        max_nodes = [k for k, v in V.items() if v == max_score]
        node = random.choices(max_nodes,k=1)[0]
        return node

    def select_softmax(self,V):
        # Turn the scores into probabilities
        possibilities = list(V.keys())
        probabilities = softmax(list(V.values()),self.specs["gamma"])
        # Sample a node from V with the probabilities
        node = random.choices(possibilities, weights=probabilities, k=1)[0]
        return node

    def __init__(self,m=3,select="random",alpha=0.95,gamma=None):
        # Specify the specifications
        self.specs["init"] = "cycle graph (m)"
        self.specs["score"] = "pagerank (alpha)"
        self.specs["select"] = "exponential factor (gamma)" if select == "opportunistic" else select
        # Record the parameters
        self.specs["m"] = m
        self.specs["alpha"] = alpha
        self.specs["gamma"] = gamma if select == "opportunistic" else None
        # Define the functions for the model
        selector = {"random":self.select_random,
                    "opportunistic":self.select_opportunistic,
                    "optimal":self.select_optimal}
        explorer = {"random":self.explore_random,
                    "opportunistic":self.explore_opportunistic,
                    "optimal":self.explore_opportunistic}
        self.select = selector[select]
        self.explore = explorer[select]
        # Create the initial network
        self.G = directed_cycle_graph(self.specs["m"])
        self.nodes = set(self.G.nodes())
        # Score and store the initial snapshots
        nx.set_node_attributes(self.G, self.score(self.G), 'score')
        self.networks = [self.G.copy()] * self.G.number_of_nodes()
        return None
    
class InOneOutTwo(InOneOutOne):

    name = "i1o2"
    specs = {"update":"in-one-out-two"}

    def update(self,node=None):
        # If no node is specified, consider possibilities among all nodes
        if node is None:
            # If there are not already potential nodes in G
            if self.G.nodes() - self.nodes == set():
                # Populate the adjacent possible
                sources = set(self.nodes)
                for source in sources:
                    targets = set(self.nodes) - set([source])
                    for target1, target2 in itertools.combinations(targets, 2):
                        pos = self.G.number_of_nodes()
                        self.G.add_edge(source,pos)
                        self.G.add_edge(pos,target1)
                        self.G.add_edge(pos,target2)
        # Otherwise, only consider possibilities involving the specified node
        else:
            # Protest if the node is outside the network
            assert node in self.G
            assert node in self.nodes
            # Get the alters of the node
            alters = set(self.nodes) - set([node])
            for alter1, alter2 in itertools.combinations(alters, 2):
                # Add downstream positions
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(pos,alter1)
                self.G.add_edge(pos,alter2)
                # Add upstream positions
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(pos,node)
                self.G.add_edge(pos,alter2)
        return None

class InTwoOutOne(InOneOutOne):

    name = "i1o2"
    specs = {"update":"in-two-out-one"}

    def update(self,node=None):
        # If no node is specified, consider possibilities among all nodes
        if node is None:
            # If there are not already potential nodes in G
            if self.G.nodes() - self.nodes == set():
                # Populate the adjacent possible
                targets = set(self.nodes)
                for target in targets:
                    sources = set(self.nodes) - set([target])
                    for source1, source2 in itertools.combinations(sources, 2):
                        pos = self.G.number_of_nodes()
                        self.G.add_edge(source1,pos)
                        self.G.add_edge(source2,pos)
                        self.G.add_edge(pos,target)
        # Otherwise, only consider possibilities involving the specified node
        else:
            # Protest if the node is outside the network
            assert node in self.G
            assert node in self.nodes
            # Get the alters of the node
            alters = set(self.nodes) - set([node])
            for alter1, alter2 in itertools.combinations(alters, 2):
                # Add downstream positions
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(pos,alter2)
                # Add upstream positions
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(alter2,pos)
                self.G.add_edge(pos,node)
        return None
    
class InOutThree(InOneOutOne):

    name = "io3"
    specs = {"update":"in-out-three"}

    def update(self,node=None):
        # If no node is specified, consider possibilities among all nodes
        if node is None:
            # If there are not already potential nodes in G
            if self.G.nodes() - self.nodes == set():
                # Populate the adjacent possible
                targets = set(self.nodes)
                for target in targets:
                    sources = set(self.nodes) - set([target])
                    for source1, source2 in itertools.combinations(sources, 2):
                        # First InTwoOutOne
                        pos = self.G.number_of_nodes()
                        self.G.add_edge(source1,pos)
                        self.G.add_edge(source2,pos)
                        self.G.add_edge(pos,target)
                        # Then InOneOutTwo
                        pos = self.G.number_of_nodes()
                        self.G.add_edge(target,pos)
                        self.G.add_edge(pos,source1)
                        self.G.add_edge(pos,source2)
        # Otherwise, only consider possibilities involving the specified node
        else:
            # Protest if the node is outside the network
            assert node in self.G
            assert node in self.nodes
            # Get the alters of the node
            alters = set(self.nodes) - set([node])
            for alter1, alter2 in itertools.combinations(alters, 2):
                # Add downstream position
                # First InTwoOutOne
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(pos,alter2)
                # Then InOneOutTwo
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(pos,alter1)
                self.G.add_edge(pos,alter2)
                # Add upstream positions
                # First InTwoOutOne
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(alter2,pos)
                self.G.add_edge(pos,node)
                # Then InOneOutTwo
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(pos,node)
                self.G.add_edge(pos,alter2)
        return None

class InTwoOutTwo(InOneOutOne):

    name = "i2o2"
    specs = {"update":"in-two-out-two"}

    def update(self,node=None):
        # If no node is specified, consider possibilities among all nodes
        if node is None:
            # If there are not already potential nodes in G
            if self.G.nodes() - self.nodes == set():
                # Populate the adjacent possible
                targets = set(self.nodes)
                for target1, target2 in itertools.combinations(targets, 2):
                    sources = set(self.nodes) - set([target1,target2])
                    for source1, source2 in itertools.combinations(sources, 2):
                        pos = self.G.number_of_nodes()
                        self.G.add_edge(target1,pos)
                        self.G.add_edge(target2,pos)
                        self.G.add_edge(pos,source1)
                        self.G.add_edge(pos,source2)
        # Otherwise, only consider possibilities involving the specified node
        else:
            # Protest if the node is outside the network
            assert node in self.G
            assert node in self.nodes
            # Get the alters of the node
            alters = set(self.nodes) - set([node])
            for alter1, alter2, alter3 in itertools.combinations(alters, 3):
                # Add three downstream positions
                # with alter1
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(pos,alter2)
                self.G.add_edge(pos,alter3)
                # with alter2
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(alter2,pos)
                self.G.add_edge(pos,alter1)
                self.G.add_edge(pos,alter3)
                # with alter3
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(node,pos)
                self.G.add_edge(alter3,pos)
                self.G.add_edge(pos,alter1)
                self.G.add_edge(pos,alter2)
                # Add three upstream positions
                # with alter1
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter2,pos)
                self.G.add_edge(alter3,pos)
                self.G.add_edge(pos,alter1)
                self.G.add_edge(pos,node)
                # with alter2
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(alter3,pos)
                self.G.add_edge(pos,alter2)
                self.G.add_edge(pos,node)
                # with alter3
                pos = self.G.number_of_nodes()
                self.G.add_node(pos)
                self.G.add_edge(alter1,pos)
                self.G.add_edge(alter2,pos)
                self.G.add_edge(pos,alter3)
                self.G.add_edge(pos,node)
        return None