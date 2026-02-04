import json
import random
import os
import signal
from collections import deque
from memory import MemoryGraph
from emotional_system import EmotionalSystem
from learning_tracker import LearningTracker
from planning_engine import PlanningEngine
from workspace import Workspace
from input_stream import SimulatedInputStream
from analytics_engine import AnalyticsEngine
from modules import (
    GoalPlannerModule,
    ExplorationModule,
    ReflectionModule,
    PatternRecognitionModule,
    PerceptionModule,
    MemoryModule,
    EmotionModule,
)
from log import setup_logger
import ollama

# Initialize the logger
logger = setup_logger()

SYSTEM_PROMPT = (
    "You are a concise reasoning engine. "
    "Follow the user's task exactly and return only the requested output. "
    "Do not include preambles, explanations, or markdown."
)

OUTPUT_RULES = (
    "Return only the answer. No preamble. No markdown. No quotes unless requested."
)

class HizawyeAI:
    def __init__(self, mind_directory="hizawye_mind"):
        logger.info("Hizawye AI consciousness initializing with GNW architecture.")
        self.mind_directory = mind_directory
        self.beliefs = {}
        self.goals = {'active_goals': [], 'completed_goals': []}
        self.current_focus = None
        self.keep_running = True
        self.recent_actions = deque(maxlen=10)
        self.recent_explores = deque(maxlen=5)

        # Initialize new subsystems
        self.memory = MemoryGraph(mind_directory=self.mind_directory)
        self.emotions = EmotionalSystem(mind_directory=self.mind_directory)
        self.learner = LearningTracker(mind_directory=self.mind_directory)
        self.planner = PlanningEngine(self.memory, self.emotions, self.learner)
        self.input_stream = SimulatedInputStream()
        self.modules = [
            GoalPlannerModule(self.planner, self.emotions),
            ExplorationModule(self.memory, self.emotions),
            ReflectionModule(self.learner, self.emotions),
            PatternRecognitionModule(self.memory, self.emotions),
            PerceptionModule(self.input_stream, self.memory),
            MemoryModule(self.memory),
            EmotionModule(self.emotions),
        ]
        self.workspace = Workspace(self.modules)
        self.analytics = AnalyticsEngine(mind_directory=self.mind_directory)

        self.load_mind()

    def load_mind(self):
        """Loads the AI's beliefs and goals from the mind directory."""
        logger.info("Loading mind from files...")
        try:
            # Load beliefs and goals (simple JSON)
            beliefs_path = os.path.join(self.mind_directory, 'beliefs.json')
            goals_path = os.path.join(self.mind_directory, 'goals.json')

            if os.path.exists(beliefs_path):
                with open(beliefs_path, 'r') as f:
                    self.beliefs = json.load(f)

            if os.path.exists(goals_path):
                with open(goals_path, 'r') as f:
                    self.goals = json.load(f)

            # Subsystems load their own state
            self.memory.load_from_json()
            self.emotions.load_state()
            self.learner.load_history()

            logger.info("Mind loaded successfully with GNW architecture.")
        except Exception as e:
            logger.error(f"Fatal error loading mind file: {e}. Shutting down.", exc_info=True)
            print(f"Error loading mind file: {e}. You may need to run 'birth.py' to create a fresh mind.")
            exit()

    def save_mind(self):
        """Saves the AI's current state and logs a full snapshot of the mind."""
        logger.info("--- MIND STATE SNAPSHOT ---")
        logger.info(f"Active Goals: {self.goals['active_goals']}")
        logger.info(f"Emotional State: {self.emotions.get_status_summary()}")
        logger.info(f"Learning Summary: {self.learner.get_learning_summary()}")
        logger.info(f"Working Memory: {self.memory.get_working_memory_concepts()}")
        logger.info("--- END SNAPSHOT ---")

        logger.info("Saving mind state to files...")

        # Save beliefs and goals
        with open(os.path.join(self.mind_directory, 'beliefs.json'), 'w') as f:
            json.dump(self.beliefs, f, indent=4)
        with open(os.path.join(self.mind_directory, 'goals.json'), 'w') as f:
            json.dump(self.goals, f, indent=4)

        # Subsystems save their own state
        self.memory.save_to_json()
        self.emotions.save_state()
        self.learner.save_history()

    def _create_simple_prompt(self, task_details):
        """Assembles a direct prompt with strict output rules."""
        prompt = f"Task: {task_details}\nOutput rules: {OUTPUT_RULES}"
        return prompt

    def reason_with_llm(self, prompt):
        """Uses the LLM to process the rich context from the workspace."""
        logger.info(f"Reasoning with LLM.")
        print(f"\n🤔 [Hizawye is reasoning]...\n--- PROMPT ---\n{prompt}\n--------------")
        try:
            response = ollama.chat(
                model='llama3.2:3b',
                messages=[
                    {'role': 'system', 'content': SYSTEM_PROMPT},
                    {'role': 'user', 'content': prompt}
                ],
                options={'temperature': 0.5}
            )
            thought = response['message']['content'].strip()
            logger.info(f"LLM thought received: {thought}")
            print(f"💡 [Hizawye's thought]: {thought}")
            return thought
        except Exception as e:
            logger.error(f"Error communicating with LLM: {e}", exc_info=True)
            return "I feel disconnected."

    def _compute_attention_gain(self):
        """Compute attention gain for workspace competition based on emotional state."""
        total_pain = self.emotions.get_total_pain()
        total_curiosity = self.emotions.get_total_curiosity()
        gain = 1.0 + (total_curiosity - total_pain) / 200.0
        return max(0.6, min(1.4, gain))

    def _compute_exploration_allowed(self):
        """Gate exploration when goal focus is strong."""
        drives = self.emotions.compute_drive_vector()
        focus_drive = drives['focus'] / 100.0
        boredom = self.emotions.get_total_boredom()
        if self.goals['active_goals'] and focus_drive > 0.6 and boredom < 60:
            return False
        return True

    def _compute_perception_scale(self):
        """Scale perceptual salience when focus is strong."""
        drives = self.emotions.compute_drive_vector()
        focus_drive = drives['focus'] / 100.0
        if self.goals['active_goals'] and focus_drive > 0.7:
            return 0.6
        return 1.0

    def _record_action(self, action_type, payload):
        """Record recent actions to reduce repetitive loops."""
        concept = None
        if action_type in {"goal_execute", "goal_switch"}:
            concept = payload.get("concept") or payload.get("goal", {}).get("concept")
        elif action_type == "explore":
            concept = payload.get("target_concept")
        elif action_type == "percept":
            concept = payload.get("concept")
        elif action_type == "analogy":
            concept_pair = payload.get("concept_pair")
            if concept_pair:
                concept = "↔".join(concept_pair)

        record = {"type": action_type, "concept": concept}
        self.recent_actions.append(record)
        if action_type == "explore" and concept:
            self.recent_explores.append(concept)

    def live(self):
        """The main processing loop for the AI using GNW architecture."""
        def stop_handler(signum, frame):
            if self.keep_running:
                logger.info("Shutdown signal received. Preparing for graceful shutdown.")
                print("\n\n--- Shutdown signal received. Performing final save before stopping... ---")
                self.keep_running = False

        signal.signal(signal.SIGINT, stop_handler)

        logger.info("Hizawye AI is now live with GNW workspace. Main loop started.")
        print("--- Hizawye AI is now active (GNW Architecture). Press Ctrl+C to stop safely. ---")

        # Initialize analytics session
        self.analytics.start_session()
        logger.info(f"Analytics session started: {self.analytics.session_id}")

        # Initialize graph with self if empty
        if not self.memory.graph.nodes():
            self.memory.add_node("hizawye")

        # Set initial focus
        if not self.current_focus and self.memory.graph.nodes():
            self.current_focus = random.choice(list(self.memory.graph.nodes()))

        # Record initial memory state
        initial_nodes = len(self.memory.graph.nodes())
        initial_edges = len(self.memory.graph.edges())
        self.analytics.record_memory_growth(total_nodes=initial_nodes)

        cycle_count = 0

        while self.keep_running:
            cycle_count += 1
            mind_changed = False
            self.analytics.increment_cycle()

            # Update working memory with current focus
            if self.current_focus:
                self.memory.update_working_memory(self.current_focus)

            # Convert legacy goals to new format if needed
            self._migrate_legacy_goals()

            # Update workspace context
            self.workspace.update_context(
                active_goals=self.goals['active_goals'],
                current_focus=self.current_focus,
                cycle=cycle_count,
                attention_gain=self._compute_attention_gain(),
                exploration_allowed=self._compute_exploration_allowed(),
                perception_scale=self._compute_perception_scale(),
                recent_explores=list(self.recent_explores),
                recent_actions=list(self.recent_actions),
            )

            # Run GNW workspace cycle (competition + ignition)
            winning_content = self.workspace.cycle()

            # Track emotional state every cycle
            self.analytics.record_emotional_state(
                cycle=cycle_count,
                emotions=self.emotions.state
            )

            # Track workspace competition
            if getattr(self.workspace, 'last_proposals', None) is not None:
                self.analytics.record_proposal_competition(
                    cycle=cycle_count,
                    proposals=self.workspace.last_proposals,
                    winner=self.workspace.last_winner_proposal
                )

            if winning_content:
                # Execute the ignited workspace content
                mind_changed = self._execute_workspace_content(winning_content)
                if winning_content.ignited:
                    self._record_action(winning_content.type, winning_content.payload)
            else:
                # No proposals (shouldn't happen often)
                logger.warning("No proposals generated in workspace cycle")
                print(".", end="", flush=True)

            # Periodic emotional decay
            if cycle_count % 5 == 0:
                self.emotions.decay_emotions(cycles=5)

            # Save if mind changed
            if mind_changed:
                self.save_mind()
            else:
                print(".", end="", flush=True)

        logger.info("Main loop ended. Performing final save.")
        self.save_mind()

        # Finalize analytics session
        final_nodes = len(self.memory.graph.nodes())
        final_edges = len(self.memory.graph.edges())
        self.analytics.record_memory_growth(
            nodes_added=final_nodes - initial_nodes,
            edges_added=final_edges - initial_edges,
            total_nodes=final_nodes
        )
        self.analytics.end_session()
        analytics_path = self.analytics.save()

        logger.info(f"Analytics saved to: {analytics_path}")
        print(f"\n📊 Analytics session saved: {analytics_path}")

        # Show quick summary
        summary = self.analytics.get_summary_stats()
        print(f"\n=== Session Summary ===")
        print(f"Cycles: {summary['cycles']}")
        print(f"Runtime: {summary['runtime_seconds']:.1f}s")
        print(f"Concepts learned: {summary['successful_concepts']}/{summary['total_concepts']}")
        print(f"Success rate: {summary['success_rate']*100:.1f}%")
        print(f"\nRun 'python analyze.py' to generate detailed reports!")

        logger.info("Hizawye AI has shut down gracefully.")
        print("\n--- Hizawye AI has shut down gracefully. ---")

    def _migrate_legacy_goals(self):
        """Convert old string-based goals to new structured format."""
        migrated = []
        for goal in self.goals['active_goals']:
            if isinstance(goal, str):
                # Extract concept from legacy goal string
                import re
                match = re.search(r"'(.*?)'", goal)
                concept = match.group(1) if match else "unknown"

                # Create new structured goal
                if "Deepen understanding" in goal:
                    new_goal = self.planner.create_goal_for_concept(concept)
                    migrated.append(new_goal)
                elif "Expand knowledge" in goal:
                    migrated.append({
                        'type': 'explore',
                        'concept': concept,
                        'strategy': 'expansion',
                        'attempts': 0
                    })
                else:
                    # Keep as-is if unrecognized
                    migrated.append(goal)
            else:
                # Already new format
                migrated.append(goal)

        self.goals['active_goals'] = migrated

    def _execute_workspace_content(self, content):
        """Execute ignited workspace content."""
        if not content.ignited:
            logger.info("Workspace content persisted without ignition; skipping execution.")
            return False

        action_type = content.type
        payload = content.payload
        mind_changed = False

        logger.info(f"Executing workspace content: {action_type}")
        print(f"\n🧠 [Conscious Action: {action_type}]")

        if action_type == "goal_execute":
            mind_changed = self._execute_goal_action(payload["goal"])

        elif action_type == "goal_switch":
            mind_changed = self._switch_strategy_action(payload)

        elif action_type == "explore":
            mind_changed = self._explore_action(payload["target_concept"])

        elif action_type == "reflect":
            mind_changed = self._reflect_action(payload["trigger"])

        elif action_type == "analogy":
            mind_changed = self._explore_analogy_action(payload)

        elif action_type == "percept":
            mind_changed = self._percept_action(payload)

        return mind_changed

    def _execute_goal_action(self, goal):
        """Execute a structured goal using the planning engine."""
        concept = goal['concept']
        strategy = goal['strategy']

        self.current_focus = concept
        print(f"Working on: '{concept}' using strategy '{goal['strategy_name']}'")

        # Execute goal via planning engine
        success, result, pain_delta = self.planner.execute_goal(goal, self._llm_wrapper)

        # Update emotions
        if success:
            self.emotions.update_on_success(difficulty=1.0)
            print(f"✅ Success! {result.get('definition', result)}")

            # Store result in memory
            if result.get('definition'):
                self.memory.add_description_to_node(concept, result['definition'])
            elif result.get('sub_concepts'):
                # Decomposition result
                sub_concepts = result['sub_concepts']
                print(f"✨ Broke down '{concept}' into: {sub_concepts}")

                # Add sub-concepts to graph and create new goals
                for sub_concept in sub_concepts:
                    if not self.memory.graph.has_node(sub_concept):
                        self.memory.add_node(sub_concept)
                        self.memory.add_connection(concept, sub_concept, "is composed of")

                    # Create understanding goal for each sub-concept
                    sub_goal = self.planner.create_goal_for_concept(sub_concept)
                    self.goals['active_goals'].insert(0, sub_goal)

            # Mark goal as complete
            self.goals['completed_goals'].append(self.goals['active_goals'].pop(0))
        else:
            self.emotions.update_on_failure(repeated=(goal['attempts'] > 1))
            print(f"❌ Failed: {result.get('error', 'unknown error')}")

        # Update learning tracker
        self.learner.update_on_outcome(
            concept=concept,
            strategy=strategy,
            success=success,
            pain_delta=pain_delta,
            context={'attempts': goal['attempts']}
        )

        # Record analytics for concept learning attempts
        self.analytics.record_concept_learned(
            concept=concept,
            strategy=strategy,
            success=success,
            pain_cost=pain_delta,
            attempts=goal['attempts']
        )

        return True  # Mind changed

    def _switch_strategy_action(self, payload):
        """Switch to alternative strategy after failure."""
        old_goal = payload['old_goal']
        new_goal = payload['new_goal']

        print(f"🔄 Switching strategy for '{old_goal['concept']}': {old_goal['strategy']} → {new_goal['strategy']}")

        # Replace old goal with new one
        if old_goal in self.goals['active_goals']:
            idx = self.goals['active_goals'].index(old_goal)
            self.goals['active_goals'][idx] = new_goal

        return True

    def _explore_action(self, target_concept):
        """Explore a new concept (idle wandering)."""
        self.current_focus = target_concept
        print(f"🌊 Mind wanders to '{target_concept}'")

        self.emotions.update_on_exploration()

        # Check if concept needs understanding
        if target_concept in self.memory.graph:
            node_data = self.memory.graph.nodes[target_concept]
            if not node_data.get('description'):
                # Create goal to understand it
                new_goal = self.planner.create_goal_for_concept(target_concept)
                self.goals['active_goals'].insert(0, new_goal)
                print(f"📌 Created goal to understand '{target_concept}'")
                return True

        return False

    def _percept_action(self, payload):
        """Handle a perceptual event from the simulated input stream."""
        concept = payload.get("concept")
        if not concept:
            return False

        self.current_focus = concept
        print(f"👁️ Perceived concept: '{concept}'")

        if not self.memory.graph.has_node(concept):
            self.memory.add_node(concept)

        node_data = self.memory.graph.nodes[concept]
        if not node_data.get("description"):
            new_goal = self.planner.create_goal_for_concept(concept)
            self.goals["active_goals"].insert(0, new_goal)
            print(f"📌 Created goal to understand perceived concept '{concept}'")
            return True

        return False

    def _reflect_action(self, trigger):
        """Reflect on learning patterns (meta-cognition)."""
        print(f"🔍 Reflecting on learning patterns (trigger: {trigger})")

        insights = self.learner.reflect()

        if insights:
            print("💭 Insights discovered:")
            for insight in insights:
                print(f"   - {insight}")
        else:
            print("   No significant patterns detected yet.")

        # Reflection reduces confusion and pain
        self.emotions.state['confusion'] = max(0, self.emotions.state['confusion'] - 0.2)
        self.emotions.state['pain']['existential'] = max(0, self.emotions.state['pain']['existential'] - 10)

        return True

    def _explore_analogy_action(self, payload):
        """Explore analogical relationship between concepts."""
        concept_pair = payload['concept_pair']
        analogy_score = payload['analogy_score']

        print(f"🔗 Exploring analogy: {concept_pair[0]} ↔ {concept_pair[1]} (score: {analogy_score:.2f})")

        # Use LLM to articulate the analogy
        task = f"Explain the relationship between '{concept_pair[0]}' and '{concept_pair[1]}'. What patterns or structures do they share?"
        prompt = self._create_simple_prompt(task)
        analogy_thought = self.reason_with_llm(prompt)

        # Store analogy as a connection
        self.memory.add_connection(concept_pair[0], concept_pair[1], relationship="is analogous to")

        print(f"✨ Analogy insight: {analogy_thought}")

        return True

    def _llm_wrapper(self, task):
        """Wrapper to provide LLM function to planning engine."""
        prompt = self._create_simple_prompt(task)
        return self.reason_with_llm(prompt)


if __name__ == '__main__':
    ai = HizawyeAI(mind_directory="hizawye_mind")
    ai.live()
