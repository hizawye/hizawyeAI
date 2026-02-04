"""
Learning Tracker: Meta-learning system for strategy adaptation.
Tracks what works, what doesn't, and learns patterns over time.
"""
import json
import os
from collections import defaultdict
from log import setup_logger

logger = setup_logger()

class LearningTracker:
    def __init__(self, mind_directory="hizawye_mind"):
        self.mind_directory = mind_directory
        self.filepath = os.path.join(mind_directory, "strategy_history.json")

        # Track strategy performance
        self.strategy_results = defaultdict(lambda: {
            'attempts': 0,
            'successes': 0,
            'failures': 0,
            'avg_pain': 0.0,
            'total_pain': 0.0,
            'contexts': []
        })

        # Track concept difficulty
        self.concept_difficulty = defaultdict(lambda: {
            'attempts': 0,
            'successes': 0,
            'best_strategy': None,
            'failed_strategies': []
        })

        # Meta-beliefs about learning
        self.meta_beliefs = {
            'abstract_concepts_need_decomposition': 0.5,
            'simple_strategies_work_for_concrete': 0.5,
            'analogies_help_complex_ideas': 0.5
        }

        self.load_history()

    def load_history(self):
        """Load learning history from file."""
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)
                self.strategy_results = defaultdict(lambda: {
                    'attempts': 0, 'successes': 0, 'failures': 0,
                    'avg_pain': 0.0, 'total_pain': 0.0, 'contexts': []
                }, data.get('strategy_results', {}))
                self.concept_difficulty = defaultdict(lambda: {
                    'attempts': 0, 'successes': 0,
                    'best_strategy': None, 'failed_strategies': []
                }, data.get('concept_difficulty', {}))
                self.meta_beliefs = data.get('meta_beliefs', self.meta_beliefs)
            logger.info("Learning history loaded.")
        except FileNotFoundError:
            logger.info("No learning history found. Starting fresh.")
            self.save_history()

    def save_history(self):
        """Save learning history to file."""
        os.makedirs(self.mind_directory, exist_ok=True)
        data = {
            'strategy_results': dict(self.strategy_results),
            'concept_difficulty': dict(self.concept_difficulty),
            'meta_beliefs': self.meta_beliefs
        }
        with open(self.filepath, 'w') as f:
            json.dump(data, f, indent=4)

    def update_on_outcome(self, concept, strategy, success, pain_delta, context=None):
        """
        Update learning data based on strategy outcome.
        Uses Bayesian-style updating of strategy priors.
        """
        # Update strategy stats
        stats = self.strategy_results[strategy]
        stats['attempts'] = int(stats['attempts']) + 1
        if success:
            stats['successes'] = int(stats['successes']) + 1
        else:
            stats['failures'] = int(stats['failures']) + 1

        stats['total_pain'] = float(stats['total_pain']) + pain_delta
        stats['avg_pain'] = stats['total_pain'] / stats['attempts']

        if context:
            contexts_list = stats['contexts'] if isinstance(stats['contexts'], list) else []
            contexts_list.append({
                'concept': concept,
                'success': success,
                'pain': pain_delta
            })
            # Keep only last 20 contexts
            if len(contexts_list) > 20:
                contexts_list = contexts_list[-20:]
            stats['contexts'] = contexts_list

        # Update concept difficulty
        concept_stats = self.concept_difficulty[concept]
        concept_stats['attempts'] = int(concept_stats.get('attempts', 0)) + 1
        if success:
            concept_stats['successes'] = int(concept_stats.get('successes', 0)) + 1
            concept_stats['best_strategy'] = strategy
        else:
            failed_list = concept_stats.get('failed_strategies', [])
            if isinstance(failed_list, list) and strategy not in failed_list:
                failed_list.append(strategy)
                concept_stats['failed_strategies'] = failed_list

        logger.info(f"Learning update: {strategy} on '{concept}' → {'success' if success else 'failure'}")
        self.save_history()

    def get_strategy_score(self, strategy):
        """
        Compute effectiveness score for a strategy.
        Higher score = better historical performance.
        """
        stats = self.strategy_results[strategy]
        if stats['attempts'] == 0:
            return 0.5  # Neutral prior for untried strategies

        success_rate = stats['successes'] / stats['attempts']
        pain_penalty = min(1.0, stats['avg_pain'] / 100.0)

        # Score balances success rate and pain cost
        score = (success_rate * 0.7) + ((1.0 - pain_penalty) * 0.3)
        return score

    def get_concept_difficulty_score(self, concept):
        """
        Estimate difficulty of a concept based on history.
        Returns 0.0 (easy) to 1.0 (very difficult).
        """
        stats = self.concept_difficulty.get(concept)
        if not stats or stats['attempts'] == 0:
            return 0.5  # Unknown difficulty

        failure_rate = (stats['attempts'] - stats['successes']) / stats['attempts']
        return failure_rate

    def recommend_strategy(self, concept, available_strategies, current_pain=0):
        """
        Recommend best strategy for a concept based on learning history.
        Considers: strategy success rates, concept history, current emotional state.
        """
        # Check concept-specific history
        concept_stats = self.concept_difficulty.get(concept)
        if concept_stats and concept_stats.get('best_strategy'):
            best = concept_stats['best_strategy']
            if best in available_strategies:
                logger.info(f"Recommending '{best}' based on past success with '{concept}'")
                return best

        # Score all available strategies
        strategy_scores = {}
        for strategy in available_strategies:
            base_score = self.get_strategy_score(strategy)

            # Adjust for current pain: high pain → prefer simpler strategies
            if current_pain > 60:
                if 'direct' in strategy or 'simple' in strategy:
                    base_score += 0.2
                elif 'complex' in strategy or 'synthesis' in strategy:
                    base_score -= 0.2

            # Avoid recently failed strategies for this concept
            if concept_stats and strategy in concept_stats.get('failed_strategies', []):
                base_score -= 0.3

            strategy_scores[strategy] = max(0.0, min(1.0, base_score))

        if not strategy_scores:
            return available_strategies[0] if available_strategies else None

        # Select highest scoring strategy
        best_strategy = max(strategy_scores, key=strategy_scores.get)
        logger.info(f"Strategy recommendation: '{best_strategy}' (score: {strategy_scores[best_strategy]:.2f})")
        return best_strategy

    def reflect(self):
        """
        Periodic meta-cognition: analyze learning patterns and update meta-beliefs.
        Returns: list of insights discovered.
        """
        insights = []

        # Analyze strategy patterns
        if len(self.strategy_results) >= 3:
            strategy_ranking = sorted(
                self.strategy_results.items(),
                key=lambda x: self.get_strategy_score(x[0]),
                reverse=True
            )

            best_strategy = strategy_ranking[0][0]
            worst_strategy = strategy_ranking[-1][0]

            insights.append(f"Most effective strategy: {best_strategy}")
            insights.append(f"Least effective strategy: {worst_strategy}")

        # Identify difficult concept patterns
        difficult_concepts = [
            (concept, stats['attempts'], stats['successes'])
            for concept, stats in self.concept_difficulty.items()
            if stats['attempts'] >= 2 and stats['successes'] == 0
        ]

        if difficult_concepts:
            insights.append(f"Struggling with {len(difficult_concepts)} concepts despite multiple attempts")

        # Update meta-beliefs based on evidence
        total_attempts = sum(s['attempts'] for s in self.strategy_results.values())
        if total_attempts >= 10:
            # Check if decomposition helps with abstract concepts
            decomposition_stats = self.strategy_results.get('top_down_decomposition')
            if decomposition_stats and decomposition_stats['attempts'] > 0:
                decomp_success = decomposition_stats['successes'] / decomposition_stats['attempts']
                self.meta_beliefs['abstract_concepts_need_decomposition'] = decomp_success

        logger.info(f"Reflection generated {len(insights)} insights")
        return insights

    def get_learning_summary(self):
        """Get human-readable summary of learning progress."""
        total_attempts = sum(s['attempts'] for s in self.strategy_results.values())
        total_successes = sum(s['successes'] for s in self.strategy_results.values())

        if total_attempts == 0:
            return "No learning history yet"

        success_rate = (total_successes / total_attempts) * 100
        num_strategies = len(self.strategy_results)
        num_concepts = len(self.concept_difficulty)

        return (f"Tried {num_strategies} strategies across {num_concepts} concepts. "
                f"Overall success rate: {success_rate:.1f}%")
