
# Ising Model data format

The Ising Model is represented in JSON with three fields (all required): The `nodes` field indicates the number of nodes in the lattice/graph. The `external_field` field is a list with length equal to the value of `nodes`, which indicates the external field strength per node. The `interactions` field contains a list of triplets, indicating the first node, second, and interaction strength respectively. Nodes are 0-indexed.