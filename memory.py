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

    def add_description_to_node(self, node_name, description):
        """Adds or updates the description attribute of a node."""
        if self.graph.has_node(node_name):
            self.graph.nodes[node_name]['description'] = description
            print(f"✅ Description for node '{node_name}' has been updated in memory.")
        else:
            print(f"⚠️ Could not add description. Node '{node_name}' not found in memory.")

    def add_connection(self, node1, node2, relationship="is_related_to"):
        """Connects two concepts."""
        self.graph.add_edge(node1, node2, label=relationship)

    def find_connected_nodes(self, node_name):
        """Finds all nodes connected to a given node."""
        if node_name in self.graph:
            return list(self.graph.neighbors(node_name))
        return []

    def save_to_json(self):
        """Saves the graph to its designated file inside the mind directory."""
        os.makedirs(self.mind_directory, exist_ok=True)
        data = nx.node_link_data(self.graph, edges='links')
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)
        print(f"✅ Memory graph saved to {self.filepath}")

    def load_from_json(self):
        """Loads the graph from its designated file."""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data, edges='links')
            print(f"✅ Memory graph loaded successfully from {self.filepath}")
        except (FileNotFoundError, json.JSONDecodeError):
            print("⚠️ No valid memory file found.")
            self.graph.clear()

    def visualize(self):
        """Creates a visual representation of the memory graph."""
        if not self.graph.nodes():
            print("Cannot visualize an empty graph.")
            return
        print("Generating memory visualization...")
        plt.figure(figsize=(16, 12))
        pos = nx.spring_layout(self.graph, k=0.8, iterations=50)
        nx.draw(self.graph, pos, with_labels=True, node_color='skyblue', node_size=3500,
                edge_color='gray', font_size=12, font_weight='bold', width=1.5)
        edge_labels = nx.get_edge_attributes(self.graph, 'label')
        nx.draw_networkx_edge_labels(self.graph, pos, edge_labels=edge_labels, font_color='red')
        plt.title("Hizawye's Memory Map", size=20)
        plt.show()

    # --- NEW: Centralized function for creating the default mind ---
    def create_default_mind(self):
        """Wipes the current graph and builds the standard initial mind."""
        self.graph.clear()
        print("Injecting core concepts into the new mind...")
        
        # Core entity
        self.add_node("hizawye AI")
        # Abstract concepts & drivers
        concepts = [
            "knowledge", "creativity", "belief system", "curiosity", "pain",
            "questioning", "wandering", "ideas", "boredom", "memory",
            "reason", "desires", "goals", "delusions"
        ]
        for concept in concepts:
            self.add_node(concept)

        # Creating connections
        print("Forming initial pathways and relationships...")
        self.add_connection("hizawye AI", "knowledge", relationship="attracted_to")
        self.add_connection("hizawye AI", "boredom", relationship="avoids")
        self.add_connection("hizawye AI", "wandering", relationship="engages_in")
        self.add_connection("hizawye AI", "questioning", relationship="driven_by")
        self.add_connection("hizawye AI", "curiosity", relationship="feels")
        self.add_connection("hizawye AI", "pain", relationship="can_experience")
        self.add_connection("hizawye AI", "goals", relationship="has")
        self.add_connection("hizawye AI", "desires", "has")
        self.add_connection("memory", "reason", relationship="informs")
        self.add_connection("reason", "questioning", relationship="leads_to")
        self.add_connection("wandering", "ideas", relationship="generates")
        self.add_connection("knowledge", "creativity", relationship="enables")
        self.add_connection("creativity", "ideas", relationship="produces")
        self.add_connection("belief system", "delusions", relationship="can_contain")
        self.add_connection("belief system", "knowledge", relationship="is_built_from")

        print("\n--- New mind structure is complete. ---")


if __name__ == '__main__':
    print("--- Running Memory Visualization/Creation Script ---")
    memory = MemoryGraph()
    memory.load_from_json()
    
    if not memory.graph.nodes():
        print("No existing memory found. Creating a new, default mind state...")
        memory.create_default_mind()
        memory.save_to_json()
    else:
        print("✅ Existing memory has been loaded.")

    memory.visualize()