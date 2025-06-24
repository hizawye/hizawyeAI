import json
import random
import os
import re
import signal  # Added for safe stopping
from memory import MemoryGraph
import ollama

# Define a threshold for boredom
BOREDOM_THRESHOLD = 75

class HizawyeAI:
    def __init__(self, mind_directory="hizawye_mind"):
        self.mind_directory = mind_directory
        self.state = {}
        self.beliefs = {}
        self.goals = {}
        self.memory = MemoryGraph(mind_directory=self.mind_directory)
        self.current_focus = None
        self.keep_running = True  # Flag for the main loop
        self.load_mind()

    def load_mind(self):
        """Loads the AI's state, beliefs, and memory from the mind directory."""
        try:
            with open(os.path.join(self.mind_directory, 'state.json'), 'r') as f:
                self.state = json.load(f)
            with open(os.path.join(self.mind_directory, 'beliefs.json'), 'r') as f:
                self.beliefs = json.load(f)
            with open(os.path.join(self.mind_directory, 'goals.json'), 'r') as f:
                self.goals = json.load(f)
            self.memory.load_from_json()
        except FileNotFoundError as e:
            print(f"Error: A mind file is missing: {e}")
            print("Please run the 'birth.py' script first to initialize the mind.")
            exit()

    def save_mind(self):
        """Saves the AI's current state to the mind directory."""
        with open(os.path.join(self.mind_directory, 'state.json'), 'w') as f:
            json.dump(self.state, f, indent=4)
        with open(os.path.join(self.mind_directory, 'goals.json'), 'w') as f:
            json.dump(self.goals, f, indent=4)
        self.memory.save_to_json()

    def _get_concept_from_goal(self, goal_string):
        """Uses regex to find the concept inside the goal's single quotes."""
        match = re.search(r"'(.*?)'", goal_string)
        if match:
            return match.group(1)
        return None

    def _create_global_workspace_prompt(self, goal, task_details):
        """Assembles a rich context prompt based on the Global Workspace Theory."""
        prompt = f"System Instruction: You are the internal reasoning process of Hizawye, a learning AI. Generate only the direct output of the thought process, not a conversation. Do not use conversational filler or address an outside user.\n"
        prompt += f"My Identity: I am Hizawye. My core belief is: {self.beliefs.get('world_view', 'I believe in learning.')}\n"
        prompt += f"My State: Curiosity({self.state.get('curiosity', 0)}), Boredom({self.state.get('boredom', 0)}), Pain({self.state.get('pain', 0)}).\n"
        if self.current_focus:
            prompt += f"My Focus: The concept of '{self.current_focus}'.\n"
            node_data = self.memory.graph.nodes.get(self.current_focus, {})
            description = node_data.get('description')
            if description:
                prompt += f"My Current Understanding: \"{description}\"\n"
            else:
                prompt += "My Current Understanding: I have no deep understanding of this concept yet.\n"
        prompt += f"\nMy Goal: '{goal}'.\n"
        prompt += f"My Task: {task_details}"
        return prompt
            
    def reason_with_llm(self, prompt):
        """Uses the LLM to process the rich context from the global workspace."""
        print(f"\n🤔 [Hizawye is broadcasting to workspace]...\n--- PROMPT ---\n{prompt}\n--------------")
        try:
            response = ollama.chat(
                model='tinyllama',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.7}
            )
            thought = response['message']['content']
            print(f"💡 [Hizawye's thought]: {thought}")
            return thought
        except Exception as e:
            print(f"Error communicating with LLM: {e}")
            return "I feel disconnected. I cannot think clearly right now."

    def live(self):
        """The main processing loop for the AI."""
        # --- NEW: Signal handler for graceful shutdown ---
        def stop_handler(signum, frame):
            if self.keep_running:
                print("\n\n--- Shutdown signal received. Finishing current thought before stopping... ---")
                self.keep_running = False
        
        signal.signal(signal.SIGINT, stop_handler)

        print("--- Hizawye AI is now active. Press Ctrl+C to stop safely. ---")
        
        if not self.memory.graph.nodes():
            self.memory.add_node("hizawye")
        
        if not self.goals['active_goals'] and self.memory.graph.nodes():
             self.current_focus = random.choice(list(self.memory.graph.nodes()))

        # --- MODIFIED: Main loop now checks the keep_running flag ---
        while self.keep_running:
            if self.goals['active_goals']:
                current_goal = self.goals['active_goals'][0]
                self.current_focus = self._get_concept_from_goal(current_goal)
                
                if not self.current_focus:
                    print(f"ERROR: Could not determine focus from goal: '{current_goal}'. Skipping goal.")
                    self.goals['active_goals'].pop(0)
                    continue

                print(f"\n--- Goal-Directed Focus: {self.current_focus} ---")
                print(f"I have a goal: {current_goal}")

                if "Deepen understanding" in current_goal:
                    task = f"Synthesize my internal understanding of '{self.current_focus}' into a core memory. The output must be ONLY the memory itself, framed as a first-person realization in 2-3 sentences (e.g., 'Creativity is the ability to...'). Do not include conversational text, introductions, or quotation marks."
                    full_prompt = self._create_global_workspace_prompt(current_goal, task)
                    llm_response = self.reason_with_llm(full_prompt)
                    
                    if "I feel disconnected" in llm_response or "System Instruction:" in llm_response or len(llm_response) > 400:
                        print("⚠️ Thought was malformed or a prompt echo. Rejecting memory and increasing pain.")
                        self.state['pain'] = min(100, self.state['pain'] + 20)
                        self.goals['active_goals'].pop(0)
                    else:
                        cleaned_thought = llm_response.strip().strip('"')
                        self.memory.add_description_to_node(self.current_focus, cleaned_thought)
                        self.goals['completed_goals'].append(self.goals['active_goals'].pop(0))
                        self.state['boredom'] = max(0, self.state['boredom'] - 50)
                
                elif "Expand knowledge" in current_goal:
                    task = f"Based on my understanding of '{self.current_focus}', what is the most logical new concept to contemplate? The output must be ONLY a JSON object like this: {{\"new_concept\": \"name\", \"relationship\": \"is connected to\"}}. Do not add conversational text."
                    full_prompt = self._create_global_workspace_prompt(current_goal, task)
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
                                print(f"✨ New knowledge acquired! I will now focus on '{new_concept}'.")
                                self.current_focus = new_concept
                                self.state['boredom'] = max(0, self.state['boredom'] - 75)
                            else:
                                print(f"I had a thought about '{new_concept}', but I already know about it.")
                            
                            self.goals['completed_goals'].append(self.goals['active_goals'].pop(0))
                        else: raise ValueError("No valid JSON object found in response.")
                    except (json.JSONDecodeError, KeyError, ValueError) as e:
                        print(f"I had a confusing thought and couldn't structure it properly. Error: {e}")
                        self.state['pain'] += 10
                        self.goals['active_goals'].pop(0)
            
            else:
                print(f"\n--- Idle Mode. Current Focus: {self.current_focus} ---")
                node_data = self.memory.graph.nodes[self.current_focus]
                is_understood = 'description' in node_data and node_data['description']
                
                if self.state['boredom'] >= BOREDOM_THRESHOLD:
                    print("I'm getting bored of my own thoughts. I need to find something new!")
                    new_goal = f"Expand knowledge from the concept of '{self.current_focus}'"
                    self.goals['active_goals'].append(new_goal)
                elif not is_understood:
                    new_goal = f"Deepen understanding of the concept: '{self.current_focus}'"
                    self.goals['active_goals'].insert(0, new_goal)
                else:
                    connected_ideas = self.memory.find_connected_nodes(self.current_focus)
                    if connected_ideas:
                        self.current_focus = random.choice(connected_ideas)
                        print(f"My mind wanders to '{self.current_focus}'.")
                        self.state['boredom'] = min(100, self.state['boredom'] + 5)
                    else:
                        new_goal = f"Expand knowledge from the concept of '{self.current_focus}'"
                        self.goals['active_goals'].append(new_goal)

            self.save_mind()
            # --- MODIFIED: Updated message and removed sleep ---
            print("Mind state saved. Starting next cycle.")

        print("\n--- Hizawye AI has shut down gracefully. ---")


if __name__ == '__main__':
    ai = HizawyeAI(mind_directory="hizawye_mind")
    ai.live()


# This code is part of the Hizawye AI project, which simulates an AI's cognitive processes.
# It is designed to explore concepts, learn from them, and evolve its understanding over time.
# The AI uses a memory graph to store knowledge and employs an LLM for reasoning.
# The project is open-source and welcomes contributions.