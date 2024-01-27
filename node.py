class Node:
    visited = False

    def __init__(self, id: int, name: str, entrypoint: bool):
        self.id = id
        self.name = name
        self.entrypoint = entrypoint
        self.children = set()
        self.ancestors = set()

    def has_children(self):
        return len(self.children) > 0

    def has_ancestors(self):
        return len(self.ancestors) > 0

    def __eq__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.name == other.name

    def __lt__(self, other):
        if not isinstance(other, Node):
            return NotImplemented
        return self.name < other.name

    def __hash__(self):
        return hash(self.name)

    def __repr__(self):
        return self.name
