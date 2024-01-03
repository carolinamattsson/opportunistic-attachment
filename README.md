# Endogenous growth network model

Toy model of a growing network under a notion of "strategic attachment", where nodes seek to join the network at an advantageous position. In this model, advantageous positions are those with higher PageRank. In this implementation, exhaustive search is used to define the PageRank for potential positions and incoming nodes are proportionately more likely to select positions with higher values.

The model is structured as a dynamic program that stores a data structure with connections among the existing nodes and also every possible next-added node. This data structure is maniputated using networkx subgraphs and grows substantially with each node added to the growing network.

The model has three modular components:
* `explore` - this module runs PageRank for all potential next-added nodes and returns the value for each potential position.
* `select` - this module simulates selection of a position, given values for each potential position.
* `add` - this module updates the adjacent possible given the selected position for a next-added node.

The three modules are strung together in `grow`, which simulates the addition of a node to the growing network. This function returns a copy of the network at this point in its development.

Also relevant is `initialize`, which populates the data structure and returns a list with m copies of the initial graph.

Using `run_model(m,d,k,N)` initializes the model with m nodes in a ring, uses d as the damping factor in PageRank, uses k as the strength of the strategic attachment, and N as the final network size. This will return a list of the N network snapshots.