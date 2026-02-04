"""
Emotional System: Multi-dimensional drive modeling for Hizawye AI.
Replaces simple 0-100 integers with complex, interacting emotional states.
"""
import json
import os
from log import setup_logger

logger = setup_logger()

class EmotionalSystem:
    def __init__(self, mind_directory="hizawye_mind"):
        self.mind_directory = mind_directory
        self.filepath = os.path.join(mind_directory, "emotional_state.json")

        # Multi-dimensional emotional state
        self.state = {
            'pain': {
                'physical': 0,        # Resource exhaustion, overload
                'existential': 0,     # Confusion about purpose/identity
                'frustration': 0      # Repeated failure on same task
            },
            'curiosity': {
                'epistemic': 80,      # Deep understanding seeking
                'diversive': 20,      # Novelty seeking
                'specific': 50        # Targeted interest in current focus
            },
            'boredom': {
                'understimulation': 0,  # Not enough activity
                'satiation': 0          # Too much of the same thing
            },
            'confidence': 0.5,        # Belief in own reasoning ability
            'confusion': 0.0          # Uncertainty about current understanding
        }

        self.load_state()

    def load_state(self):
        """Load emotional state from file."""
        try:
            with open(self.filepath, 'r') as f:
                loaded = json.load(f)
                self.state.update(loaded)
            logger.info("Emotional state loaded.")
        except FileNotFoundError:
            logger.info("No existing emotional state. Using defaults.")
            self.save_state()

    def save_state(self):
        """Save emotional state to file."""
        os.makedirs(self.mind_directory, exist_ok=True)
        with open(self.filepath, 'w') as f:
            json.dump(self.state, f, indent=4)

    def get_total_pain(self):
        """Compute aggregate pain level."""
        pain = self.state['pain']
        return sum(pain.values()) / 3.0

    def get_total_curiosity(self):
        """Compute aggregate curiosity level."""
        curiosity = self.state['curiosity']
        return sum(curiosity.values()) / 3.0

    def get_total_boredom(self):
        """Compute aggregate boredom level."""
        boredom = self.state['boredom']
        return sum(boredom.values()) / 2.0

    def compute_drive_vector(self):
        """
        Compute action priorities based on competing drives.
        Returns: dict with priority scores for different action types.
        """
        total_pain = self.get_total_pain()
        total_curiosity = self.get_total_curiosity()
        total_boredom = self.get_total_boredom()
        confidence = self.state['confidence']
        confusion = self.state['confusion']

        # Drive interactions
        exploration_drive = (
            self.state['curiosity']['diversive'] * 0.5 +
            total_boredom * 0.3 +
            (1.0 - confusion) * 0.2
        )

        focus_drive = (
            self.state['curiosity']['epistemic'] * 0.6 +
            self.state['curiosity']['specific'] * 0.4 -
            total_pain * 0.3
        )

        retreat_drive = total_pain * 0.7 + confusion * 0.3

        # Confidence modulates risk-taking
        exploration_temperature = 0.3 + (confidence * 0.4) - (confusion * 0.3)
        exploration_temperature = max(0.1, min(1.0, exploration_temperature))

        return {
            'exploration': exploration_drive,
            'focus': focus_drive,
            'retreat': retreat_drive,
            'temperature': exploration_temperature,
            'should_simplify': total_pain > 60 or confusion > 0.7,
            'should_explore': total_boredom > 70 or exploration_drive > 60
        }

    def modulate_llm_prompt(self, base_prompt, context_type='general'):
        """
        Modify LLM prompts based on emotional state.
        High confusion → request simpler explanations
        High confidence → attempt complex synthesis
        High frustration → take different angle
        """
        drives = self.compute_drive_vector()
        modulations = []

        if drives['should_simplify']:
            modulations.append("Explain in the simplest, most concrete terms possible.")

        if self.state['confusion'] > 0.6:
            modulations.append("Use analogies and examples to clarify.")

        if self.state['pain']['frustration'] > 50:
            modulations.append("Approach this from a completely different angle than before.")

        if self.state['confidence'] > 0.7 and context_type == 'synthesis':
            modulations.append("Attempt a sophisticated, nuanced synthesis.")

        if modulations:
            enhanced_prompt = base_prompt + "\n\nAdditional constraints: " + " ".join(modulations)
            return enhanced_prompt

        return base_prompt

    def update_on_success(self, difficulty=1.0):
        """Update emotional state after successful goal completion."""
        self.state['pain']['frustration'] = max(0, self.state['pain']['frustration'] - 20)
        self.state['confidence'] = min(1.0, self.state['confidence'] + 0.05 * difficulty)
        self.state['confusion'] = max(0, self.state['confusion'] - 0.1)
        self.state['boredom']['satiation'] = min(100, self.state['boredom']['satiation'] + 10)
        logger.info(f"Emotional update (success): confidence={self.state['confidence']:.2f}")

    def update_on_failure(self, repeated=False):
        """Update emotional state after goal failure."""
        if repeated:
            self.state['pain']['frustration'] = min(100, self.state['pain']['frustration'] + 25)
        else:
            self.state['pain']['existential'] = min(100, self.state['pain']['existential'] + 15)

        self.state['confidence'] = max(0.1, self.state['confidence'] - 0.1)
        self.state['confusion'] = min(1.0, self.state['confusion'] + 0.15)
        logger.info(f"Emotional update (failure): frustration={self.state['pain']['frustration']}")

    def update_on_exploration(self):
        """Update emotional state during idle exploration."""
        self.state['boredom']['understimulation'] = max(0, self.state['boredom']['understimulation'] - 15)
        self.state['curiosity']['diversive'] = min(100, self.state['curiosity']['diversive'] + 5)
        self.state['boredom']['satiation'] = min(100, self.state['boredom']['satiation'] + 3)

    def decay_emotions(self, cycles=1):
        """Natural decay of intense emotions over time."""
        decay_rate = 0.02 * cycles

        # Pain decays slowly
        for pain_type in self.state['pain']:
            self.state['pain'][pain_type] = max(0, self.state['pain'][pain_type] - decay_rate * 10)

        # Boredom decays with activity
        for boredom_type in self.state['boredom']:
            self.state['boredom'][boredom_type] = max(0, self.state['boredom'][boredom_type] - decay_rate * 5)

        # Confusion decays naturally
        self.state['confusion'] = max(0, self.state['confusion'] - decay_rate * 3)

    def get_status_summary(self):
        """Get human-readable emotional status."""
        drives = self.compute_drive_vector()
        total_pain = self.get_total_pain()

        status = []
        if total_pain > 60:
            status.append("experiencing significant pain")
        if self.state['confidence'] > 0.7:
            status.append("confident")
        elif self.state['confidence'] < 0.3:
            status.append("uncertain")
        if self.state['confusion'] > 0.6:
            status.append("confused")
        if drives['should_explore']:
            status.append("restless for novelty")

        return ", ".join(status) if status else "emotionally neutral"
