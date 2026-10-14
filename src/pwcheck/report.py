"""Human and machine-readable formatting of password-free metadata."""

import json
from dataclasses import asdict
from typing import TYPE_CHECKING

from pwcheck.analyzer import AnalysisResult
from pwcheck.entropy import GUESSES_PER_SECOND, crack_seconds, format_crack_time

if TYPE_CHECKING:
    from pwcheck.hibp import BreachResult


def format_json(result: AnalysisResult, breach: BreachResult | None = None) -> str:
    """Serialize the v1 report schema without secret text or ANSI escapes."""
    payload = asdict(result)
    payload.update(
        schema_version=1,
        offline_guesses_per_second=GUESSES_PER_SECOND,
        offline_crack_seconds=crack_seconds(result.entropy_bits),
        offline_crack_time=format_crack_time(result.entropy_bits),
        hibp=asdict(breach) if breach is not None else None,
    )
    return json.dumps(payload, ensure_ascii=True, allow_nan=False, indent=2)


def format_human(
    result: AnalysisResult,
    *,
    color: bool = False,
    breach: BreachResult | None = None,
) -> str:
    """Format a human report; callers decide whether ANSI color is allowed."""
    verdict = f"Score: {result.score}/4 ({result.label})"
    if color:
        match result.score:
            case 0 | 1:
                ansi = "31"
            case 2:
                ansi = "33"
            case _:
                ansi = "32"
        verdict = f"\033[{ansi}m{verdict}\033[0m"
    classes = ", ".join(result.character_classes) or "none"
    lines = [
        verdict,
        f"Length: {result.length} characters",
        f"Character classes: {classes}",
        f"Estimated entropy: {result.entropy_bits:.1f} bits "
        f"(raw {result.raw_entropy_bits:.1f}, penalties {result.penalty_bits:.1f}; "
        "ceilings may also apply)",
        "Estimated offline crack time: "
        f"{format_crack_time(result.entropy_bits)} at 10^10 guesses/second",
        "Estimates are heuristic, not a security guarantee.",
    ]
    if breach is not None:
        lines.append(f"HIBP: {breach.message}")
        lines.append("Source: Have I Been Pwned (https://haveibeenpwned.com/)")
    lines.append("Weaknesses:")
    lines.extend(f"  - {finding.message}" for finding in result.findings)
    if not result.findings:
        lines.append("  - No listed patterns detected.")
    lines.append("Suggestions (highest impact first):")
    lines.extend(f"  - {suggestion}" for suggestion in result.suggestions)
    return "\n".join(lines)
