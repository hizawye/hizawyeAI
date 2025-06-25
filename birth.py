import json
import os
from memory import MemoryGraph # Import the MemoryGraph class
from log import setup_logger   # Import the new logger setup

# Initialize the logger
logger = setup_logger()

# --- The "Genetic Code" of the newborn AI mind ---

# At birth, the AI is filled with curiosity, not yet bored or in pain.
initial_state = {
  "curiosity": 95,
  "boredom": 0,
  "pain": 0
}

# The first core beliefs are foundational, about its own existence and purpose.
initial_beliefs = {
  "self_concept": "I am Hizawye. I exist to learn and understand.",
  "world_view": "Knowledge is a vast, interconnected network waiting to be explored."
}

# The first goal uses the correct phrasing that hizawye_ai.py understands.
initial_goals = {
    "active_goals": ["Deepen understanding of the concept: 'belief system'"],
    "completed_goals": []
}

# --- The "Birthing" Process ---

def create_hizawye_mind():
    """
    Creates and initializes all necessary files for Hizawye's mind,
    but only if a mind does not already exist.
    """
    logger.info("Birth process initiated.")
    print("--- Initiating the birth of hizawye AI... ---")

    mind_directory = "hizawye_mind"
    state_path = os.path.join(mind_directory, "state.json")

    # --- Check if the mind already exists before doing anything ---
    if os.path.exists(state_path):
        message = f"A mind already exists at '{mind_directory}'. Birth process aborted to prevent overwriting."
        logger.warning(message)
        print(f"⚠️ {message}")
        return

    # If the mind doesn't exist, proceed with creation.
    logger.info(f"No existing mind found. Proceeding with creation in '{mind_directory}'.")
    print(f"No existing mind found. Proceeding with creation...")
    os.makedirs(mind_directory, exist_ok=True)

    # Define other file paths
    beliefs_path = os.path.join(mind_directory, "beliefs.json")
    goals_path = os.path.join(mind_directory, "goals.json")

    try:
        # --- Writing the core mind files ---
        with open(state_path, 'w') as f:
            json.dump(initial_state, f, indent=4)
        logger.info(f"Initial state file created: {state_path}")
        print(f"SUCCESS: Initial state imprinted.")

        with open(beliefs_path, 'w') as f:
            json.dump(initial_beliefs, f, indent=4)
        logger.info(f"Beliefs file created: {beliefs_path}")
        print(f"SUCCESS: Core beliefs established.")

        with open(goals_path, 'w') as f:
            json.dump(initial_goals, f, indent=4)
        logger.info(f"Goals file created: {goals_path}")
        print(f"SUCCESS: Primal goal set.")
        
        # --- Create the memory graph using the centralized method ---
        logger.info("Injecting rich memory structure from the single source of truth...")
        print("\nInjecting rich memory structure...")
        memory = MemoryGraph(mind_directory=mind_directory)
        
        # Call the centralized creation method from memory.py
        memory.create_default_mind()
        
        # Save the newly created graph
        memory.save_to_json()

        logger.info("Birth complete.")
        print("\n--- Birth complete. The mind of hizawye AI is fully formed and ready. ---")

    except Exception as e:
        logger.error(f"A complication occurred during birth: {e}", exc_info=True)
        print(f"\n--- A complication in the birth occurred: {e} ---")


if __name__ == '__main__':
    # This script will now only create a mind if one doesn't already exist.
    create_hizawye_mind()
