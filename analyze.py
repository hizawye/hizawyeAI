#!/usr/bin/env python3
"""
Analytics CLI Tool for Hizawye AI
View and analyze session data, generate reports, and compare sessions.
"""

import argparse
import json
from pathlib import Path
from analytics_engine import AnalyticsEngine
from report_generator import ReportGenerator


def load_latest_session(mind_dir: Path) -> dict:
    """Load the most recent analytics session."""
    analytics_dir = mind_dir / "analytics"
    latest_path = analytics_dir / "session_latest.json"

    if not latest_path.exists():
        print("❌ No analytics sessions found. Run the AI first to generate data.")
        return None

    return AnalyticsEngine.load_session(latest_path)


def load_session_by_id(mind_dir: Path, session_id: str) -> dict:
    """Load a specific session by ID."""
    analytics_dir = mind_dir / "analytics"

    # Try exact match first
    session_file = analytics_dir / f"session_{session_id.replace(':', '-')}.json"
    if session_file.exists():
        return AnalyticsEngine.load_session(session_file)

    # Try partial match
    matches = list(analytics_dir.glob(f"session_*{session_id}*.json"))
    if matches:
        return AnalyticsEngine.load_session(matches[0])

    print(f"❌ Session '{session_id}' not found.")
    return None


def list_sessions(mind_dir: Path):
    """List all available analytics sessions."""
    analytics_dir = mind_dir / "analytics"

    if not analytics_dir.exists():
        print("❌ No analytics directory found.")
        return

    sessions = sorted(analytics_dir.glob("session_*.json"))
    sessions = [s for s in sessions if s.name != "session_latest.json"]

    if not sessions:
        print("❌ No analytics sessions found.")
        return

    print(f"\n📊 Found {len(sessions)} session(s):\n")

    for session_file in sessions:
        data = AnalyticsEngine.load_session(session_file)
        session_id = data.get("session_id", "Unknown")
        cycles = data.get("cycles", 0)
        runtime = data.get("runtime_seconds", 0)

        concepts = data.get("concepts_learned", {})
        successful = sum(1 for c in concepts.values() if c.get("success", False))
        total = len(concepts)

        minutes = int(runtime // 60)
        seconds = int(runtime % 60)

        print(f"  • {session_id}")
        print(f"    Runtime: {minutes}m {seconds}s ({cycles} cycles)")
        print(f"    Learning: {successful}/{total} concepts")
        print()


def generate_reports(session_data: dict, output_dir: Path):
    """Generate all reports for a session."""
    generator = ReportGenerator(session_data)

    print(f"\n📝 Generating reports to {output_dir}/")

    saved_files = generator.generate_all_reports(output_dir)

    print(f"\n✅ Generated {len(saved_files)} reports:")
    for filepath in saved_files:
        print(f"  • {filepath.name}")

    return saved_files


def show_summary(session_data: dict):
    """Display quick summary statistics."""
    session_id = session_data.get("session_id", "Unknown")
    cycles = session_data.get("cycles", 0)
    runtime = session_data.get("runtime_seconds", 0)

    minutes = int(runtime // 60)
    seconds = int(runtime % 60)

    concepts = session_data.get("concepts_learned", {})
    total_concepts = len(concepts)
    successful = sum(1 for c in concepts.values() if c.get("success", False))

    strategies = session_data.get("strategies_used", {})
    pain_events = session_data.get("pain_events", [])
    reflections = session_data.get("reflections", [])

    competition = session_data.get("workspace_competition", {})
    if competition:
        dominant = max(competition.items(), key=lambda x: x[1].get("wins", 0))
        dominant_name = dominant[0]
        dominant_wins = dominant[1].get("wins", 0)
    else:
        dominant_name = "N/A"
        dominant_wins = 0

    print(f"\n📊 Session Summary: {session_id}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Runtime:        {minutes}m {seconds}s ({cycles} cycles)")
    print(f"Concepts:       {successful}/{total_concepts} learned")
    print(f"Strategies:     {len(strategies)} different approaches")
    print(f"Pain events:    {len(pain_events)}")
    print(f"Reflections:    {len(reflections)}")
    print(f"Dominant thread: {dominant_name} ({dominant_wins} wins)")
    print()


def compare_sessions(session1: dict, session2: dict):
    """Compare two sessions side by side."""
    print("\n📊 Session Comparison")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    id1 = session1.get("session_id", "Session 1")
    id2 = session2.get("session_id", "Session 2")

    def get_stats(data):
        concepts = data.get("concepts_learned", {})
        total = len(concepts)
        successful = sum(1 for c in concepts.values() if c.get("success", False))
        success_rate = (successful / total * 100) if total > 0 else 0

        return {
            "cycles": data.get("cycles", 0),
            "runtime": data.get("runtime_seconds", 0),
            "concepts_total": total,
            "concepts_success": successful,
            "success_rate": success_rate,
            "strategies": len(data.get("strategies_used", {})),
            "pain_events": len(data.get("pain_events", [])),
            "reflections": len(data.get("reflections", []))
        }

    stats1 = get_stats(session1)
    stats2 = get_stats(session2)

    print(f"{'Metric':<20} {'Session 1':>15} {'Session 2':>15} {'Change':>10}")
    print("─" * 65)

    print(f"{'Cycles':<20} {stats1['cycles']:>15} {stats2['cycles']:>15} {stats2['cycles']-stats1['cycles']:>+10}")
    print(f"{'Runtime (sec)':<20} {stats1['runtime']:>15.1f} {stats2['runtime']:>15.1f} {stats2['runtime']-stats1['runtime']:>+10.1f}")
    print(f"{'Concepts learned':<20} {stats1['concepts_success']:>15} {stats2['concepts_success']:>15} {stats2['concepts_success']-stats1['concepts_success']:>+10}")
    print(f"{'Success rate (%)':<20} {stats1['success_rate']:>15.1f} {stats2['success_rate']:>15.1f} {stats2['success_rate']-stats1['success_rate']:>+10.1f}")
    print(f"{'Strategies used':<20} {stats1['strategies']:>15} {stats2['strategies']:>15} {stats2['strategies']-stats1['strategies']:>+10}")
    print(f"{'Pain events':<20} {stats1['pain_events']:>15} {stats2['pain_events']:>15} {stats2['pain_events']-stats1['pain_events']:>+10}")
    print(f"{'Reflections':<20} {stats1['reflections']:>15} {stats2['reflections']:>15} {stats2['reflections']-stats1['reflections']:>+10}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Analyze Hizawye AI session data and generate reports"
    )

    parser.add_argument(
        "--mind-dir",
        type=str,
        default="hizawye_mind",
        help="Path to mind directory (default: hizawye_mind)"
    )

    parser.add_argument(
        "--session",
        type=str,
        help="Session ID to analyze (default: latest)"
    )

    parser.add_argument(
        "--list",
        action="store_true",
        help="List all available sessions"
    )

    parser.add_argument(
        "--compare",
        type=str,
        nargs=2,
        metavar=("SESSION1", "SESSION2"),
        help="Compare two sessions"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="reports",
        help="Output directory for reports (default: reports)"
    )

    parser.add_argument(
        "--format",
        choices=["summary", "reports", "both"],
        default="both",
        help="Output format (default: both)"
    )

    args = parser.parse_args()

    mind_dir = Path(args.mind_dir)

    # List sessions
    if args.list:
        list_sessions(mind_dir)
        return

    # Compare sessions
    if args.compare:
        session1 = load_session_by_id(mind_dir, args.compare[0])
        session2 = load_session_by_id(mind_dir, args.compare[1])

        if session1 and session2:
            compare_sessions(session1, session2)
        return

    # Load session
    if args.session:
        session_data = load_session_by_id(mind_dir, args.session)
    else:
        session_data = load_latest_session(mind_dir)

    if not session_data:
        return

    # Show summary
    if args.format in ["summary", "both"]:
        show_summary(session_data)

    # Generate reports
    if args.format in ["reports", "both"]:
        output_dir = Path(args.output)
        generate_reports(session_data, output_dir)


if __name__ == "__main__":
    main()
