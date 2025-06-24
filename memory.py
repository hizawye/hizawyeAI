import networkx as nx
import json
import os
import matplotlib.pyplot as plt

class MemoryGraph:
    def __init__(self, mind_directory="hizawye_mind"):
        """Initializes the memory graph, aware of its directory."""
        self.graph = nx.Graph()
        self.mind_directory = mind_directory
        self.filepath = os.path.join(self.mind_directory, "memory_graph.json")

    def add_node(self, node_name, attributes=None):
        """Adds a concept/node to the memory."""
        self.graph.add_node(node_name, **(attributes or {}))

    def add_connection(self, node1, node2, relationship="is_related_to"):
        """Connects two concepts."""
        self.graph.add_edge(node1, node2, label=relationship)

    def find_connected_nodes(self, node_name):
        """Finds all nodes connected to a given node."""
        if node_name in self.graph:
            return list(self.graph.neighbors(node_name))
        return []

    def get_unexplored_ideas(self):
        """Finds nodes with few connections, representing dead ends to research."""
        unexplored = []
        for node in self.graph.nodes():
            if self.graph.degree(node) <= 1:
                unexplored.append(node)
        return unexplored

    def save_to_json(self):
        """Saves the graph to its designated file inside the mind directory."""
        os.makedirs(self.mind_directory, exist_ok=True)
        # This function correctly creates dictionary data FROM a graph
        data = nx.node_link_data(self.graph)
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def load_from_json(self):
        """Loads the graph from its designated file."""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            # --- FIX: Use node_link_graph to create a graph FROM data ---
            self.graph = nx.node_link_graph(data)
        except FileNotFoundError:
            print("No existing memory file found. Starting with a fresh memory.")
            self.save_to_json()
            
    def visualize(self):
        """Creates a visual representation of the memory graph."""
        pos = nx.spring_layout(self.graph, k=0.9, iterations=50)
        nx.draw(self.graph, pos, with_labels=True, node_color='skyblue', node_size=2000, edge_color='gray', font_size=10)
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels)
        plt.show()


if __name__ == '__main__':
    memory = MemoryGraph()
    memory.load_from_json() # Load previous memory if it exists
    
    # Let's add some initial concepts based on your diagram
    memory.add_node("hizawye AI")
    memory.add_node("knowledge")
    memory.add_node("creativity")
    
    memory.add_connection("hizawye AI", "knowledge", relationship="attracted_to")
    memory.add_connection("knowledge", "creativity", relationship="enables")
    
    print("Unexplored Ideas:", memory.get_unexplored_ideas())
    
    memory.save_to_json() # Save the state of the memory
    memory.visualize()