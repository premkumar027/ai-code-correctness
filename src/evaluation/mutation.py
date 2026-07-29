"""Mutation testing — how strong is a model-authored test suite?

The Lean arm has a blind spot: `compiles && no sorry` says nothing about whether
the theorem is *worth* proving. A model can state something trivially true and
prove it honestly. The Python analogue of that loophole is a test suite full of
weak assertions that its own implementation happens to satisfy.

Mutation testing closes it. For each task we take the known-correct
`tasks/<task>/reference.py`, introduce one small defect at a time (flip a
comparison, shift a constant, swap and/or), and keep only the defects that the
hidden human suite detects — proving each pooled mutant is a genuine, catchable
bug rather than an unreachable or semantically-equivalent edit.

A model's test suite is then run against each pooled mutant. Mutation score =
fraction of real bugs its tests catch. An escaped mutant is the direct
counterpart of a vacuous theorem: the artifact type-checks, but it does not
constrain the implementation.

The pool is expensive to build (one pytest run per candidate) and completely
determined by reference.py, so it is cached under results/mutants/.
"""

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path

from src.evaluation.python_runner import run as run_hidden_suite
from src.evaluation.python_runner import run_pair

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TASKS_DIR = PROJECT_ROOT / "tasks"
CACHE_DIR = PROJECT_ROOT / "results" / "mutants"

# Mutants are cheap to detect but a bad one can loop forever (`while i < n` ->
# `while i <= n`), so runs against mutants get a short leash. The hidden suites
# finish in well under a second on the unmutated reference, so 10s is ample
# headroom; anything slower is a hang caused by the defect, which counts as
# detected either way. Pool building is dominated by these timeouts, so keeping
# the leash short is what makes it finish in minutes rather than an hour.
MUTANT_TIMEOUT = 10
MAX_MUTANTS = 12          # cap per task, keeps a full arm run to ~minutes
MAX_CANDIDATES = 140      # cap on AST sites probed while building the pool


# ---------------------------------------------------------------------------
# Mutation operators
# ---------------------------------------------------------------------------

# Each operator lists several replacements, not one. The order-reversing variants
# (Lt -> Gt, LtE -> GtE) matter most: they produce output of the right length and
# type but the wrong values, which is precisely the defect that type-and-length
# assertions cannot see. Without them the pool cannot separate a medium suite from
# a vacuous one.
_CMP_VARIANTS = {
    ast.Lt:    [ast.LtE, ast.Gt],
    ast.LtE:   [ast.Lt, ast.GtE],
    ast.Gt:    [ast.GtE, ast.Lt],
    ast.GtE:   [ast.Gt, ast.LtE],
    ast.Eq:    [ast.NotEq],
    ast.NotEq: [ast.Eq],
    ast.In:    [ast.NotIn],
    ast.NotIn: [ast.In],
    ast.Is:    [ast.IsNot],
    ast.IsNot: [ast.Is],
}

_BIN_VARIANTS = {
    ast.Add:      [ast.Sub, ast.Mult],
    ast.Sub:      [ast.Add],
    ast.Mult:     [ast.Add, ast.FloorDiv],
    ast.Div:      [ast.Mult],
    ast.FloorDiv: [ast.Mult, ast.Add],
    ast.Mod:      [ast.Mult],
}

_BOOL_VARIANTS = {ast.And: [ast.Or], ast.Or: [ast.And]}

# Non-commutative operators also get their operands swapped: `a - b` -> `b - a`
# keeps the shape of the result and changes only its value. Add is included
# because these tasks concatenate strings, where `s + e` and `e + s` differ; in a
# purely numeric context the swap is equivalent and the human-suite filter drops it.
_SWAPPABLE_BINOPS = (ast.Add, ast.Sub, ast.Div, ast.FloorDiv, ast.Mod)

# Calls whose result is passed straight through when the call is removed.
# Dropping `sorted(...)` attacks the row-ordering convention ("one oracle answer
# per experiment, ordered by sorted(E)"), which is part of the task spec and
# invisible to any test that only checks lengths and types.
_UNWRAPPABLE_CALLS = ("sorted", "reversed")


class _Mutator(ast.NodeTransformer):
    """Apply exactly one mutation, at the site with index `target`.

    Sites are numbered by traversal order. Passing target=-1 mutates nothing and
    leaves `self.count` holding the total number of available sites.
    """

    def __init__(self, target: int = -1):
        self.target = target
        self.count = 0
        self.description = ""

    def _hit(self, description: str) -> bool:
        index = self.count
        self.count += 1
        if index == self.target:
            self.description = f"site {index}: {description}"
            return True
        return False

    def visit_Compare(self, node):
        self.generic_visit(node)
        for i, op in enumerate(node.ops):
            for variant in _CMP_VARIANTS.get(type(op), []):
                if self._hit(f"{type(op).__name__} -> {variant.__name__}"):
                    node.ops[i] = variant()
        return node

    def visit_BinOp(self, node):
        self.generic_visit(node)
        for variant in _BIN_VARIANTS.get(type(node.op), []):
            if self._hit(f"{type(node.op).__name__} -> {variant.__name__}"):
                node.op = variant()
        if isinstance(node.op, _SWAPPABLE_BINOPS):
            if self._hit(f"swap operands of {type(node.op).__name__}"):
                node.left, node.right = node.right, node.left
        return node

    def visit_BoolOp(self, node):
        self.generic_visit(node)
        for variant in _BOOL_VARIANTS.get(type(node.op), []):
            if self._hit(f"{type(node.op).__name__} -> {variant.__name__}"):
                node.op = variant()
        return node

    def visit_Call(self, node):
        self.generic_visit(node)
        name = getattr(node.func, "id", getattr(node.func, "attr", "call"))

        # Swapping the first two arguments preserves arity, so the call still
        # runs; only the answer is wrong. Keyword-free calls only.
        if len(node.args) >= 2 and not any(
            isinstance(a, ast.Starred) for a in node.args[:2]
        ):
            if self._hit(f"swap first two args of {name}()"):
                node.args[0], node.args[1] = node.args[1], node.args[0]

        # sorted(xs) -> xs : same elements, unspecified order.
        if (
            name in _UNWRAPPABLE_CALLS
            and len(node.args) == 1
            and not node.keywords
            and not isinstance(node.args[0], ast.Starred)
        ):
            if self._hit(f"drop {name}()"):
                return node.args[0]
        return node

    def visit_Constant(self, node):
        if isinstance(node.value, bool):
            if self._hit(f"{node.value} -> {not node.value}"):
                return ast.copy_location(ast.Constant(value=not node.value), node)
        elif isinstance(node.value, int):
            for delta in (1, -1):
                if self._hit(f"{node.value} -> {node.value + delta}"):
                    return ast.copy_location(
                        ast.Constant(value=node.value + delta), node
                    )
        return node


def _candidates(source: str) -> list[tuple[str, str]]:
    """Every single-site mutant of `source`, as (mutated_source, description)."""
    total = _Mutator(target=-1)
    total.visit(ast.parse(source))

    seen: set[str] = {source}
    out: list[tuple[str, str]] = []
    for i in range(min(total.count, MAX_CANDIDATES)):
        mutator = _Mutator(target=i)
        tree = mutator.visit(ast.parse(source))
        ast.fix_missing_locations(tree)
        try:
            mutated = ast.unparse(tree)
        except Exception:
            continue
        if mutated in seen:
            continue
        seen.add(mutated)
        out.append((mutated, mutator.description))
    return out


# ---------------------------------------------------------------------------
# Pool construction (cached)
# ---------------------------------------------------------------------------

def build_pool(task_name: str, force: bool = False, verbose: bool = False) -> list[dict]:
    """Mutants of the task reference that the hidden human suite detects.

    Two filters make the score meaningful:

    1. The human suite must detect the mutant. This proves the defect is real and
       catchable, not an unreachable or semantically-equivalent edit.
    2. The pool prefers *subtle* mutants — those that leave most of the human
       suite passing. Catastrophic mutants (which crash on any input) are caught
       even by vacuous type-and-length assertions, so they cannot tell a strong
       suite from a weak one. Measured on merge_sort, an AST-ordered pool scored a
       deliberately vacuous suite at 90%; ranking by subtlety is what gives the
       metric its spread.
    """
    cache_file = CACHE_DIR / f"{task_name}.json"
    if cache_file.exists() and not force:
        return json.loads(cache_file.read_text())["mutants"]

    reference = TASKS_DIR / task_name / "reference.py"
    if not reference.exists():
        return []

    source = reference.read_text(encoding="utf-8")
    candidates = _candidates(source)
    detected: list[dict] = []
    rejected = 0

    degenerate = 0
    for mutated, description in candidates:
        result = run_hidden_suite(mutated, task_name, timeout=MUTANT_TIMEOUT)
        if result.passed:
            rejected += 1
            if verbose:
                print(f"    {description:<40} skip (equivalent)")
            continue
        if result.total == 0:
            # The mutant breaks at import or collection time, so *any* test suite
            # detects it — including one that only checks a function is callable.
            # Keeping these would inflate every model's score by the same constant
            # and dilute the signal, so they are dropped rather than ranked last.
            degenerate += 1
            if verbose:
                print(f"    {description:<40} skip (degenerate: breaks on import)")
            continue
        detected.append({
            "code": mutated,
            "description": description,
            # How much of the human suite survives: higher = subtler defect.
            "human_passed": result.passed_count,
            "human_total": result.total,
        })
        if verbose:
            print(f"    {description:<40} keep "
                  f"(human {result.passed_count}/{result.total} still pass)")

    # Subtlest first, then a deterministic tie-break.
    detected.sort(key=lambda m: (-m["human_passed"], m["description"]))
    pool = detected[:MAX_MUTANTS]

    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(json.dumps({
        "task": task_name,
        "candidates_probed": len(candidates),
        "rejected_equivalent": rejected,
        "rejected_degenerate": degenerate,
        "detected": len(detected),
        "pooled": len(pool),
        "mutants": pool,
    }, indent=2))
    return pool


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

@dataclass
class MutationScore:
    total: int = 0
    caught: int = 0
    escaped: list[str] = field(default_factory=list)

    @property
    def score(self) -> float | None:
        return self.caught / self.total if self.total else None

    def __str__(self) -> str:
        if not self.total:
            return "no mutants"
        return f"{self.caught}/{self.total} mutants caught"


def score(task_name: str, test_code: str) -> MutationScore:
    """Fraction of pooled defects that `test_code` detects."""
    pool = build_pool(task_name)
    result = MutationScore(total=len(pool))
    for mutant in pool:
        run = run_pair(mutant["code"], test_code, timeout=MUTANT_TIMEOUT)
        # Anything other than a clean pass means the suite noticed: assertion
        # failure, error, or a hang caused by the defect.
        if run.passed:
            result.escaped.append(mutant["description"])
        else:
            result.caught += 1
    return result


if __name__ == "__main__":
    # Prebuild caches so an arm run doesn't pay for pool construction:
    #   uv run python -m src.evaluation.mutation [task ...]
    import sys

    from src.prompts.tasks import LEAN_ONLY_TASKS, TASKS

    targets = sys.argv[1:] or [t for t in TASKS if t not in LEAN_ONLY_TASKS]
    for task in targets:
        print(f"{task}:")
        pool = build_pool(task, verbose=True)
        print(f"  -> pooled {len(pool)} mutants\n")
