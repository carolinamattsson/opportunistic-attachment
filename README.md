# Network Growth Under Opportunistic Attachment

Toy model of a growing network under a notion of "opportunistic attachment", where nodes seek to join the network at an advantageous position. In this model, advantageous positions are those with higher PageRank. In this implementation, exhaustive search is used to define the PageRank for potential positions and incoming nodes are proportionately more likely to select positions with higher values.

The model is structured as a dynamic program that stores a data structure with connections among the existing nodes and also every possible next-added node. This data structure is maniputated using networkx subgraphs and grows substantially with each node added to the growing network.

The model has several modular components:
* `explore` - this module runs PageRank for all potential next-added nodes and returns the value for each potential position.
* `select` - this module simulates selection of a position, given values for each potential position.
* `join` - this module adds a node to the selected position.
* `update` - this module updates the adjacent possible given the selected position for a next-added node.

The three modules are strung together in `grow`, which simulates the addition of a node to the growing network. This function returns a copy of the network at this point in its development.

I'd suggest running the replication files in the following order:
1. `run.ipynb` - this file runs the minimal model, growing many networks.
2. `plots_viz.ipynb` - this file generates the network visualizations.
3. `plots_space.ipynb` - this file creates the figures for the opportunity space.
4. `plots_ranks.ipynb` - this file creates the figures for the dynamics of node rank.
5. `plots_optimal.ipynb` - this file creates the figure for the optimal selection.
6. `run_variations.ipynb` - this file runs the model with variations on the ego networks of incoming nodes.
7. `plots_appendix.ipynb` - this file creates the figures for the appendix.