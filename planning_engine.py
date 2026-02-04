"""
Planning Engine: Intelligent goal decomposition and strategy selection.
Replaces hardcoded goal patterns with adaptive planning.
"""
import random
from log import setup_logger

logger = setup_logger()

class PlanningEngine:
    def __init__(self, memory_graph, emotional_system, learning_tracker):
        self.memory = memory_graph
        self.emotions = emotional_system
        self.learner = learning_tracker

        # Strategy library with metadata
        self.strategies = {
            'direct_define': {
                'name': 'Direct Definition',
                'description': 'Attempt to define concept directly in one step',
                'complexity': 'simple',
                'best_for': 'concrete concepts',
                'llm_task': lambda concept: f"Define the concept '{concept}' in a single, concise, first-person sentence. Example: 'Creativity is the ability to connect disparate ideas in novel ways.'"
            },
            'analogical_reasoning': {
                'name': 'Analogical Reasoning',
                'description': 'Understand concept through analogy to known concepts',
                'complexity': 'moderate',
                'best_for': 'abstract concepts with familiar parallels',
                'llm_task': lambda concept: f"Explain '{concept}' by drawing an analogy to a simpler, more concrete concept. Format: '{concept} is like [simpler concept] because...'"
            },
            'bottom_up_composition': {
                'name': 'Bottom-Up Composition',
                'description': 'Build understanding from simpler components',
                'complexity': 'moderate',
                'best_for': 'composite concepts',
                'llm_task': lambda concept: f"Identify 2-3 foundational sub-concepts that compose '{concept}'. Output as JSON array: [\"sub1\", \"sub2\"]"
            },
            'top_down_decomposition': {
                'name': 'Top-Down Decomposition',
                'description': 'Break complex concept into parts',
                'complexity': 'moderate',
                'best_for': 'complex, multifaceted concepts',
                'llm_task': lambda concept: f"Break '{concept}' into 3 distinct aspects or dimensions. Output as JSON array: [\"aspect1\", \"aspect2\", \"aspect3\"]"
            },
            'contextual_synthesis': {
                'name': 'Contextual Synthesis',
                'description': 'Understand concept through its relationships',
                'complexity': 'complex',
                'best_for': 'relational concepts',
                'llm_task': lambda concept, neighbors: f"Define '{concept}' in relation to these connected concepts: {neighbors}. Show how '{concept}' bridges or differs from them."
            }
        }

    def select_strategy(self, concept, context=None):
        """
        Intelligently select best strategy for understanding a concept.
        Considers: graph structure, emotional state, learning history, concept complexity.
        """
        available_strategies = list(self.strategies.keys())

        # Get emotional drives
        drives = self.emotions.compute_drive_vector()
        current_pain = self.emotions.get_total_pain()

        # Filter strategies based on emotional state
        if drives['should_simplify']:
            # High pain/confusion → prefer simpler strategies
            available_strategies = [
                s for s in available_strategies
                if self.strategies[s]['complexity'] in ['simple', 'moderate']
            ]
            logger.info("Pain threshold high, limiting to simpler strategies")

        # Use learning history to recommend best strategy
        if available_strategies:
            recommended = self.learner.recommend_strategy(
                concept,
                available_strategies,
                current_pain
            )
            if recommended:
                return recommended

        # Fallback: analyze graph structure
        graph_distance = self._compute_graph_distance(concept)

        if graph_distance == 0:
            # Concept not in graph yet, try direct definition first
            return 'direct_define'
        elif graph_distance > 3:
            # Far from known concepts, use analogy or decomposition
            return random.choice(['analogical_reasoning', 'top_down_decomposition'])
        else:
            # Close to known concepts, try contextual synthesis
            return 'contextual_synthesis'

    def _compute_graph_distance(self, concept):
        """
        Compute minimum distance from concept to any understood node.
        Returns 0 if concept not in graph, otherwise min path length.
        """
        if not self.memory.graph.has_node(concept):
            return 0

        # Find all understood nodes (nodes with descriptions)
        understood_nodes = [
            node for node, data in self.memory.graph.nodes(data=True)
            if data.get('description')
        ]

        if not understood_nodes:
            return float('inf')

        import networkx as nx
        min_distance = float('inf')

        for understood_node in understood_nodes:
            try:
                distance = nx.shortest_path_length(self.memory.graph, concept, understood_node)
                min_distance = min(min_distance, distance)
            except nx.NetworkXNoPath:
                continue

        return min_distance if min_distance != float('inf') else 5

    def create_goal_for_concept(self, concept, strategy=None):
        """
        Create a structured goal object (replaces hardcoded goal strings).
        """
        if strategy is None:
            strategy = self.select_strategy(concept)

        strategy_info = self.strategies[strategy]

        goal = {
            'type': 'understand_concept',
            'concept': concept,
            'strategy': strategy,
            'strategy_name': strategy_info['name'],
            'attempts': 0,
            'created_at': self._get_timestamp()
        }

        logger.info(f"Created goal: understand '{concept}' using '{strategy_info['name']}'")
        return goal

    def execute_goal(self, goal, llm_function):
        """
        Execute a goal using the selected strategy.
        Returns: (success: bool, result: dict, pain_delta: float)
        """
        concept = goal['concept']
        strategy = goal['strategy']
        strategy_info = self.strategies[strategy]

        # Track attempt
        goal['attempts'] += 1

        # Generate LLM task based on strategy
        if strategy == 'contextual_synthesis':
            neighbors = self.memory.find_connected_nodes(concept)
            task = strategy_info['llm_task'](concept, neighbors)
        elif strategy in ['bottom_up_composition', 'top_down_decomposition']:
            task = strategy_info['llm_task'](concept)
        else:
            task = strategy_info['llm_task'](concept)

        # Modulate prompt based on emotional state
        task = self.emotions.modulate_llm_prompt(task, context_type='definition')

        # Execute LLM call
        logger.info(f"Executing strategy '{strategy}' for '{concept}'")
        llm_response = llm_function(task)

        # Process result based on strategy type
        if strategy in ['bottom_up_composition', 'top_down_decomposition']:
            return self._process_decomposition_result(concept, strategy, llm_response)
        else:
            return self._process_definition_result(concept, strategy, llm_response)

    def _process_definition_result(self, concept, strategy, llm_response):
        """
        Validate and process a definition result.
        Returns: (success, result_dict, pain_delta)
        """
        # Extract clean thought (remove thinking tags)
        clean_thought = self._extract_final_thought(llm_response)

        # Validate definition quality
        invalid_phrases = [
            "system instruction", "your task", "your output", "define the concept",
            "direct fulfillment", "echo instructions", "first-person realization",
            "example:", "as a thought synthesizer"
        ]

        is_invalid = (
            "i feel disconnected" in clean_thought.lower() or
            any(phrase in clean_thought.lower() for phrase in invalid_phrases) or
            len(clean_thought) > 300 or
            len(clean_thought.split()) < 4
        )

        if is_invalid:
            logger.warning(f"Invalid definition for '{concept}' using '{strategy}'")
            return (False, {'error': 'malformed_response', 'response': llm_response}, 25.0)

        # Success: valid definition
        logger.info(f"Valid definition for '{concept}'")
        return (True, {'definition': clean_thought}, -20.0)

    def _process_decomposition_result(self, concept, strategy, llm_response):
        """
        Parse and validate decomposition (JSON array) result.
        Returns: (success, result_dict, pain_delta)
        """
        import json

        try:
            # Extract JSON array from response
            json_start = llm_response.find('[')
            json_end = llm_response.rfind(']') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON array found")

            json_str = llm_response[json_start:json_end]
            raw_concepts = json.loads(json_str)

            # Flatten nested arrays
            sub_concepts = []
            def flatten(lst):
                for el in lst:
                    if isinstance(el, list):
                        flatten(el)
                    else:
                        sub_concepts.append(str(el))
            flatten(raw_concepts)

            if len(sub_concepts) < 2:
                raise ValueError("Too few sub-concepts")

            logger.info(f"Successfully decomposed '{concept}' into {len(sub_concepts)} parts")
            return (True, {'sub_concepts': sub_concepts}, -10.0)

        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse decomposition: {e}")
            return (False, {'error': 'parse_failure', 'response': llm_response}, 15.0)

    def _extract_final_thought(self, llm_response):
        """Extract final thought, removing <think> tags."""
        if "</think>" in llm_response:
            parts = llm_response.split("</think>")
            clean_thought = parts[-1].strip()
            if clean_thought:
                return clean_thought
        return llm_response

    def _get_timestamp(self):
        """Get current timestamp for goal tracking."""
        from datetime import datetime
        return datetime.now().isoformat()

    def should_retreat(self, goal):
        """
        Determine if we should abandon current strategy and try different approach.
        Based on: repeated failures, excessive pain, emotional state.
        """
        if goal['attempts'] >= 3:
            logger.warning(f"Goal has {goal['attempts']} attempts, should consider retreat")
            return True

        drives = self.emotions.compute_drive_vector()
        if drives['retreat'] > 70:
            logger.warning("Retreat drive is high, should change approach")
            return True

        return False

    def generate_alternative_goal(self, failed_goal):
        """
        After failure, generate an alternative approach.
        Uses different strategy or breaks down the concept differently.
        """
        concept = failed_goal['concept']
        failed_strategy = failed_goal['strategy']

        # Get all strategies except the failed one
        alternative_strategies = [
            s for s in self.strategies.keys()
            if s != failed_strategy
        ]

        if not alternative_strategies:
            # Fallback: create exploration goal
            return {
                'type': 'explore',
                'concept': concept,
                'strategy': 'wandering',
                'attempts': 0
            }

        # Select new strategy
        new_strategy = self.learner.recommend_strategy(
            concept,
            alternative_strategies,
            self.emotions.get_total_pain()
        )

        if not new_strategy:
            new_strategy = random.choice(alternative_strategies)

        logger.info(f"Generated alternative: '{new_strategy}' after '{failed_strategy}' failed")
        return self.create_goal_for_concept(concept, strategy=new_strategy)
