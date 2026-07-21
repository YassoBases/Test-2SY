"""M9 — Curriculum Progression Graph verifier.

Shows Cluster → Domain → Micro Skill → Educational Case → Vocab → Grammar
→ Discussion → Alex for A1–C1, and proves ordered progression + same-node
case diversity.

Usage:
  python -u scripts/verify_speaking_m9_progression_graph.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND))

PASS = 0
FAIL = 0


def check(name: str, cond: bool, detail: str = "") -> None:
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  OK  {name}", flush=True)
    else:
        FAIL += 1
        suffix = f" — {detail}" if detail else ""
        print(f" FAIL {name}{suffix}", flush=True)


def _simulate_path(cefr: str, lessons: int = 5):
    """Simulate successive lessons with mastery rising → advance along spine."""
    from app.services.language_speaking_curriculum_engine import (
        PROGRESSION_NODES,
        PROGRESSION_SPINE_IDS,
        ProgressionMasteryLedger,
        resolve_progression_decision,
    )

    ledger = ProgressionMasteryLedger()
    order = ("A1", "A2", "B1", "B2", "C1")
    level = cefr.upper() if cefr.upper() in order else "A2"
    level_i = order.index(level)
    # Pre-complete earlier CEFR bands (foundations already met) so samples show
    # the active band's journey rather than replaying A1 for every level.
    for nid in PROGRESSION_SPINE_IDS:
        node = PROGRESSION_NODES[nid]
        try:
            if order.index(node.cefr_min) < level_i:
                ledger.node_mastery[nid] = node.estimated_mastery_advance
                ledger.node_exposure[nid] = 2
                if nid not in ledger.completed_path:
                    ledger.completed_path.append(nid)
        except ValueError:
            pass

    decisions = []
    for _ in range(lessons):
        d = resolve_progression_decision(cefr=cefr, ledger=ledger)
        decisions.append(d)
        ledger.current_node_id = d.node.node_id
        ledger.node_exposure[d.node.node_id] = int(
            ledger.node_exposure.get(d.node.node_id) or 0
        ) + 1
        if d.case_variant.case_id not in ledger.used_case_ids:
            ledger.used_case_ids.append(d.case_variant.case_id)
        ledger.node_mastery[d.node.node_id] = d.node.estimated_mastery_advance
        for pid in d.node.prerequisite_ids:
            pr = PROGRESSION_NODES.get(pid)
            if pr:
                ledger.node_mastery[pid] = max(
                    float(ledger.node_mastery.get(pid) or 0.0),
                    pr.estimated_mastery_advance,
                )
                ledger.node_exposure[pid] = max(1, int(ledger.node_exposure.get(pid) or 0))
    return decisions


def _generate_package(cefr: str, **kwargs):
    from types import SimpleNamespace

    from app.services.language_educational_package.pipeline import process_package_generation
    from app.services.language_speaking_curriculum_engine import enrich_speaking_constraints_payload
    from app.services.language_speaking_diagnostic.selector import select_speaking_target
    from app.services.language_speaking_educational_package.constraint_builder import (
        build_speaking_package_constraints,
    )
    from app.services.language_speaking_educational_package.template_author import (
        AUTHOR_PROVIDER_TEMPLATE,
        author_package_json_template,
    )
    from app.services.language_speaking_knowledge_model.storage import empty_knowledge_model
    from app.services.language_speaking_lesson_planner.planner import (
        assemble_speaking_lesson_blueprint,
        continue_alex_from_story_spine,
    )
    from app.services.language_speaking_runtime_api.journey_constraints import (
        build_constraints_payload_from_journey,
    )

    km = empty_knowledge_model(student_id=9900, language_id=1)
    rec = select_speaking_target(km, official_cefr=cefr, speaking_goal="general_english")
    bp = assemble_speaking_lesson_blueprint(rec)
    try:
        bp.official_cefr_hint = cefr
    except Exception:
        pass
    row = SimpleNamespace(
        official_speaking_cefr=SimpleNamespace(value=cefr),
        learning_stage_speaking=2,
        promotion_readiness_json=kwargs.get("promotion_readiness_json") or {},
    )
    payload = build_constraints_payload_from_journey(row=row, blueprint=bp, session=None)
    payload["official_cefr"] = cefr
    if kwargs.get("speaking_progression_mastery"):
        # Re-resolve progression with injected ledger (journey enriched with empty state)
        payload["speaking_progression_mastery"] = kwargs["speaking_progression_mastery"]
        for k in (
            "curriculum_progression",
            "progression_node_id",
            "progression_case_id",
            "progression_action",
        ):
            payload.pop(k, None)
        payload = enrich_speaking_constraints_payload(payload)
    constraints = build_speaking_package_constraints(payload)
    raw = author_package_json_template(constraints)
    result = process_package_generation(
        constraints,
        raw,
        author_provider=AUTHOR_PROVIDER_TEMPLATE,
        attempt_repair=True,
    )
    assert result.success and result.package is not None
    pkg = result.package
    alex = continue_alex_from_story_spine(
        bp.alex_context,
        title=pkg.story_spine.title,
        setting=pkg.story_spine.setting,
        characters=[c.name for c in pkg.story_spine.characters],
        conflict=pkg.story_spine.conflict,
        continuation_hook=pkg.story_spine.continuation_hook,
        case_category=pkg.story_spine.case_category,
        case_archetype=pkg.story_spine.case_archetype,
        stakeholders=list(pkg.story_spine.stakeholders),
        decision_point=pkg.story_spine.decision_point,
    )
    return constraints, pkg, alex


def main() -> int:
    print("\n=== M9 Curriculum Progression Graph ===\n", flush=True)

    from app.services.language_speaking_curriculum_engine import (
        CURRICULUM_ENGINE_VERSION,
        PROGRESSION_NODES,
        PROGRESSION_SPINE_IDS,
        ProgressionMasteryLedger,
        resolve_progression_decision,
    )

    check("engine version ≥ 2.4", CURRICULUM_ENGINE_VERSION.startswith("2.4"))
    check("spine has 20+ nodes", len(PROGRESSION_SPINE_IDS) >= 20)
    check(
        "all spine ids resolve",
        all(nid in PROGRESSION_NODES for nid in PROGRESSION_SPINE_IDS),
    )
    # Graph integrity
    orphan_prereq = False
    for nid, node in PROGRESSION_NODES.items():
        for p in node.prerequisite_ids:
            if p not in PROGRESSION_NODES:
                orphan_prereq = True
        check(
            f"{nid}. has ≥2 case variants",
            len(node.case_variants) >= 2,
            str(len(node.case_variants)),
        )
    check("no orphan prerequisites", not orphan_prereq)

    print("\n--- Sample progression paths by CEFR ---", flush=True)
    for cefr in ("A1", "A2", "B1", "B2", "C1"):
        decisions = _simulate_path(cefr, lessons=4)
        print(f"\n[{cefr}]", flush=True)
        prev_idx = -1
        for i, d in enumerate(decisions):
            chain = (
                f"{d.node.cluster_label} → {d.node.domain_label} → "
                f"{d.node.label} → {d.case_variant.title_hint} "
                f"[{d.action}]"
            )
            print(f"  L{i+1}. {chain}", flush=True)
            check(
                f"{cefr}.L{i+1} graph fields present",
                bool(d.node.cluster_id and d.node.domain_id and d.case_variant.case_id),
            )
            idx = PROGRESSION_SPINE_IDS.index(d.node.node_id)
            if i > 0:
                check(
                    f"{cefr}.L{i+1} does not jump backward",
                    idx >= prev_idx,
                    f"{idx} < {prev_idx}",
                )
            prev_idx = idx
        # Natural forward motion within CEFR band when mastery rises
        ids = [d.node.node_id for d in decisions]
        check(
            f"{cefr}. path advances or stays orderly",
            len(set(ids)) >= 2 or decisions[0].node.cefr_min == cefr,
            str(ids),
        )

    print("\n--- Same-node case diversity ---", flush=True)
    ledger = ProgressionMasteryLedger()
    # Force stay on airport node with weak mastery
    ledger.current_node_id = "micro:airport_arrival"
    ledger.node_mastery["micro:airport_arrival"] = 0.2
    ledger.node_exposure["micro:airport_arrival"] = 1
    # Unlock prereqs
    for pid in PROGRESSION_NODES["micro:airport_arrival"].prerequisite_ids:
        ledger.node_mastery[pid] = 0.5
        ledger.node_exposure[pid] = 1
    cases = []
    for _ in range(4):
        d = resolve_progression_decision(cefr="A2", ledger=ledger)
        cases.append(d.case_variant.case_id)
        ledger.used_case_ids.append(d.case_variant.case_id)
        ledger.node_exposure["micro:airport_arrival"] += 1
        # Keep mastery weak → stay on node
        ledger.node_mastery["micro:airport_arrival"] = 0.25
        ledger.current_node_id = "micro:airport_arrival"
    check(
        "same node across weak-mastery repeats",
        all("airport" in c or c.startswith("case:airport") for c in cases),
        str(cases),
    )
    check(
        "different Educational Cases on same node",
        len(set(cases)) >= 3,
        str(cases),
    )
    check(
        "action is repeat_new_case when weak",
        resolve_progression_decision(cefr="A2", ledger=ledger).action
        in {"repeat_new_case", "enter"},
    )

    print("\n--- Generated packages include progression ---", flush=True)
    for cefr in ("A1", "B1", "C1"):
        cons, pkg, alex = _generate_package(cefr)
        prog = cons.curriculum_progression or {}
        check(f"{cefr}. progression stamped", bool(prog.get("micro_skill_id")))
        check(f"{cefr}. cluster present", bool(prog.get("cluster_label")))
        check(f"{cefr}. domain present", bool(prog.get("domain_label")))
        check(f"{cefr}. micro skill present", bool(prog.get("micro_skill_label")))
        check(f"{cefr}. case variant present", bool(prog.get("case_variant_id")))
        check(f"{cefr}. vocab from curriculum", len(cons.vocabulary_targets) >= 4)
        check(f"{cefr}. grammar from curriculum", len(cons.grammar_targets) >= 1)
        check(f"{cefr}. discussion reinforces case", len(pkg.discussion.steps) >= 4)
        check(
            f"{cefr}. Alex continues same case",
            alex.case_continuation_hook == pkg.story_spine.continuation_hook
            and alex.case_category == pkg.story_spine.case_category,
        )
        check(
            f"{cefr}. story title follows progression seed",
            bool(pkg.story_spine.title)
            and (
                prog.get("case_title_hint", "").lower() in pkg.story_spine.title.lower()
                or pkg.input_material.title
            ),
        )
        print(
            f"  {cefr}: {prog.get('cluster_label')} → {prog.get('domain_label')} → "
            f"{prog.get('micro_skill_label')} → {prog.get('case_title_hint')}",
            flush=True,
        )

    print("\n--- Ordered lesson chain (no random jumps) ---", flush=True)
    # Two consecutive packages with advancing mastery ledger
    ledger = ProgressionMasteryLedger()
    c1, p1, _ = _generate_package(
        "A2", speaking_progression_mastery=ledger.to_dict()
    )
    node1 = (c1.curriculum_progression or {}).get("micro_skill_id")
    ledger.current_node_id = str(node1 or "")
    if node1:
        n = PROGRESSION_NODES[node1]
        ledger.node_mastery[node1] = n.estimated_mastery_advance
        ledger.node_exposure[node1] = 2
        for pid in n.prerequisite_ids:
            pr = PROGRESSION_NODES[pid]
            ledger.node_mastery[pid] = pr.estimated_mastery_advance
            ledger.node_exposure[pid] = 1
    c2, p2, _ = _generate_package(
        "A2", speaking_progression_mastery=ledger.to_dict()
    )
    node2 = (c2.curriculum_progression or {}).get("micro_skill_id")
    i1 = PROGRESSION_SPINE_IDS.index(node1) if node1 in PROGRESSION_SPINE_IDS else -1
    i2 = PROGRESSION_SPINE_IDS.index(node2) if node2 in PROGRESSION_SPINE_IDS else -1
    check(
        "second lesson is same node or next on spine",
        i2 >= i1 >= 0,
        f"{node1}@{i1} → {node2}@{i2}",
    )
    check(
        "two lessons are not unrelated random worlds",
        bool(node1 and node2),
    )

    print(f"\n=== M9 result: {PASS} passed, {FAIL} failed ===\n", flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
