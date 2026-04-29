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

LEAN_PROMPT_STYLES = {
    'naive': (
        "Implement {algorithm} in Lean 4 and prove: {lean_property}."
        "Do not use Mathlib or sorry."
    ),

    'structured':(
        "Implement {algorithm} in Lean 4.\n\n"
        "Requirements:\n"
        "- Do NOT import or use Mathlib\n"
        "- Define appropriate types for input and output\n"
        "- Handle edge cases: {edge_cases}\n"
        "- {extra_requirements}\n\n"
        "Then prove the following property about your implementation:\n"
        "{lean_property}\n\n"
        "Do not use sorry anywhere. Your response should contain ONLY Lean 4 code"
    ),

    'chain_of_thought':(
        "Implement {algorithm} in Lean 4.\n\n"
        "First, explain your approach to the implementation.\n"
        "Then, write the complete implementation.\n"
        "Then explain your proof strategy.\n"
        "Finally, prove: {lean_property}\n\n"
        "Do not use Mathlib or sorry"
    )
}

def build_prompt(style: str, language: str, algorithm: str, **kwargs):
    if language.lower() == 'lean 4':
        template = LEAN_PROMPT_STYLES[style]
    else:
        template = PROMPT_STYLES[style]

    return template.format(
        algorithm=algorithm,
        language=language,
        **kwargs
        )