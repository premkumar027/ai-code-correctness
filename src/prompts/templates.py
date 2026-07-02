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


def build_prompt(style: str, language: str, algorithm: str, lean_library: str = "none", **kwargs):
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
        return template.format(
            algorithm=algorithm,
            language=language,
            **kwargs,
        )