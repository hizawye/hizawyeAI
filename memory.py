import networkx as nx
import json
import os
import random
import math
from datetime import datetime, timezone
# --- NEW: Force a non-interactive backend for matplotlib ---
# This must be done BEFORE importing pyplot
import matplotlib
matplotlib.use('Agg')
# --- END NEW ---
import matplotlib.pyplot as plt
from log import setup_logger

# Initialize the logger
logger = setup_logger()

class MemoryGraph:
    def __init__(self, mind_directory="hizawye_mind"):
        """Initializes the memory graph, aware of its directory."""
        self.graph = nx.Graph()
        self.mind_directory = mind_directory
        self.filepath = os.path.join(self.mind_directory, "memory_graph.json")
        self.attention_scores = {}  # Node importance scores
        self.working_memory = []    # Hot cache of active concepts (7±2 limit)
        self.working_memory_capacity = 7

    def add_node(self, node_name, attributes=None):
        """Adds a concept/node to the memory."""
        self.graph.add_node(node_name, **(attributes or {}))
        logger.info(f"Node '{node_name}' added to memory graph.")

    def add_description_to_node(self, node_name, description):
        """Adds or updates the description attribute of a node."""
        if self.graph.has_node(node_name):
            self.graph.nodes[node_name]['description'] = description
            logger.info(f"Description for node '{node_name}' has been updated.")
        else:
            logger.warning(f"Attempted to add description to non-existent node '{node_name}'.")

    def add_connection(self, node1, node2, relationship="is_related_to"):
        """Connects two concepts."""
        now = datetime.now(timezone.utc).isoformat()
        if self.graph.has_edge(node1, node2):
            edge_data = self.graph.get_edge_data(node1, node2) or {}
            weight = int(edge_data.get("weight", 1)) + 1
            label = relationship or edge_data.get("label", "is_related_to")
        else:
            weight = 1
            label = relationship

        self.graph.add_edge(
            node1,
            node2,
            label=label,
            weight=weight,
            last_updated=now
        )
        logger.info(
            f"Connection created between '{node1}' and '{node2}' with relationship '{label}'."
        )

    def find_connected_nodes(self, node_name):
        """Finds all nodes connected to a given node."""
        if node_name in self.graph:
            return list(self.graph.neighbors(node_name))
        return []

    def compute_attention_scores(self, current_focus=None, recency_weight=0.3):
        """
        Compute importance/attention scores for all nodes using:
        - PageRank (centrality in graph)
        - Spreading activation from current focus
        - Recency (recently accessed nodes stay active)
        """
        if not self.graph.nodes():
            return {}

        # Base scores from PageRank (structural importance)
        try:
            pagerank_scores = nx.pagerank(self.graph, alpha=0.85)
        except:
            pagerank_scores = {node: 1.0 / len(self.graph.nodes()) for node in self.graph.nodes()}

        # Spreading activation from current focus
        activation_scores = {}
        if current_focus and current_focus in self.graph:
            # Current focus gets max activation
            activation_scores[current_focus] = 1.0

            # 1-hop neighbors get moderate activation
            for neighbor in self.graph.neighbors(current_focus):
                activation_scores[neighbor] = 0.6

            # 2-hop neighbors get lower activation
            try:
                two_hop = set()
                for neighbor in self.graph.neighbors(current_focus):
                    for second_neighbor in self.graph.neighbors(neighbor):
                        if second_neighbor != current_focus:
                            two_hop.add(second_neighbor)
                for node in two_hop:
                    if node not in activation_scores:
                        activation_scores[node] = 0.3
            except:
                pass

        # Combine scores
        combined_scores = {}
        for node in self.graph.nodes():
            pagerank = pagerank_scores.get(node, 0.1)
            activation = activation_scores.get(node, 0.0)
            recency = 1.0 if node in self.working_memory else 0.0

            # Weighted combination
            combined_scores[node] = (
                pagerank * 0.4 +
                activation * 0.4 +
                recency * recency_weight
            )

        self.attention_scores = combined_scores
        logger.info(f"Computed attention scores for {len(combined_scores)} nodes")
        return combined_scores

    def get_rich_context(self, concept, max_depth=2):
        """
        Get comprehensive context for a concept including:
        - Concept's own description
        - 1-hop neighbors with relationships
        - Paths to related understood concepts
        - Semantic density (connectivity metric)
        """
        if not self.graph.has_node(concept):
            return f"Concept '{concept}' is not yet in memory."

        context_parts = []

        # Own description
        node_data = self.graph.nodes[concept]
        if node_data.get('description'):
            context_parts.append(f"Known: {node_data['description']}")
        else:
            context_parts.append(f"'{concept}' is not yet understood.")

        # 1-hop neighbors with relationships
        neighbors = list(self.graph.neighbors(concept))
        if neighbors:
            neighbor_info = []
            for neighbor in neighbors[:5]:  # Limit to top 5
                edge_data = self.graph.get_edge_data(concept, neighbor)
                relationship = edge_data.get('label', 'is_related_to') if edge_data else 'is_related_to'

                neighbor_node_data = self.graph.nodes[neighbor]
                if neighbor_node_data.get('description'):
                    neighbor_info.append(f"{concept} {relationship} {neighbor} (understood)")
                else:
                    neighbor_info.append(f"{concept} {relationship} {neighbor}")

            if neighbor_info:
                context_parts.append("Connections: " + "; ".join(neighbor_info))

        # Paths to understood concepts (shows how to reach knowledge)
        understood_nodes = [
            node for node, data in self.graph.nodes(data=True)
            if data.get('description') and node != concept
        ]

        if understood_nodes and len(understood_nodes) > 0:
            # Find shortest path to any understood concept
            closest_understood = None
            min_distance = float('inf')

            for understood_node in understood_nodes[:10]:  # Check closest 10
                try:
                    path_length = nx.shortest_path_length(self.graph, concept, understood_node)
                    if path_length < min_distance and path_length > 0:
                        min_distance = path_length
                        closest_understood = understood_node
                except nx.NetworkXNoPath:
                    continue

            if closest_understood and min_distance <= max_depth:
                try:
                    path = nx.shortest_path(self.graph, concept, closest_understood)
                    context_parts.append(f"Path to knowledge: {' → '.join(path)}")
                except:
                    pass

        # Semantic density (how connected is this area?)
        density = len(neighbors) / max(1, len(self.graph.nodes()))
        if density > 0.3:
            context_parts.append("This concept is in a densely connected area of knowledge.")
        elif density < 0.1:
            context_parts.append("This concept is relatively isolated.")

        return " | ".join(context_parts)

    def find_analogies(self, concept_a, concept_b):
        """
        Find structural similarities between two concepts.
        Returns: analogy score (0-1) and shared patterns.
        """
        if not (self.graph.has_node(concept_a) and self.graph.has_node(concept_b)):
            return 0.0, []

        # Shared neighbors (concepts connected to both)
        neighbors_a = set(self.graph.neighbors(concept_a))
        neighbors_b = set(self.graph.neighbors(concept_b))
        shared = neighbors_a & neighbors_b

        # Structural similarity: compare degree, clustering
        degree_a = self.graph.degree(concept_a)
        degree_b = self.graph.degree(concept_b)
        degree_similarity = 1.0 - abs(degree_a - degree_b) / max(degree_a, degree_b, 1)

        # Relationship pattern similarity
        relationships_a = set()
        relationships_b = set()

        for neighbor in neighbors_a:
            edge_data = self.graph.get_edge_data(concept_a, neighbor)
            if edge_data:
                relationships_a.add(edge_data.get('label', 'is_related_to'))

        for neighbor in neighbors_b:
            edge_data = self.graph.get_edge_data(concept_b, neighbor)
            if edge_data:
                relationships_b.add(edge_data.get('label', 'is_related_to'))

        shared_relationships = relationships_a & relationships_b

        # Compute analogy score
        analogy_score = (
            len(shared) / max(len(neighbors_a | neighbors_b), 1) * 0.5 +
            degree_similarity * 0.3 +
            len(shared_relationships) / max(len(relationships_a | relationships_b), 1) * 0.2
        )

        patterns = {
            'shared_neighbors': list(shared),
            'shared_relationships': list(shared_relationships)
        }

        return analogy_score, patterns

    def update_working_memory(self, concept):
        """
        Maintain working memory cache (Miller's 7±2 rule).
        Recently accessed concepts stay hot for faster retrieval.
        """
        # Add to working memory
        if concept in self.working_memory:
            # Move to front (most recent)
            self.working_memory.remove(concept)

        self.working_memory.insert(0, concept)

        # Evict if over capacity (LRU)
        if len(self.working_memory) > self.working_memory_capacity:
            evicted = self.working_memory.pop()
            logger.info(f"Working memory: evicted '{evicted}', added '{concept}'")

    def get_working_memory_concepts(self):
        """Get currently active concepts in working memory."""
        return self.working_memory.copy()

    def find_exploration_target(self, current_focus, avoid_recent=True):
        """
        Intelligently select next concept to explore.
        Uses attention scores to prioritize important/relevant concepts.
        """
        if not current_focus or current_focus not in self.graph:
            # Random selection if no focus
            if self.graph.nodes():
                return random.choice(list(self.graph.nodes()))
            return None

        # Update attention scores based on current focus
        self.compute_attention_scores(current_focus)

        # Get candidates (connected concepts)
        candidates = list(self.graph.neighbors(current_focus))

        if not candidates:
            # Dead end: pick highest attention score globally
            sorted_nodes = sorted(
                self.attention_scores.items(),
                key=lambda x: x[1],
                reverse=True
            )
            for node, score in sorted_nodes:
                if not avoid_recent or node not in self.working_memory:
                    return node
            return sorted_nodes[0][0] if sorted_nodes else None

        # Filter out recently explored if requested
        if avoid_recent:
            candidates = [c for c in candidates if c not in self.working_memory[:3]]

        if not candidates:
            candidates = list(self.graph.neighbors(current_focus))

        # Score candidates by attention
        candidate_scores = {
            c: self.attention_scores.get(c, 0.0) for c in candidates
        }

        # Weight by understanding status (prefer ununderstood)
        for candidate in candidates:
            node_data = self.graph.nodes[candidate]
            if not node_data.get('description'):
                candidate_scores[candidate] *= 1.5  # Boost unknown concepts

        # Select highest scoring candidate
        if candidate_scores:
            best_candidate = max(candidate_scores.items(), key=lambda x: x[1])[0]
            return best_candidate

        return random.choice(candidates) if candidates else None

    def save_to_json(self):
        """Saves the graph to its designated file inside the mind directory."""
        os.makedirs(self.mind_directory, exist_ok=True)
        data = nx.node_link_data(self.graph, edges='links')
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)
        # We log the save action from hizawye_ai.py which has more context

    def load_from_json(self):
        """Loads the graph from its designated file."""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
            self.graph = nx.node_link_graph(data, edges='links')
            logger.info(f"Memory graph loaded successfully from {self.filepath}")
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning("No valid memory file found. The graph will be empty.")
            self.graph.clear()
            
    def visualize(self, current_focus=None, label_top_k=12, overview_top_k=20):
        """Creates a visual representation of the memory graph and saves it to a file."""
        if not self.graph.nodes():
            print("Cannot visualize an empty graph.")
            return

        print("Generating memory visualization...")

        attention_scores = self.compute_attention_scores(current_focus=current_focus)
        scores = list(attention_scores.values()) if attention_scores else [0.0]
        min_score = min(scores)
        max_score = max(scores)
        score_range = max(max_score - min_score, 1e-6)

        def scale_score(score, min_size=1200, max_size=5200):
            normalized = (score - min_score) / score_range
            return min_size + normalized * (max_size - min_size)

        known_nodes = {
            node for node, data in self.graph.nodes(data=True)
            if data.get('description')
        }

        top_nodes = sorted(
            attention_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:max(3, min(label_top_k, len(self.graph.nodes())))]
        top_set = {node for node, _ in top_nodes}

        colors = {
            "known": "#4CAF50",
            "unknown": "#FFB74D",
            "top": "#1976D2",
        }

        node_sizes = []
        node_colors = []
        node_edgecolors = []
        node_edgewidths = []
        for node in self.graph.nodes():
            score = attention_scores.get(node, 0.0)
            size = scale_score(score)
            if node in top_set:
                size *= 1.25
                node_colors.append(colors["top"])
            elif node in known_nodes:
                node_colors.append(colors["known"])
            else:
                node_colors.append(colors["unknown"])
            node_sizes.append(size)

            if current_focus and node == current_focus:
                node_edgecolors.append("#FFD54F")
                node_edgewidths.append(3.0)
            else:
                node_edgecolors.append("#263238")
                node_edgewidths.append(1.5)

        if len(self.graph.nodes()) <= 30:
            label_nodes = set(self.graph.nodes())
        else:
            label_nodes = set(top_set)

        if current_focus:
            label_nodes.add(current_focus)

        labels = {node: node for node in label_nodes}

        plt.figure(figsize=(20, 16))
        pos = nx.spring_layout(self.graph, k=0.9, iterations=80, seed=7)

        nx.draw_networkx_nodes(
            self.graph,
            pos,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors=node_edgecolors,
            linewidths=node_edgewidths
        )
        edge_widths = self._edge_widths(self.graph)
        nx.draw_networkx_edges(
            self.graph,
            pos,
            edge_color="#90A4AE",
            width=edge_widths,
            alpha=0.8
        )
        nx.draw_networkx_labels(
            self.graph,
            pos,
            labels=labels,
            font_size=11,
            font_weight="bold"
        )

        edge_labels = {
            (u, v): data.get('label', '')
            for u, v, data in self.graph.edges(data=True)
            if u in label_nodes and v in label_nodes
        }
        nx.draw_networkx_edge_labels(
            self.graph,
            pos,
            edge_labels=edge_labels,
            font_color="#C62828",
            font_size=9
        )

        from matplotlib.patches import Patch
        legend_items = [
            Patch(facecolor=colors["top"], edgecolor="#263238", label="Top attention"),
            Patch(facecolor=colors["known"], edgecolor="#263238", label="Known concept"),
            Patch(facecolor=colors["unknown"], edgecolor="#263238", label="Unknown concept"),
        ]
        if current_focus:
            legend_items.append(Patch(facecolor="#FFD54F", edgecolor="#263238", label="Current focus"))
        plt.legend(handles=legend_items, loc="upper right", frameon=True)

        plt.title("Hizawye's Memory Map", size=24)
        plt.axis("off")

        output_path = os.path.join(self.mind_directory, "memory_map.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Memory map saved as an image to: {output_path}")

        if overview_top_k and len(self.graph.nodes()) > 0:
            top_k = min(overview_top_k, len(self.graph.nodes()))
            self._save_overview_map(attention_scores, top_k, current_focus)

    def _edge_widths(self, graph):
        widths = []
        for _, _, data in graph.edges(data=True):
            weight = max(1, int(data.get("weight", 1)))
            width = 1.0 + min(4.0, math.log1p(weight))

            last_updated = data.get("last_updated")
            if last_updated:
                try:
                    updated = datetime.fromisoformat(last_updated)
                    age_days = (datetime.now(timezone.utc) - updated).days
                    recency_factor = max(0.5, 1.0 - (age_days / 30.0))
                    width *= recency_factor
                except ValueError:
                    pass

            widths.append(width)
        return widths

    def _save_overview_map(self, attention_scores, overview_top_k, current_focus=None):
        top_nodes = sorted(
            attention_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )[:overview_top_k]
        node_set = {node for node, _ in top_nodes}
        if current_focus:
            node_set.add(current_focus)

        subgraph = self.graph.subgraph(node_set).copy()

        if not subgraph.nodes():
            return

        labels = {node: node for node in subgraph.nodes()}
        plt.figure(figsize=(14, 12))
        pos = nx.spring_layout(subgraph, k=0.8, iterations=60, seed=11)

        node_colors = []
        node_edgecolors = []
        node_sizes = []
        for node in subgraph.nodes():
            if node in node_set:
                node_colors.append("#1976D2")
            else:
                node_colors.append("#90A4AE")
            node_sizes.append(2000)
            if current_focus and node == current_focus:
                node_edgecolors.append("#FFD54F")
            else:
                node_edgecolors.append("#263238")

        nx.draw_networkx_nodes(
            subgraph,
            pos,
            node_color=node_colors,
            node_size=node_sizes,
            edgecolors=node_edgecolors,
            linewidths=1.5
        )
        edge_widths = self._edge_widths(subgraph)
        nx.draw_networkx_edges(
            subgraph,
            pos,
            edge_color="#90A4AE",
            width=edge_widths,
            alpha=0.9
        )
        nx.draw_networkx_labels(
            subgraph,
            pos,
            labels=labels,
            font_size=10,
            font_weight="bold"
        )

        plt.title("Hizawye's Memory Map (Top Attention)", size=20)
        plt.axis("off")
        output_path = os.path.join(self.mind_directory, "memory_map_focus.png")
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✅ Memory focus map saved as an image to: {output_path}")

    def create_default_mind(self):
        """Wipes the current graph and builds the standard initial mind."""
        self.graph.clear()
        logger.info("Creating default mind state in memory graph.")
        print("Injecting core concepts into the new mind...")
        
        self.add_node("hizawye AI")
        concepts = [
            "knowledge", "creativity", "belief system", "curiosity", "pain",
            "questioning", "wandering", "ideas", "boredom", "memory",
            "reason", "desires", "goals", "delusions"
        ]
        for concept in concepts:
            self.add_node(concept)

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

        logger.info("Default mind structure created.")
        print("\n--- New mind structure is complete. ---")


if __name__ == '__main__':
    print("--- Running Memory Visualization/Creation Script ---")
    memory = MemoryGraph()
    memory.load_from_json()

    current_focus = None
    goals_path = os.path.join(memory.mind_directory, "goals.json")
    if os.path.exists(goals_path):
        try:
            with open(goals_path, "r") as f:
                goals_data = json.load(f)
            active_goals = goals_data.get("active_goals", []) if isinstance(goals_data, dict) else []
            if active_goals:
                first_goal = active_goals[0]
                if isinstance(first_goal, dict):
                    current_focus = first_goal.get("concept")
        except (json.JSONDecodeError, OSError):
            current_focus = None
    
    if not memory.graph.nodes():
        print("No existing memory found. Creating a new, default mind state...")
        memory.create_default_mind()
        memory.save_to_json()
    else:
        print("✅ Existing memory has been loaded.")

    memory.visualize(current_focus=current_focus)
