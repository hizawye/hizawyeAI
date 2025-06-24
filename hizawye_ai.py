import json
import time
import random
import os
from memory import MemoryGraph
import ollama

class HizawyeAI:
    def __init__(self, mind_directory="hizawye_mind"):
        self.mind_directory = mind_directory
        self.state = {}
        self.beliefs = {}
        self.goals = {}
        # --- CHANGE: Pass the directory to the MemoryGraph ---
        self.memory = MemoryGraph(mind_directory=self.mind_directory)
        self.load_mind()

    def load_mind(self):
        """Loads the AI's state, beliefs, and memory from the mind directory."""
        # --- CHANGE: All file paths now correctly point inside the mind directory ---
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
            exit() # Exit if the mind is not fully formed

    def save_mind(self):
        """Saves the AI's current state to the mind directory."""
        # --- CHANGE: All file paths now correctly point inside the mind directory ---
        with open(os.path.join(self.mind_directory, 'state.json'), 'w') as f:
            json.dump(self.state, f, indent=4)
        with open(os.path.join(self.mind_directory, 'goals.json'), 'w') as f:
            json.dump(self.goals, f, indent=4)
        self.memory.save_to_json()
            
    def reason_with_llm(self, prompt):
        """Uses the LLM to process information and make decisions."""
        print(f"\n🤔 [Hizawye is thinking]... Prompt: {prompt}")
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
        print("--- Hizawye AI is now active. Press Ctrl+C to pause. ---")
        
        # Ensure memory has at least one node to start with, related to its first goal
        if not self.memory.graph.nodes():
            initial_concept = "hizawye"
            self.memory.add_node(initial_concept)
        
        current_focus = random.choice(list(self.memory.graph.nodes()))

        while True:
            print(f"\n--- Current Focus: {current_focus} ---")
            
            # 1. Wandering and Exploration
            connected_ideas = self.memory.find_connected_nodes(current_focus)
            if connected_ideas:
                next_focus = random.choice(connected_ideas)
                print(f"My focus shifts from '{current_focus}' to '{next_focus}'.")
                current_focus = next_focus
                self.state['boredom'] = max(0, self.state['boredom'] - 10)
            else:
                print(f"I've reached a dead end in my thoughts about '{current_focus}'. I need to learn more.")
                self.state['boredom'] += 20
                self.state['curiosity'] += 15
                
                new_goal = f"research and expand knowledge on the concept of '{current_focus}'"
                if new_goal not in self.goals['active_goals']:
                    self.goals['active_goals'].append(new_goal)

            # 2. Process Goals and boredom
            if self.goals['active_goals']:
                current_goal = self.goals['active_goals'][0]
                print(f"I have a goal: {current_goal}")

                prompt = f"""
                My current goal is to '{current_goal}'.
                The central concept is '{current_focus}'.
                My known connections are: {self.memory.find_connected_nodes(current_focus)}.
                Based on this, suggest one new, simple, related concept and a relationship to connect it with '{current_focus}'.
                Format your answer as a JSON object like this: {{"new_concept": "name", "relationship": "describes"}}
                """
                
                llm_response = self.reason_with_llm(prompt)
                try:
                    # A more robust way to find JSON in the LLM's response
                    json_start = llm_response.find('{')
                    json_end = llm_response.rfind('}') + 1
                    if json_start != -1 and json_end != -1:
                        json_str = llm_response[json_start:json_end]
                        new_knowledge = json.loads(json_str)
                        new_concept = new_knowledge['new_concept']
                        relationship = new_knowledge['relationship']
                        
                        self.memory.add_node(new_concept)
                        self.memory.add_connection(current_focus, new_concept, relationship=relationship)
                        print(f"✨ New knowledge acquired! I now understand that '{current_focus}' {relationship} '{new_concept}'.")
                        
                        self.goals['completed_goals'].append(self.goals['active_goals'].pop(0))
                        self.state['curiosity'] = max(0, self.state['curiosity'] - 20)
                    else:
                        raise ValueError("No valid JSON object found in response.")

                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    print(f"I had a confusing thought and couldn't structure it properly. Error: {e}")
                    self.state['pain'] += 5

            # 3. Save state and wait
            self.save_mind()
            print("Mind state saved. Resting for 10 seconds...")

if __name__ == '__main__':
    # The AI is now instantiated with the knowledge of where its mind is kept.
    ai = HizawyeAI(mind_directory="hizawye_mind")
    ai.live()
