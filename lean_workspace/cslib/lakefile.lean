import Lake
open Lake DSL

package llmsolution

-- The Lean Computer Science Library (https://github.com/leanprover/cslib).
-- Pulls in its pinned Mathlib transitively; do not also require mathlib here.
require cslib from git "https://github.com/leanprover/cslib" @ "main"

lean_lib LLMSolution
