"""Synthetic-vault generator for the scale benchmark (paper revision pass 2, 2026-06-07).

Emits markdown notes matching Cipher's REAL vault schema — same frontmatter keys
(`date`/`domain`/`project`/`person`/`type`/`status`/`due`/`source_conversation`),
same folder layout, same filename patterns (`YYYY-MM-DD_slug.md` for dated
categories, bare `slug.md` for people/projects, day files for conversations/) —
so `brain.init_vault()` indexes it exactly like the live vault.

EVERY generated file carries `synthetic: true` frontmatter. This data is for
benchmarking only and is never written into the canonical vault.

Proportions roughly mirror the real vault on 2026-06-07 (conversations-heavy;
see MIX below). RNG is seeded; BASE_DATE is fixed — same args, same vault.
"""

from __future__ import annotations

import argparse
import random
from datetime import date, timedelta
from pathlib import Path

BASE_DATE = date(2026, 6, 7)  # fixed (not date.today()) for reproducibility

# (kind, weight) — mirrors the live vault's mix (conversations ~1/3, the rest spread).
MIX: list[tuple[str, float]] = [
    ("conversation", 0.30),
    ("action_item", 0.12),
    ("follow_up", 0.05),
    ("commitment", 0.10),
    ("decision", 0.10),
    ("person", 0.10),
    ("project", 0.07),
    ("meeting", 0.08),
    ("learned", 0.08),
]

# First entries are deterministic anchors the benchmark queries by name.
PEOPLE = [
    "Jenny Marlow",
    "Dave Chen",
    "Priya Nair",
    "Marcus Webb",
    "Sofia Reyes",
    "Tom Okafor",
    "Lena Fischer",
    "Ravi Menon",
    "Grace Liu",
    "Omar Haddad",
]
PROJECTS = [
    "atlas",
    "northwind",
    "lighthouse",
    "redwood",
    "quartz",
    "meridian",
    "bluebird",
    "cascade",
]
ROLES = ["CEO", "designer", "accountant", "investor", "contractor", None, None]
DOMAINS = ["office", "startup", "personal", None, None]
TOPICS = [
    "vector databases",
    "prompt caching",
    "wake words",
    "tauri packaging",
    "speech synthesis",
]

VERBS = [
    "call",
    "email",
    "review",
    "draft",
    "send",
    "schedule",
    "fix",
    "prepare",
    "test",
    "ship",
]
OBJECTS = [
    "the investor deck",
    "the quarterly summary",
    "the onboarding flow",
    "the billing report",
    "the launch checklist",
    "the API contract",
    "the demo script",
    "the budget sheet",
    "the migration plan",
    "the press note",
]
FILLER = [
    "The timeline is tight but workable.",
    "Costs stay inside the monthly envelope.",
    "Blocked on an external reply for now.",
    "This supersedes the earlier draft from last week.",
    "Latency looked fine on the last pass.",
    "Needs a second look before it goes out.",
    "The vendor confirmed the numbers this morning.",
    "Two follow-ups came out of the discussion.",
    "Scope was trimmed to keep the week realistic.",
    "Everything else stays as agreed.",
]


def _sentences(rng: random.Random, lo: int, hi: int) -> str:
    n = rng.randint(lo, hi)
    out = []
    for _ in range(n):
        out.append(
            rng.choice(
                [
                    f"We need to {rng.choice(VERBS)} {rng.choice(OBJECTS)} by {rng.choice(['Friday', 'Monday', 'next week', 'end of month'])}.",
                    f"{rng.choice(PEOPLE)} mentioned {rng.choice(OBJECTS)} during the sync.",
                    rng.choice(FILLER),
                ]
            )
        )
    return " ".join(out)


def _fm(pairs: list[tuple[str, object]]) -> str:
    """YAML frontmatter block; None -> null (mirrors the live writers)."""
    lines = ["---"]
    for k, v in pairs:
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        elif v is None:
            lines.append(f"{k}: null")
        elif isinstance(v, bool):
            lines.append(f"{k}: {'true' if v else 'false'}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines)


def _counts(n: int) -> dict[str, int]:
    """Largest-remainder allocation of n files across MIX."""
    raw = [(kind, n * w) for kind, w in MIX]
    counts = {kind: int(x) for kind, x in raw}
    rem = sorted(raw, key=lambda kw: kw[1] - int(kw[1]), reverse=True)
    i = 0
    while sum(counts.values()) < n:
        counts[rem[i % len(rem)][0]] += 1
        i += 1
    # Anchors: the benchmark queries Jenny Marlow + atlas by name.
    counts["person"] = max(counts["person"], 2)
    counts["project"] = max(counts["project"], 1)
    return counts


def generate(root: Path, n: int, seed: int = 42) -> dict[str, int]:
    rng = random.Random(seed)
    root.mkdir(parents=True, exist_ok=True)
    counts = _counts(n)
    written: dict[str, int] = {k: 0 for k in counts}

    def d(spread: int = 180) -> date:
        return BASE_DATE - timedelta(days=rng.randint(0, spread))

    def scope(pairs_person: float = 0.4, pairs_project: float = 0.3):
        person = rng.choice(PEOPLE) if rng.random() < pairs_person else None
        project = rng.choice(PROJECTS) if rng.random() < pairs_project else None
        return person, project

    # conversations/ — day files with turn structure (most recent days first so the
    # temporal query window (BASE_DATE-7..BASE_DATE) always has matter at every size).
    for i in range(counts["conversation"]):
        day = BASE_DATE - timedelta(days=i)  # consecutive days back from base
        turns = rng.randint(3, 8)
        body = []
        for t in range(1, turns + 1):
            body.append(
                f"## Turn {t} — {rng.randint(8, 21):02d}:{rng.randint(0, 59):02d}\n\n"
                f"**User:** {_sentences(rng, 1, 2)}\n\n"
                f"**Cipher:** {_sentences(rng, 1, 3)}\n\n---"
            )
        person, project = scope()
        text = (
            _fm(
                [
                    ("date", day.isoformat()),
                    ("turns", turns),
                    ("domain", rng.choice(DOMAINS)),
                    ("project", project),
                    ("person", person),
                    ("synthetic", True),
                ]
            )
            + "\n\n"
            + "\n\n".join(body)
            + "\n"
        )
        p = root / "conversations" / f"{day.isoformat()}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")
        written["conversation"] += 1

    def dated_note(
        folder: str,
        i: int,
        kind: str,
        status: str,
        due: date | None,
        extra: list[tuple[str, object]] | None = None,
    ) -> None:
        nd = d()
        person, project = scope()
        slug = f"{rng.choice(VERBS)}_{rng.choice(OBJECTS).split()[-1]}_{i}"
        pairs = [
            ("date", nd.isoformat()),
            ("domain", rng.choice(DOMAINS)),
            ("project", project),
            ("person", person),
            ("type", kind),
            ("status", status),
        ]
        if due is not None:
            pairs.append(("due", due.isoformat()))
        pairs += (extra or []) + [
            (
                "source_conversation",
                f"conversations/{nd.isoformat()}.md#turn-{rng.randint(1, 6)}",
            ),
            ("synthetic", True),
        ]
        body = f"{_sentences(rng, 2, 5)}\n\n## Details\n\n{_sentences(rng, 3, 8)}\n"
        p = root / folder / f"{nd.isoformat()}_{slug}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(_fm(pairs) + "\n\n" + body, encoding="utf-8")

    for i in range(counts["action_item"]):
        due = (
            BASE_DATE + timedelta(days=rng.randint(-5, 30))
            if rng.random() < 0.7
            else None
        )
        dated_note(
            "action_items",
            i,
            "action_item",
            rng.choice(["open", "open", "open", "done"]),
            due,
        )
        written["action_item"] += 1
    for i in range(counts["follow_up"]):
        dated_note(
            "action_items",
            1000 + i,
            "follow_up",
            "open",
            BASE_DATE + timedelta(days=rng.randint(1, 21))
            if rng.random() < 0.5
            else None,
        )
        written["follow_up"] += 1
    for i in range(counts["commitment"]):
        dated_note(
            "commitments",
            i,
            "commitment",
            rng.choice(["open", "open", "done"]),
            BASE_DATE + timedelta(days=rng.randint(-3, 21)),
        )
        written["commitment"] += 1
    for i in range(counts["decision"]):
        dated_note(
            "decisions",
            i,
            "decision",
            rng.choice(["active", "active", "superseded"]),
            None,
        )
        written["decision"] += 1
    for i in range(counts["meeting"]):
        nd = d()
        attendees = rng.sample(PEOPLE, rng.randint(2, 4))
        body = f"{_sentences(rng, 3, 6)}\n\n## Items\n\n- {_sentences(rng, 1, 1)}\n- {_sentences(rng, 1, 1)}\n"
        p = root / "meetings" / f"{nd.isoformat()}_sync_{i}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            _fm(
                [
                    ("date", nd.isoformat()),
                    ("domain", rng.choice(DOMAINS)),
                    ("project", None),
                    ("person", None),
                    ("type", "meeting"),
                    ("mode", "individual"),
                    ("attendees", attendees),
                    ("synthetic", True),
                ]
            )
            + "\n\n"
            + body,
            encoding="utf-8",
        )
        written["meeting"] += 1
    for i in range(counts["learned"]):
        nd = d()
        topic = rng.choice(TOPICS)
        slug = topic.replace(" ", "_")
        p = root / "learned" / slug / f"{nd.isoformat()}_{i}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            _fm(
                [
                    ("date", nd.isoformat()),
                    ("domain", None),
                    ("project", None),
                    ("person", None),
                    ("type", "learned"),
                    ("topic", topic),
                    ("sources", [f"https://example.com/synthetic/{slug}/{i}"]),
                    ("synthetic", True),
                ]
            )
            + f"\n\n# {topic}\n\n{_sentences(rng, 4, 9)}\n\n## Key points\n\n{_sentences(rng, 3, 6)}\n",
            encoding="utf-8",
        )
        written["learned"] += 1
    for i in range(counts["person"]):
        name = PEOPLE[i % len(PEOPLE)] if i < len(PEOPLE) else f"Synthetic Person {i}"
        slug = name.lower().replace(" ", "_")
        nd = d()
        role = rng.choice(ROLES)
        pairs = [
            ("date", nd.isoformat()),
            ("domain", rng.choice(DOMAINS)),
            ("project", None),
            ("person", name),
            ("type", "person"),
        ]
        if role:
            pairs.append(("role", role))
        pairs.append(("synthetic", True))
        p = root / "people" / f"{slug}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            _fm(pairs)
            + f"\n\n# {name}\n\n{_sentences(rng, 2, 4)}\n\n## Mentions\n\n- {_sentences(rng, 1, 2)}\n",
            encoding="utf-8",
        )
        written["person"] += 1
    for i in range(counts["project"]):
        name = PROJECTS[i % len(PROJECTS)] if i < len(PROJECTS) else f"synthproj{i}"
        nd = d()
        p = root / "projects" / f"{name}.md"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            _fm(
                [
                    ("date", nd.isoformat()),
                    ("domain", rng.choice(DOMAINS)),
                    ("project", name),
                    ("person", None),
                    ("type", "project"),
                    ("status", "active"),
                    ("synthetic", True),
                ]
            )
            + f"\n\n# {name}\n\n{_sentences(rng, 2, 4)}\n\n## Updates\n\n- {_sentences(rng, 1, 2)}\n",
            encoding="utf-8",
        )
        written["project"] += 1

    return written


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "root", type=Path, help="throwaway output dir (NEVER the real vault)"
    )
    ap.add_argument("-n", type=int, default=100, help="total markdown files")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    w = generate(args.root, args.n, args.seed)
    total = sum(w.values())
    print(f"wrote {total} synthetic notes to {args.root}: {w}")
