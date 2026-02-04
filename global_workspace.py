"""
Global Workspace: Parallel thought competition system.
Implements Global Workspace Theory - consciousness emerges from competition
between multiple parallel thought processes.
"""
import asyncio
from abc import ABC, abstractmethod
from log import setup_logger

logger = setup_logger()

class ThoughtThread(ABC):
    """
    Abstract base class for parallel thought processes.
    Each thread generates proposals for what to think/do next.
    """
    def __init__(self, name, priority_base=1.0):
        self.name = name
        self.priority_base = priority_base
        self.last_broadcast = None

    @abstractmethod
    async def generate_proposal(self, context) -> 'Proposal | None':
        """
        Generate a proposal for what action to take.
        Returns: Proposal object or None
        """
        pass

    def observe_broadcast(self, winning_proposal):
        """
        Observe the winning proposal from the global workspace.
        This allows threads to update their internal state based on
        what the "conscious" mind is doing.
        """
        self.last_broadcast = winning_proposal


class Proposal:
    """
    A proposed action from a thought thread.
    Proposals compete to become the conscious thought/action.
    """
    def __init__(self, source_thread, action_type, priority, payload=None):
        self.source = source_thread
        self.action_type = action_type  # 'goal_directed', 'explore', 'reflect', etc.
        self.priority = priority  # Urgency × confidence × emotional alignment
        self.payload = payload  # Action-specific data


class GoalDirectedThread(ThoughtThread):
    """
    Focuses on achieving active goals.
    High priority when goals exist, low when idle.
    """
    def __init__(self, planner, emotions):
        super().__init__("GoalDirected", priority_base=1.5)
        self.planner = planner
        self.emotions = emotions
        self.current_goal = None

    async def generate_proposal(self, context):
        """Generate proposal to work on active goal."""
        goals = context.get('active_goals', [])

        if not goals:
            return None  # No goals, this thread is silent

        # Get first active goal
        self.current_goal = goals[0]

        # Check if we should retreat from current goal
        if self.planner.should_retreat(self.current_goal):
            # Propose switching strategies
            alternative = self.planner.generate_alternative_goal(self.current_goal)
            priority = 0.8  # High but not urgent
            logger.info(f"[{self.name}] Proposing strategy switch for '{self.current_goal['concept']}'")
            return Proposal(
                source_thread=self.name,
                action_type='switch_strategy',
                priority=priority,
                payload={'old_goal': self.current_goal, 'new_goal': alternative}
            )

        # Propose executing current goal
        drives = self.emotions.compute_drive_vector()
        focus_drive = drives['focus']
        confidence = self.emotions.state['confidence']

        # Priority = focus drive × confidence
        priority = (focus_drive / 100.0) * confidence * self.priority_base

        logger.info(f"[{self.name}] Proposing goal execution: '{self.current_goal['concept']}' (priority={priority:.2f})")
        return Proposal(
            source_thread=self.name,
            action_type='execute_goal',
            priority=priority,
            payload={'goal': self.current_goal}
        )


class IdleWanderingThread(ThoughtThread):
    """
    Explores memory graph when bored or curious.
    Low priority when focused, high when idle.
    """
    def __init__(self, memory, emotions):
        super().__init__("IdleWandering", priority_base=0.8)
        self.memory = memory
        self.emotions = emotions

    async def generate_proposal(self, context):
        """Generate proposal to explore memory."""
        drives = self.emotions.compute_drive_vector()
        current_focus = context.get('current_focus')

        # Should we explore?
        if not drives['should_explore'] and context.get('active_goals'):
            return None  # Quiet when focused and not bored

        # Find interesting exploration target
        target = self.memory.find_exploration_target(current_focus, avoid_recent=True)

        if not target:
            return None

        # Priority = exploration drive × boredom
        exploration_drive = drives['exploration']
        boredom = self.emotions.get_total_boredom()

        priority = ((exploration_drive + boredom) / 200.0) * self.priority_base

        logger.info(f"[{self.name}] Proposing exploration of '{target}' (priority={priority:.2f})")
        return Proposal(
            source_thread=self.name,
            action_type='explore',
            priority=priority,
            payload={'target_concept': target}
        )


class MetaCognitionThread(ThoughtThread):
    """
    Reflects on learning patterns and strategy effectiveness.
    Triggers periodically or when pain is high.
    """
    def __init__(self, learner, emotions):
        super().__init__("MetaCognition", priority_base=0.6)
        self.learner = learner
        self.emotions = emotions
        self.cycles_since_reflection = 0
        self.reflection_interval = 15  # Reflect every N cycles

    async def generate_proposal(self, context):
        """Generate proposal to reflect on learning."""
        self.cycles_since_reflection += 1

        total_pain = self.emotions.get_total_pain()
        confusion = self.emotions.state['confusion']

        # Trigger reflection if:
        # 1. High pain/confusion (need to understand what's wrong)
        # 2. Periodic interval reached
        should_reflect = (
            total_pain > 70 or
            confusion > 0.7 or
            self.cycles_since_reflection >= self.reflection_interval
        )

        if not should_reflect:
            return None

        # Priority increases with pain/confusion
        urgency = (total_pain + confusion * 100) / 200.0
        priority = urgency * self.priority_base

        logger.info(f"[{self.name}] Proposing reflection (priority={priority:.2f})")
        return Proposal(
            source_thread=self.name,
            action_type='reflect',
            priority=priority,
            payload={'trigger': 'pain' if total_pain > 70 else 'periodic'}
        )

    def observe_broadcast(self, winning_proposal):
        """Reset counter if reflection wins."""
        super().observe_broadcast(winning_proposal)
        if winning_proposal and winning_proposal.action_type == 'reflect':
            self.cycles_since_reflection = 0


class PatternRecognitionThread(ThoughtThread):
    """
    Identifies analogies and patterns in memory graph.
    Helps connect disparate concepts.
    """
    def __init__(self, memory, emotions):
        super().__init__("PatternRecognition", priority_base=0.5)
        self.memory = memory
        self.emotions = emotions
        self.last_pattern_check = 0

    async def generate_proposal(self, context):
        """Generate proposal to find patterns/analogies."""
        self.last_pattern_check += 1

        # Only check patterns occasionally (computationally expensive)
        if self.last_pattern_check < 10:
            return None

        self.last_pattern_check = 0

        current_focus = context.get('current_focus')
        if not current_focus or current_focus not in self.memory.graph:
            return None

        # Look for analogies in working memory
        working_memory = self.memory.get_working_memory_concepts()
        if len(working_memory) < 2:
            return None

        # Find best analogy candidate
        best_analogy_score = 0.0
        best_pair = None

        for concept in working_memory[:5]:  # Check top 5 recent concepts
            if concept == current_focus:
                continue
            score, _ = self.memory.find_analogies(current_focus, concept)
            if score > best_analogy_score:
                best_analogy_score = score
                best_pair = (current_focus, concept)

        if best_analogy_score < 0.3:  # Threshold for interesting analogies
            return None

        # Priority based on analogy strength and curiosity
        curiosity = self.emotions.state['curiosity']['epistemic']
        priority = (best_analogy_score * 0.6 + curiosity / 100.0 * 0.4) * self.priority_base

        logger.info(f"[{self.name}] Proposing analogy exploration: {best_pair} (score={best_analogy_score:.2f})")
        return Proposal(
            source_thread=self.name,
            action_type='explore_analogy',
            priority=priority,
            payload={'concept_pair': best_pair, 'analogy_score': best_analogy_score}
        )


class GlobalWorkspace:
    """
    Central coordinator for parallel thought processes.
    Implements consciousness as winner-take-all competition.
    """
    def __init__(self, memory, emotions, learner, planner):
        self.memory = memory
        self.emotions = emotions
        self.learner = learner
        self.planner = planner

        # Initialize thought threads
        self.threads = [
            GoalDirectedThread(planner, emotions),
            IdleWanderingThread(memory, emotions),
            MetaCognitionThread(learner, emotions),
            PatternRecognitionThread(memory, emotions)
        ]

        self.current_context = {}
        self.last_winner = None

    def update_context(self, **kwargs):
        """Update the global context available to all threads."""
        self.current_context.update(kwargs)

    async def cycle(self):
        """
        Single consciousness cycle:
        1. All threads generate proposals in parallel
        2. Score and select winner
        3. Broadcast winner to all threads
        4. Return winning proposal for execution
        """
        logger.info("=== Global Workspace Cycle Start ===")

        # Generate proposals from all threads concurrently
        proposal_tasks = [
            thread.generate_proposal(self.current_context)
            for thread in self.threads
        ]

        proposals = await asyncio.gather(*proposal_tasks)

        # Filter out None proposals
        valid_proposals = [p for p in proposals if p is not None]

        # Expose proposals for analytics tracking
        self.last_proposals = valid_proposals

        if not valid_proposals:
            logger.info("No proposals generated, workspace idle")
            return None

        # Score proposals (already have priority scores)
        for proposal in valid_proposals:
            logger.info(f"  [{proposal.source}] {proposal.action_type} → priority={proposal.priority:.3f}")

        # Winner-take-all selection
        winner = max(valid_proposals, key=lambda p: p.priority)

        logger.info(f">>> WINNER: [{winner.source}] {winner.action_type} (priority={winner.priority:.3f})")

        # Broadcast winner to all threads
        for thread in self.threads:
            thread.observe_broadcast(winner)

        self.last_winner = winner
        return winner

    def get_status_summary(self):
        """Get human-readable status of all threads."""
        status = []
        for thread in self.threads:
            status.append(f"{thread.name}: {'active' if thread.last_broadcast else 'idle'}")
        return " | ".join(status)


# Synchronous wrapper for main loop integration
class GlobalWorkspaceSync:
    """
    Synchronous wrapper for GlobalWorkspace to integrate with
    existing synchronous main loop.
    """
    def __init__(self, memory, emotions, learner, planner):
        self.workspace = GlobalWorkspace(memory, emotions, learner, planner)
        self.event_loop = None

    def update_context(self, **kwargs):
        """Update context (synchronous)."""
        self.workspace.update_context(**kwargs)

    def cycle(self):
        """
        Run a single workspace cycle (synchronous).
        Returns: winning Proposal or None
        """
        # Create event loop if needed
        if self.event_loop is None:
            try:
                self.event_loop = asyncio.get_event_loop()
            except RuntimeError:
                self.event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.event_loop)

        # Run async cycle in sync context
        return self.event_loop.run_until_complete(self.workspace.cycle())

    def get_status_summary(self):
        """Get status summary."""
        return self.workspace.get_status_summary()
