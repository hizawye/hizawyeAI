"""
Report Generator for Hizawye AI Analytics
Generates beautiful markdown reports from analytics data.
"""

from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class ReportGenerator:
    """Generates markdown reports from analytics session data."""

    def __init__(self, session_data: Dict[str, Any]):
        self.data = session_data

    def generate_session_summary(self) -> str:
        """Generate executive session summary report."""
        cycles = self.data.get("cycles", 0)
        runtime = self.data.get("runtime_seconds", 0)
        minutes = int(runtime // 60)
        seconds = int(runtime % 60)

        concepts = self.data.get("concepts_learned", {})
        total_concepts = len(concepts)
        successful = sum(1 for c in concepts.values() if c.get("success", False))
        success_rate = (successful / total_concepts * 100) if total_concepts > 0 else 0

        strategies = self.data.get("strategies_used", {})

        # Dominant thread
        competition = self.data.get("workspace_competition", {})
        if competition:
            dominant_thread = max(competition.items(), key=lambda x: x[1].get("wins", 0))
            dominant_name = dominant_thread[0]
            dominant_wins = dominant_thread[1].get("wins", 0)
            dominant_pct = (dominant_wins / cycles * 100) if cycles > 0 else 0
        else:
            dominant_name = "N/A"
            dominant_pct = 0

        # Emotional journey
        timeline = self.data.get("emotional_timeline", [])
        if timeline:
            first_state = timeline[0]
            last_state = timeline[-1]

            peak_pain_event = max(timeline, key=lambda x: x.get("pain", 0))
            avg_curiosity = sum(e.get("curiosity", 0) for e in timeline) / len(timeline)
        else:
            first_state = {}
            last_state = {}
            peak_pain_event = {}
            avg_curiosity = 0

        report = f"""# Hizawye AI - Session Report
**Date:** {self.data.get('session_id', 'Unknown')}
**Runtime:** {minutes} min {seconds} sec ({cycles} cycles)

## Executive Summary
- Concepts learned: {successful}/{total_concepts}
- Strategies used: {len(strategies)} different approaches
- Success rate: {success_rate:.1f}%
- Dominant thread: {dominant_name} ({dominant_pct:.0f}% of conscious actions)

## Emotional Journey
- Started: confidence {first_state.get('confidence', 0):.2f}
- Ended: confidence {last_state.get('confidence', 0):.2f}
- Peak pain: {peak_pain_event.get('pain', 0):.1f} at cycle {peak_pain_event.get('cycle', 0)}
- Curiosity: avg {avg_curiosity:.1f}

## Top Insights
"""
        # Add strategy insights
        if strategies:
            best_strategy = max(
                strategies.items(),
                key=lambda x: (x[1].get("successes", 0) / x[1].get("attempts", 1)) if x[1].get("attempts", 0) > 0 else 0
            )
            best_name = best_strategy[0]
            best_rate = (best_strategy[1].get("successes", 0) / best_strategy[1].get("attempts", 1) * 100) if best_strategy[1].get("attempts", 0) > 0 else 0
            report += f"- {best_name} most effective ({best_rate:.0f}% success)\n"

        # Failed concepts
        failed = [name for name, data in concepts.items() if not data.get("success", False)]
        if failed:
            report += f"- Struggled with: {', '.join(failed[:3])}\n"

        # Meta-cognition
        reflections = self.data.get("reflections", [])
        if reflections:
            report += f"- Meta-cognition triggered {len(reflections)} times\n"

        return report

    def generate_learning_analysis(self) -> str:
        """Generate learning analysis report."""
        strategies = self.data.get("strategies_used", {})
        concepts = self.data.get("concepts_learned", {})

        report = """# Learning Analysis

## Strategy Effectiveness

| Strategy | Attempts | Success Rate | Avg Pain Cost | Performance |
|----------|----------|--------------|---------------|-------------|
"""

        for strategy_name, stats in sorted(strategies.items(), key=lambda x: x[1].get("successes", 0), reverse=True):
            attempts = stats.get("attempts", 0)
            successes = stats.get("successes", 0)
            total_pain = stats.get("total_pain", 0)

            success_rate = (successes / attempts * 100) if attempts > 0 else 0
            avg_pain = (total_pain / attempts) if attempts > 0 else 0

            performance = "⭐⭐⭐" if success_rate > 75 else "⭐⭐" if success_rate > 50 else "⭐"

            report += f"| {strategy_name} | {attempts} | {success_rate:.0f}% | {avg_pain:.1f} | {performance} |\n"

        # Difficult concepts
        failed_concepts = [(name, data) for name, data in concepts.items() if not data.get("success", False)]
        if failed_concepts:
            report += "\n## Difficult Concepts\n"
            for i, (name, data) in enumerate(failed_concepts[:5], 1):
                attempts = data.get("attempts", 0)
                strategies_tried = data.get("strategies_tried", [])
                report += f"{i}. **{name}** - {attempts} attempts, 0 success (tried: {', '.join(strategies_tried)})\n"

        # Successful concepts
        successful_concepts = [(name, data) for name, data in concepts.items() if data.get("success", False)]
        if successful_concepts:
            report += "\n## Successfully Learned\n"
            for name, data in successful_concepts[:10]:
                strategy = data.get("successful_strategy", "unknown")
                attempts = data.get("attempts", 0)
                report += f"- **{name}** (strategy: {strategy}, attempts: {attempts})\n"

        return report

    def generate_consciousness_patterns(self) -> str:
        """Generate consciousness pattern analysis."""
        competition = self.data.get("workspace_competition", {})
        cycles = self.data.get("cycles", 0)

        report = """# Consciousness Patterns

## Global Workspace Competition

### Thread Win Rates
"""

        if competition:
            sorted_threads = sorted(competition.items(), key=lambda x: x[1].get("wins", 0), reverse=True)

            for thread_name, stats in sorted_threads:
                wins = stats.get("wins", 0)
                proposals = stats.get("total_proposals", 0)
                win_rate = (wins / cycles * 100) if cycles > 0 else 0

                report += f"- {thread_name}: {win_rate:.0f}% ({wins}/{cycles} cycles)\n"

            # ASCII bar chart
            report += "\n### Visual Distribution\n```\n"
            max_wins = max(s.get("wins", 0) for s in competition.values())
            for thread_name, stats in sorted_threads:
                wins = stats.get("wins", 0)
                bar_length = int((wins / max_wins * 40)) if max_wins > 0 else 0
                bar = "█" * bar_length
                report += f"{thread_name:20s} {bar} {wins}\n"
            report += "```\n"

        # Behavioral patterns
        reflections = self.data.get("reflections", [])
        if reflections:
            report += "\n### Reflection Triggers\n"
            reflection_cycles = [r.get("cycle", 0) for r in reflections]
            report += f"- Cycles: {', '.join(map(str, reflection_cycles))}\n"

            triggers = {}
            for r in reflections:
                trigger = r.get("trigger", "unknown")
                triggers[trigger] = triggers.get(trigger, 0) + 1

            report += "- Trigger types:\n"
            for trigger, count in sorted(triggers.items(), key=lambda x: x[1], reverse=True):
                report += f"  - {trigger}: {count} times\n"

        return report

    def generate_emotional_dynamics(self) -> str:
        """Generate emotional dynamics report."""
        timeline = self.data.get("emotional_timeline", [])
        pain_events = self.data.get("pain_events", [])

        report = """# Emotional Dynamics

## Pain Analysis
"""

        if pain_events:
            total_pain = len(pain_events)
            peak_pain = max(pain_events, key=lambda x: x.get("pain", 0))

            report += f"- Total pain events: {total_pain}\n"
            report += f"- Peak pain: {peak_pain.get('pain', 0):.1f} at cycle {peak_pain.get('cycle', 0)}\n"

            # Pain types
            frustration_count = sum(1 for e in pain_events if e.get("frustration", 0) > 50)
            confusion_count = sum(1 for e in pain_events if e.get("confusion", 0) > 50)

            report += f"- Frustration events: {frustration_count}\n"
            report += f"- Confusion events: {confusion_count}\n"

        if timeline:
            # Curiosity analysis
            curiosity_values = [e.get("curiosity", 0) for e in timeline if "curiosity" in e]
            if curiosity_values:
                avg_curiosity = sum(curiosity_values) / len(curiosity_values)
                min_curiosity = min(curiosity_values)
                max_curiosity = max(curiosity_values)

                report += f"\n## Curiosity Patterns\n"
                report += f"- Average: {avg_curiosity:.1f}\n"
                report += f"- Range: {min_curiosity:.1f} - {max_curiosity:.1f}\n"

            # Confidence trajectory
            confidence_values = [e.get("confidence", 0) for e in timeline if "confidence" in e]
            if confidence_values:
                start_conf = confidence_values[0]
                end_conf = confidence_values[-1]
                min_conf = min(confidence_values)

                report += f"\n## Confidence Trajectory\n"
                report += f"- Started: {start_conf:.2f}\n"
                report += f"- Low point: {min_conf:.2f}\n"
                report += f"- Ended: {end_conf:.2f}\n"

                if end_conf > start_conf:
                    report += "- Trend: ↑ Growing confidence\n"
                elif end_conf < start_conf:
                    report += "- Trend: ↓ Declining confidence\n"
                else:
                    report += "- Trend: → Stable\n"

        return report

    def generate_all_reports(self, output_dir: Path):
        """Generate all reports and save to files."""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        reports = {
            "session_summary.md": self.generate_session_summary(),
            "learning_analysis.md": self.generate_learning_analysis(),
            "consciousness_patterns.md": self.generate_consciousness_patterns(),
            "emotional_dynamics.md": self.generate_emotional_dynamics()
        }

        saved_files = []
        for filename, content in reports.items():
            filepath = output_dir / filename
            with open(filepath, 'w') as f:
                f.write(content)
            saved_files.append(filepath)

        return saved_files
