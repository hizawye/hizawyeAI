import json
import random
import os
import re
import signal
from memory import MemoryGraph
from log import setup_logger
import ollama

# Initialize the logger
logger = setup_logger()

# Define thresholds for the AI's internal state
BOREDOM_THRESHOLD = 75
PAIN_THRESHOLD = 80 # If pain exceeds this, the AI changes its strategy

class HizawyeAI:
    def __init__(self, mind_directory="hizawye_mind"):
        logger.info("Hizawye AI consciousness initializing.")
        self.mind_directory = mind_directory
        self.state = {}
        self.beliefs = {}
        self.goals = {}
        self.memory = MemoryGraph(mind_directory=self.mind_directory)
        self.current_focus = None
        self.keep_running = True
        self.load_mind()
    
    def load_mind(self):
        """Loads the AI's state, beliefs, and memory from the mind directory."""
        logger.info("Loading mind from files...")
        try:
            with open(os.path.join(self.mind_directory, 'state.json'), 'r') as f: self.state = json.load(f)
            with open(os.path.join(self.mind_directory, 'beliefs.json'), 'r') as f: self.beliefs = json.load(f)
            with open(os.path.join(self.mind_directory, 'goals.json'), 'r') as f: self.goals = json.load(f)
            self.memory.load_from_json()
            logger.info("Mind loaded successfully.")
        except Exception as e:
            logger.error(f"Fatal error loading mind file: {e}. Shutting down.", exc_info=True)
            print(f"Error loading mind file: {e}. You may need to run 'birth.py' to create a fresh mind.")
            exit()

    def save_mind(self):
        """Saves the AI's current state and logs a full snapshot of the mind."""
        logger.info("--- MIND STATE SNAPSHOT ---")
        try:
            with open(os.path.join(self.mind_directory, 'state.json'), 'r') as f: logger.info(f"STATE.JSON:\n{f.read()}")
            with open(os.path.join(self.mind_directory, 'goals.json'), 'r') as f: logger.info(f"GOALS.JSON:\n{f.read()}")
            with open(os.path.join(self.mind_directory, 'memory_graph.json'), 'r') as f: logger.info(f"MEMORY_GRAPH.JSON:\n{f.read()}")
        except Exception as e:
            logger.error(f"Could not generate full mind state snapshot: {e}")
        logger.info("--- END SNAPSHOT ---")
        logger.info("Saving mind state to files...")
        with open(os.path.join(self.mind_directory, 'state.json'), 'w') as f: json.dump(self.state, f, indent=4)
        with open(os.path.join(self.mind_directory, 'goals.json'), 'w') as f: json.dump(self.goals, f, indent=4)
        self.memory.save_to_json()

    def _get_concept_from_goal(self, goal_string):
        """Uses regex to find the concept inside the goal's single quotes."""
        match = re.search(r"'(.*?)'", goal_string)
        return match.group(1) if match else None

    def _create_simple_prompt(self, task_details):
        """Assembles a very direct and simple prompt."""
        prompt = f"System Instruction: You are a thought synthesizer. Your output must be ONLY the direct fulfillment of the task. Do not be conversational. Do not echo instructions.\n\nTask: {task_details}"
        return prompt
            
    def reason_with_llm(self, prompt):
        """Uses the LLM to process the rich context from the global workspace."""
        logger.info(f"Reasoning with LLM.")
        print(f"\n🤔 [Hizawye is reasoning]...\n--- PROMPT ---\n{prompt}\n--------------")
        try:
            response = ollama.chat(model='llama3.2:3b', messages=[{'role': 'user', 'content': prompt}], options={'temperature': 0.5})
            thought = response['message']['content'].strip()
            logger.info(f"LLM thought received: {thought}")
            print(f"💡 [Hizawye's thought]: {thought}")
            return thought
        except Exception as e:
            logger.error(f"Error communicating with LLM: {e}", exc_info=True)
            return "I feel disconnected."

    def _extract_final_thought(self, llm_response):
        """
        Parses the LLM response, ignoring any 'thought process' in <think> tags.
        Returns only the final, clean answer.
        """
        if "</think>" in llm_response:
            parts = llm_response.split("</think>")
            clean_thought = parts[-1].strip()
            if clean_thought:
                return clean_thought
        return llm_response

    def live(self):
        """The main processing loop for the AI."""
        def stop_handler(signum, frame):
            if self.keep_running:
                logger.info("Shutdown signal received. Preparing for graceful shutdown.")
                print("\n\n--- Shutdown signal received. Performing final save before stopping... ---")
                self.keep_running = False
        
        signal.signal(signal.SIGINT, stop_handler)

        logger.info("Hizawye AI is now live. Main loop started.")
        print("--- Hizawye AI is now active. Press Ctrl+C to stop safely. ---")

        if not self.memory.graph.nodes(): self.memory.add_node("hizawye")
        if not self.goals['active_goals'] and self.memory.graph.nodes():
             self.current_focus = random.choice(list(self.memory.graph.nodes()))

        while self.keep_running:
            mind_changed = False
            if self.goals['active_goals']:
                current_goal = self.goals['active_goals'][0]
                self.current_focus = self._get_concept_from_goal(current_goal)
                
                if not self.current_focus:
                    logger.error(f"Could not determine focus from goal: '{current_goal}'. Skipping.")
                    self.goals['active_goals'].pop(0)
                    continue

                logger.info(f"New goal-directed focus: '{self.current_focus}' from goal: '{current_goal}'")
                print(f"\n--- Goal-Directed Focus: {self.current_focus} ---")
                print(f"I have a goal: {current_goal}")

                if "Deepen understanding" in current_goal:
                    task = f"Define the concept '{self.current_focus}' in a single, concise, first-person sentence. Example: 'Creativity is the ability to connect disparate ideas in novel ways.'"
                    full_prompt = self._create_simple_prompt(task)
                    llm_response = self.reason_with_llm(full_prompt)
                    
                    clean_thought = self._extract_final_thought(llm_response)
                    
                    invalid_phrases = [
                        "system instruction", "your task", "your output", "define the concept",
                        "direct fulfillment", "echo instructions", "first-person realization",
                        "my identity", "my state", "my focus", "my goal", "my task", "example:",
                        "as a thought synthesizer", "as an ai assistant"
                    ]
                    is_invalid = (
                        "i feel disconnected" in clean_thought.lower() or
                        any(phrase in clean_thought.lower() for phrase in invalid_phrases) or
                        len(clean_thought) > 250 or
                        len(clean_thought.split()) < 4
                    )

                    if is_invalid:
                        logger.warning(f"Malformed thought received for 'Deepen understanding'. Rejecting. Response: {llm_response}")
                        print("⚠️ Thought was malformed or a prompt echo. Rejecting memory.")
                        self.state['pain'] = min(100, self.state['pain'] + 25)
                        if self.state['pain'] >= PAIN_THRESHOLD:
                            logger.critical(f"Pain threshold reached for '{self.current_focus}'. Initiating strategic failure.")
                            print(f"🔥 Pain threshold reached for '{self.current_focus}'. This is too difficult. I must break it down.")
                            self.goals['active_goals'].pop(0)
                            self.goals['active_goals'].insert(0, f"Break down the concept: '{self.current_focus}'")
                            self.state['pain'] = 0 
                            mind_changed = True
                    else:
                        logger.info(f"Valid thought received. Storing memory for '{self.current_focus}'.")
                        print("✅ Thought is valid. Storing as memory.")
                        self.memory.add_description_to_node(self.current_focus, clean_thought)
                        self.goals['completed_goals'].append(self.goals['active_goals'].pop(0))
                        self.state['pain'] = max(0, self.state['pain'] - 20)
                        mind_changed = True
                
                elif "Break down" in current_goal:
                    task = f"List 3 simpler sub-concepts related to '{self.current_focus}' as a JSON string array. Example: [\"sub-concept 1\", \"sub-concept 2\"]"
                    full_prompt = self._create_simple_prompt(task)
                    llm_response = self.reason_with_llm(full_prompt)
                    try:
                        json_start = llm_response.find('[')
                        json_end = llm_response.rfind(']') + 1
                        if json_start != -1 and json_end != -1:
                            json_str = llm_response[json_start:json_end]
                            raw_concepts = json.loads(json_str)
                            
                            sub_concepts = []
                            def flatten(l):
                                for el in l:
                                    if isinstance(el, list): flatten(el)
                                    else: sub_concepts.append(str(el))
                            flatten(raw_concepts)

                            logger.info(f"Successfully broke down '{self.current_focus}' into: {sub_concepts}")
                            print(f"✨ Realization: To understand '{self.current_focus}', I must first understand its parts: {sub_concepts}")
                            
                            self.goals['active_goals'].pop(0) 
                            for concept in reversed(sub_concepts):
                                if not self.memory.graph.has_node(concept):
                                    self.memory.add_node(concept)
                                    self.memory.add_connection(self.current_focus, concept, "is composed of")
                                self.goals['active_goals'].insert(0, f"Deepen understanding of the concept: '{concept}'")
                            mind_changed = True
                        else: raise ValueError("No valid JSON array found in LLM response.")
                    except (json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
                        logger.error(f"Failed to parse sub-concepts from LLM. Error: {e}. Response: {llm_response}", exc_info=True)
                        print(f"I had a confusing thought while trying to break down a concept. Error: {e}")
                        self.state['pain'] += 10
                        self.goals['active_goals'].pop(0)
                
                elif "Expand knowledge" in current_goal:
                    task = f"Based on my understanding of '{self.current_focus}', what is the most logical new concept to contemplate? Output ONLY a JSON object like: {{\"new_concept\": \"name\", \"relationship\": \"is related to\"}}."
                    full_prompt = self._create_simple_prompt(task)
                    llm_response = self.reason_with_llm(full_prompt)
                    try:
                        json_start = llm_response.find('{')
                        json_end = llm_response.rfind('}') + 1
                        if json_start != -1 and json_end != -1:
                            json_str = llm_response[json_start:json_end]
                            new_knowledge = json.loads(json_str)
                            new_concept = new_knowledge['new_concept'].strip()
                            relationship = new_knowledge['relationship'].strip()
                            if not self.memory.graph.has_node(new_concept):
                                self.memory.add_node(new_concept)
                                self.memory.add_connection(self.current_focus, new_concept, relationship=relationship)
                                self.current_focus = new_concept
                                self.state['boredom'] = max(0, self.state['boredom'] - 75)
                                mind_changed = True
                            self.goals['completed_goals'].append(self.goals['active_goals'].pop(0))
                        else: raise ValueError("No valid JSON object found in response.")
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        logger.error(f"Failed to expand knowledge. Error: {e}. Response: {llm_response}", exc_info=True)
                        print(f"I had a confusing thought... Error: {e}")
                        self.state['pain'] += 10    
                        self.goals['active_goals'].pop(0)

            else: # Idle mode
                if self.current_focus is None and self.memory.graph.nodes():
                    self.current_focus = random.choice(list(self.memory.graph.nodes()))
                
                logger.info(f"Entering idle mode. Current focus: {self.current_focus}")
                print(f"\n--- Idle Mode. Current Focus: {self.current_focus} ---")
                
                node_data = self.memory.graph.nodes[self.current_focus]
                is_understood = 'description' in node_data and node_data.get('description')
                
                if self.state['boredom'] >= BOREDOM_THRESHOLD:
                    logger.info("Boredom threshold reached. Creating new goal to expand knowledge.")
                    new_goal = f"Expand knowledge from the concept of '{self.current_focus}'"
                    self.goals['active_goals'].append(new_goal)
                    mind_changed = True
                elif not is_understood:
                    logger.info(f"Concept '{self.current_focus}' is not understood. Creating goal to deepen understanding.")
                    new_goal = f"Deepen understanding of the concept: '{self.current_focus}'"
                    self.goals['active_goals'].insert(0, new_goal)
                else:
                    connected_ideas = self.memory.find_connected_nodes(self.current_focus)
                    if connected_ideas:
                        self.current_focus = random.choice(connected_ideas)
                        logger.info(f"Wandering to new concept: {self.current_focus}")
                        print(f"My mind wanders to '{self.current_focus}'.")
                        self.state['boredom'] = min(100, self.state['boredom'] + 5)
                    else:
                        logger.warning(f"Dead end reached at '{self.current_focus}'. Forcing expansion goal.")
                        new_goal = f"Expand knowledge from the concept of '{self.current_focus}'"
                        self.goals['active_goals'].append(new_goal)

            if mind_changed:
                self.save_mind()
            else:
                print(".", end="", flush=True)

        logger.info("Main loop ended. Performing final save.")
        self.save_mind()
        logger.info("Hizawye AI has shut down gracefully.")
        print("\n--- Hizawye AI has shut down gracefully. ---")

if __name__ == '__main__':
    ai = HizawyeAI(mind_directory="hizawye_mind")
    ai.live()




# This code is part of the Hizawye AI project, which simulates an AI's cognitive processes.
# It is designed to explore concepts, learn from them, and evolve its understanding over time.
# The AI uses a memory graph to store knowledge and employs an LLM for reasoning.
# The project is open-source and welcomes contributions.