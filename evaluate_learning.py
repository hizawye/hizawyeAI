#!/usr/bin/env python3
"""
Evaluate whether learning happened using heuristic checks and an optional judge model.
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import ollama  # type: ignore
except Exception:
    ollama = None

from analytics_engine import AnalyticsEngine

INVALID_PHRASES = [
    "system instruction",
    "your task",
    "your output",
    "define the concept",
    "direct fulfillment",
    "echo instructions",
    "first-person realization",
    "example:",
    "as a thought synthesizer",
    "output rules",
    "additional constraints",
    "i feel disconnected",
]


def load_memory_descriptions(mind_dir: Path) -> Dict[str, str]:
    memory_path = mind_dir / "memory_graph.json"
    if not memory_path.exists():
        return {}
    with memory_path.open() as f:
        data = json.load(f)
    descriptions: Dict[str, str] = {}
    for node in data.get("nodes", []):
        if not isinstance(node, dict):
            continue
        concept = node.get("id")
        description = node.get("description")
        if concept and description:
            descriptions[str(concept)] = str(description)
    return descriptions


def load_session(mind_dir: Path, session_id: Optional[str]) -> Optional[dict]:
    if session_id:
        analytics_dir = mind_dir / "analytics"
        session_file = analytics_dir / f"session_{session_id.replace(':', '-')}.json"
        if session_file.exists():
            return AnalyticsEngine.load_session(session_file)
        matches = list(analytics_dir.glob(f"session_*{session_id}*.json"))
        if matches:
            return AnalyticsEngine.load_session(matches[0])
        return None

    latest = mind_dir / "analytics" / "session_latest.json"
    if latest.exists():
        return AnalyticsEngine.load_session(latest)
    return None


def heuristic_eval(description: str, min_words: int, max_words: int) -> Dict[str, Any]:
    desc = description.strip()
    words = desc.split()
    lower = desc.lower()

    reasons = []
    if len(words) < min_words:
        reasons.append(f"too_short({len(words)})")
    if len(words) > max_words:
        reasons.append(f"too_long({len(words)})")
    if any(phrase in lower for phrase in INVALID_PHRASES):
        reasons.append("invalid_phrase")
    if len(set(words)) < max(3, len(words) // 3):
        reasons.append("low_variety")

    return {
        "pass": len(reasons) == 0,
        "word_count": len(words),
        "reasons": reasons,
    }


def _extract_json(text: str) -> Optional[dict]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def ollama_available(model: str) -> bool:
    if not ollama:
        return False
    try:
        list_fn = getattr(ollama, "list", None)
        if callable(list_fn):
            data = list_fn()
            models: List[str] = []
            if isinstance(data, dict):
                models = [m.get("name") for m in data.get("models", []) if isinstance(m, dict)]
            elif isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        models.append(item.get("name"))
                    elif isinstance(item, str):
                        models.append(item)
            if model in models:
                return True
            if any(name and name.startswith(model) for name in models):
                return True
    except Exception:
        return False

    try:
        _ = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            options={"temperature": 0}
        )
        return True
    except Exception:
        return False


def judge_with_llm(model: str, concept: str, description: str) -> Dict[str, Any]:
    if not ollama:
        return {"error": "ollama_not_installed"}

    prompt = (
        "You are a strict evaluator of definitions.\n"
        "Evaluate the definition for correctness, clarity, and non-tautology.\n"
        "Return JSON only: {\"score\":0-5, \"verdict\":\"pass\"|\"fail\", \"reasons\":[...]}\n"
        "A score of 3+ should be pass if the definition is reasonably clear and not circular.\n\n"
        f"Concept: {concept}\n"
        f"Definition: {description}\n"
    )

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0}
        )
        text = response["message"]["content"].strip()
        data = _extract_json(text)
        if not data:
            return {"error": "invalid_json", "raw": text}
        score = data.get("score")
        verdict = data.get("verdict")
        reasons = data.get("reasons", [])
        return {
            "score": score,
            "verdict": verdict,
            "reasons": reasons,
        }
    except Exception as exc:
        return {"error": f"exception: {exc}"}


def main():
    parser = argparse.ArgumentParser(description="Evaluate learned concepts using heuristics and/or a judge model")
    parser.add_argument("--mind-dir", type=str, default="hizawye_mind")
    parser.add_argument("--session", type=str, help="Session ID (default: latest)")
    parser.add_argument(
        "--scope",
        choices=["described", "successful", "attempted", "all-nodes"],
        default="described",
        help="Which concepts to evaluate"
    )
    parser.add_argument("--model", type=str, default="llama3.2:3b")
    parser.add_argument(
        "--mode",
        choices=["heuristic", "llm", "both"],
        default="both",
        help="Evaluation mode"
    )
    parser.add_argument("--max", type=int, default=0, help="Limit number of concepts (0 = all)")
    parser.add_argument("--min-words", type=int, default=5)
    parser.add_argument("--max-words", type=int, default=80)
    parser.add_argument("--output", type=str, default="reports")

    args = parser.parse_args()

    mind_dir = Path(args.mind_dir)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    session = load_session(mind_dir, args.session)
    descriptions = load_memory_descriptions(mind_dir)

    concepts: List[str] = []
    missing_descriptions: List[str] = []

    if args.scope in ("successful", "attempted"):
        if not session:
            print("❌ No analytics session found.")
            return
        concepts_learned = session.get("concepts_learned", {})
        if args.scope == "successful":
            concepts = [c for c, v in concepts_learned.items() if v.get("success")]
        else:
            concepts = list(concepts_learned.keys())
    elif args.scope == "all-nodes":
        memory_path = mind_dir / "memory_graph.json"
        if not memory_path.exists():
            print("❌ No memory_graph.json found.")
            return
        with memory_path.open() as f:
            data = json.load(f)
        concepts = [n.get("id") for n in data.get("nodes", []) if isinstance(n, dict) and n.get("id")]
    else:
        concepts = list(descriptions.keys())

    concepts = [c for c in concepts if c]

    if args.max and len(concepts) > args.max:
        concepts = concepts[: args.max]

    use_llm = args.mode in ("llm", "both")
    llm_ok = False
    if use_llm:
        llm_ok = ollama_available(args.model)
        if not llm_ok:
            print(f"⚠️ Ollama model not available: {args.model}. LLM evaluation disabled.")

    results = []
    heuristic_pass = 0
    llm_pass = 0
    both_pass = 0

    for concept in concepts:
        description = descriptions.get(concept)
        if not description:
            missing_descriptions.append(concept)
            results.append({
                "concept": concept,
                "description": None,
                "heuristic": None,
                "llm": None,
                "verdict": "missing_description",
            })
            continue

        heuristic = None
        llm = None
        verdict = "unknown"

        if args.mode in ("heuristic", "both"):
            heuristic = heuristic_eval(description, args.min_words, args.max_words)
            if heuristic["pass"]:
                heuristic_pass += 1

        if use_llm and llm_ok:
            llm = judge_with_llm(args.model, concept, description)
            if llm.get("verdict") == "pass" and (llm.get("score") is None or llm.get("score") >= 3):
                llm_pass += 1

        if args.mode == "heuristic":
            verdict = "pass" if heuristic and heuristic["pass"] else "fail"
        elif args.mode == "llm":
            verdict = "pass" if llm and llm.get("verdict") == "pass" and (llm.get("score") is None or llm.get("score") >= 3) else "fail"
        else:
            verdict = "pass" if (heuristic and heuristic["pass"] and llm and llm.get("verdict") == "pass" and (llm.get("score") is None or llm.get("score") >= 3)) else "fail"

        if verdict == "pass" and args.mode == "both":
            both_pass += 1

        results.append({
            "concept": concept,
            "description": description,
            "heuristic": heuristic,
            "llm": llm,
            "verdict": verdict,
        })

    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    session_id = session.get("session_id") if session else "unknown"

    summary = {
        "timestamp": timestamp,
        "session_id": session_id,
        "scope": args.scope,
        "mode": args.mode,
        "model": args.model if use_llm else None,
        "total_concepts": len(concepts),
        "missing_descriptions": len(missing_descriptions),
        "heuristic_pass": heuristic_pass,
        "llm_pass": llm_pass,
        "both_pass": both_pass,
    }

    json_path = output_dir / f"learning_verification_{timestamp}.json"
    with json_path.open("w") as f:
        json.dump({"summary": summary, "results": results}, f, indent=2)

    # Markdown report
    md_lines = [
        "# Learning Verification Report",
        f"**Date:** {timestamp}",
        f"**Session:** {session_id}",
        f"**Scope:** {args.scope}",
        f"**Mode:** {args.mode}",
        f"**Model:** {args.model if use_llm else 'N/A'}",
        "",
        "## Summary",
        f"- Concepts evaluated: {summary['total_concepts']}",
        f"- Missing descriptions: {summary['missing_descriptions']}",
        f"- Heuristic pass: {summary['heuristic_pass']}",
        f"- LLM pass: {summary['llm_pass']}",
        f"- Both pass: {summary['both_pass']}",
        "",
        "## Results",
        "| Concept | Heuristic | LLM Verdict | Score | Notes |",
        "|---|---|---|---|---|",
    ]

    for item in results:
        concept = item["concept"]
        heuristic_state = "N/A"
        if item.get("heuristic") is not None:
            heuristic_state = "pass" if item["heuristic"]["pass"] else "fail"
        llm_state = "N/A"
        score = ""
        notes = ""
        if item.get("llm"):
            if item["llm"].get("error"):
                llm_state = "error"
                notes = item["llm"].get("error", "")
            else:
                llm_state = item["llm"].get("verdict", "unknown")
                score = item["llm"].get("score", "")
        if item["verdict"] == "missing_description":
            notes = "missing description"
        md_lines.append(f"| {concept} | {heuristic_state} | {llm_state} | {score} | {notes} |")

    md_path = output_dir / f"learning_verification_{timestamp}.md"
    with md_path.open("w") as f:
        f.write("\n".join(md_lines))

    print("\n✅ Learning verification complete")
    print(f"- JSON: {json_path}")
    print(f"- Report: {md_path}")
    print(f"- Evaluated: {summary['total_concepts']} concepts")
    if missing_descriptions:
        print(f"- Missing descriptions: {len(missing_descriptions)}")


if __name__ == "__main__":
    main()
