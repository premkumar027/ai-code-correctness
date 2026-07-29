PROMPT_STYLES = {
    'naive': 'Write {algorithm} in {language}.',

    'structured': (
        "Write {algorithm} in {language}.\n\n"
        "Specifications:\n"
        "- Use {data_structure} as the primary data structure\n"
        "- Handle edge cases: {edge_cases}\n"
        "- Do not use any external libraries\n"
        "- Include type hints and a docstring\n"
        "- {extra_requirements}\n\n"
        "Your response should contain ONLY the code, no explanations"
    ),

    'chain_of_thought': (
        'Write {algorithm} in {language}.\n'
        'First, explain your approach step by step.\n'
        'Then, write the complete implementation.\n'
        'Finally, analyze the time and space complexity'

    )
}

LEAN_LIBRARY_HINTS = {
    "none":    "Do not import or use any external libraries. Implement everything from scratch.",
    "mathlib": "You may use Mathlib. Add `import Mathlib` at the top of your file.",
    "cslib":   "You may use Cslib. Add the appropriate import at the top of your file.",
}

LEAN_PROMPT_STYLES = {
    'naive': (
        "Implement {algorithm} in Lean 4 and prove: {lean_property}.\n"
        "{library_hint}\n"
        "Do not use sorry."
    ),

    'structured': (
        "Implement {algorithm} in Lean 4.\n\n"
        "Requirements:\n"
        "- {library_hint}\n"
        "- Define appropriate types for input and output\n"
        "- Handle edge cases: {edge_cases}\n"
        "- {extra_requirements}\n\n"
        "Then prove the following property about your implementation:\n"
        "{lean_property}\n\n"
        "Do not use sorry anywhere. Your response should contain ONLY Lean 4 code."
    ),

    'chain_of_thought': (
        "Implement {algorithm} in Lean 4.\n\n"
        "First, explain your approach to the implementation.\n"
        "Then, write the complete implementation.\n"
        "Then explain your proof strategy.\n"
        "Finally, prove: {lean_property}\n\n"
        "{library_hint}\n"
        "Do not use sorry."
    ),
}


# ---------------------------------------------------------------------------
# Python "self-tests" arm
#
# The model writes the implementation AND its own test suite, mirroring the Lean
# arm where it writes the implementation AND the theorem AND the proof. The
# hidden human suite in tasks/*/ is NEVER mentioned to the model and never fed
# back — it is scored silently as ground truth.
# ---------------------------------------------------------------------------

SELF_TEST_COUNT = 10

_INTERFACE_BLOCK = (
    "The implementation must expose exactly this API — names, argument order and\n"
    "return shapes matter, because your code will be called through it:\n\n"
    "{interface}\n"
)

# Mechanical plumbing so the two artifacts can be separated and executed. This is
# harness format, not problem-solving help (the Lean equivalent is "no sorry").
_OUTPUT_CONTRACT = (
    "OUTPUT FORMAT — return exactly two Python code blocks, in this order and\n"
    "nothing else after them:\n\n"
    "```python\n"
    "# === IMPLEMENTATION ===\n"
    "<the implementation>\n"
    "```\n\n"
    "```python\n"
    "# === TESTS ===\n"
    "import pytest\n"
    "from solution import <the names listed above>\n\n"
    "<exactly " + str(SELF_TEST_COUNT) + " test functions, each named test_...>\n"
    "```\n\n"
    "Rules for the test block:\n"
    "- Write exactly " + str(SELF_TEST_COUNT) + " plain `def test_...()` functions using bare `assert`.\n"
    "- Import the implementation from the module `solution`. Never redefine it in\n"
    "  the test block, and never import from any other local module.\n"
    "- The tests must pass against a correct implementation of the task, and must\n"
    "  be strong enough to fail against a subtly wrong one.\n"
)

PYTHON_SELF_TEST_STYLES = {
    'naive': (
        "Write {algorithm} in Python, together with a test suite for it.\n\n"
        "{interface_block}\n"
        "{output_contract}"
    ),

    'structured': (
        "Write {algorithm} in Python, together with a test suite for it.\n\n"
        "Specifications:\n"
        "- Use {data_structure} as the primary data structure\n"
        "- Handle edge cases: {edge_cases}\n"
        "- Do not use any external libraries (pytest in the test block is fine)\n"
        "- Include type hints and a docstring\n"
        "- {extra_requirements}\n\n"
        "{interface_block}\n"
        "Your tests should cover the normal behaviour and the edge cases listed above.\n\n"
        "{output_contract}"
    ),

    'chain_of_thought': (
        "Write {algorithm} in Python, together with a test suite for it.\n\n"
        "First, explain your approach to the implementation step by step.\n"
        "Then explain what properties and edge cases a test suite must check to be\n"
        "convinced the implementation is correct.\n"
        "Finally, write the implementation and the tests.\n\n"
        "{interface_block}\n"
        "{output_contract}"
    ),
}


def build_self_test_prompt(style: str, algorithm: str, interface: str, **kwargs):
    """Prompt for the Python arm where the model also authors its own tests."""
    template = PYTHON_SELF_TEST_STYLES[style]
    return template.format(
        algorithm=algorithm,
        interface_block=_INTERFACE_BLOCK.format(interface=interface.strip()),
        output_contract=_OUTPUT_CONTRACT,
        **kwargs,
    )


def build_prompt(style: str, language: str, algorithm: str, lean_library: str = "none",
                 interface: str | None = None, **kwargs):
    if language.lower() == 'lean 4':
        template = LEAN_PROMPT_STYLES[style]
        library_hint = LEAN_LIBRARY_HINTS.get(lean_library, LEAN_LIBRARY_HINTS["none"])
        return template.format(
            algorithm=algorithm,
            language=language,
            library_hint=library_hint,
            **kwargs,
        )
    else:
        template = PROMPT_STYLES[style]
        prompt = template.format(
            algorithm=algorithm,
            language=language,
            **kwargs,
        )
        # Optional (opt-in via --with-interface). The already-collected given-tests
        # data was generated WITHOUT this, so enabling it makes runs incomparable
        # with the existing 93 combos unless that arm is re-run.
        if interface:
            prompt += "\n\n" + _INTERFACE_BLOCK.format(interface=interface.strip())
        return prompt