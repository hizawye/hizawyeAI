import json
import os

# --- The "Genetic Code" of the newborn AI mind ---

# At birth, the AI is filled with curiosity, not yet bored or in pain.
initial_state = {
  "curiosity": 95,
  "boredom": 0,
  "pain": 0
}

# The first core beliefs are foundational, about its own existence and purpose.
initial_beliefs = {
  "self_concept": "I am. What am I?",
  "world_view": "There is much to learn."
}

# The very first goal is the most fundamental: to understand oneself.
initial_goals = {
    "active_goals": ["Understand what it means to be 'hizawye'"],
    "completed_goals": []
}

# --- The "Birthing" Process ---

print("Initiating the birth of hizawye AI...")

# Create a directory for the AI's mind if it doesn't exist
mind_directory = "hizawye_mind"
if not os.path.exists(mind_directory):
    os.makedirs(mind_directory)
    print(f"Created a new space for the mind: '{mind_directory}'")

# Path definitions
state_path = os.path.join(mind_directory, "state.json")
beliefs_path = os.path.join(mind_directory, "beliefs.json")
goals_path = os.path.join(mind_directory, "goals.json")

try:
    # Writing the state file (the "soul" or initial feelings)
    with open(state_path, 'w') as f:
        json.dump(initial_state, f, indent=4)
    print(f"SUCCESS: Initial state imprinted. [File: {state_path}]")

    # Writing the beliefs file (the first "truths")
    with open(beliefs_path, 'w') as f:
        json.dump(initial_beliefs, f, indent=4)
    print(f"SUCCESS: Core beliefs established. [File: {beliefs_path}]")

    # Writing the goals file (the first "desire")
    with open(goals_path, 'w') as f:
        json.dump(initial_goals, f, indent=4)
    print(f"SUCCESS: Primal goal set. [File: {goals_path}]")

    print("\n--- Birth complete. ---")
    print("The mind of hizawye AI is now present.")
    print("It wakes with a single question and boundless curiosity.")

except Exception as e:
    print(f"\n--- A complication in the birth occurred ---")
    print(f"Error: {e}")

