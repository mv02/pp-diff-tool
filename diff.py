import argparse
import json
from node import Node


def load_data(path: str) -> set[Node]:
    """Load JSON file from specified path and return parsed data."""
    with open(path, "r") as file:
        data = json.load(file)
    methods = data["methods"]
    id = 0
    nodes = dict()

    # Add all methods to set
    for method in methods:
        nodes[method] = Node(id, method, method in data["entrypoints"])
        id += 1
        for invoke in methods[method]:
            for implementation in methods[method][invoke]:
                nodes[implementation] = Node(id, implementation, implementation in data["entrypoints"])
                id += 1
    # Link children and ancestors together
    for method in methods:
        for invoke in methods[method]:
            for implementation in methods[method][invoke]:
                nodes[implementation].ancestors.add(nodes[method])
                nodes[method].children.add(nodes[implementation])

    return set(nodes.values())


def print_tree(node: Node, diff: set[Node]):
    """Print tree in DOT format recursively."""
    if node.visited:
        return

    node.visited = True
    node.children = {n for n in node.children if n in diff}

    if not node.has_children():
        print(f'    "{str(node)}";')
        return

    for child in node.children:
        print(f'    "{str(node)}" -> "{str(child)}";')
        print_tree(child, diff)


def to_output(node: Node, subgraph: int):
    """Generate 3d-force-graph data recursively."""
    if node.visited:
        return {"nodes": [], "links": []}

    node.visited = True
    node.children = {n for n in node.children if n in diff}

    output = {"nodes": [{"id": node.id, "name": node.name, "shortName": node.short_name, "subgraph": subgraph}], "links": []}

    for child in node.children:
        output["links"].append({"source": node.id, "target": child.id})
        output["nodes"] += to_output(child, subgraph)["nodes"]

    return output


# Parse command-line arguments
parser = argparse.ArgumentParser()
parser.add_argument('file1')
parser.add_argument('file2')
args = parser.parse_args()

# Load data from given files
nodes1 = load_data(args.file1)
nodes2 = load_data(args.file2)

# Perform a set difference of loaded trees and filter out methods with hashes in their name
diff1 = {n for n in nodes1 - nodes2 if not "$Proxy" in n.name and not "LambdaForm$MH" in n.name}
diff2 = {n for n in nodes2 - nodes1 if not "$Proxy" in n.name and not "LambdaForm$MH" in n.name}

# Pick the larger (= non-empty) difference
diff = diff1 if len(diff1) > len(diff2) else diff2
print(f"// The graphs differ in {len(diff)} nodes.")

# Select and sort root nodes
roots = {node for node in diff if not node.has_ancestors() or len(node.ancestors.intersection(diff)) == 0}
roots = sorted(roots)

# Generate the graph data for 3d-force-graph
output = {"nodes": [], "links": []}

for i, node in enumerate(roots):
    tmp = to_output(node, i)
    output["nodes"] += tmp["nodes"]
    output["links"] += tmp["links"]

with open("data.js", "w") as file:
    file.write("const data = ")
    json.dump(output, file)
