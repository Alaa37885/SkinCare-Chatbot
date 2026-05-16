from resolver.models import ResolvedInput


def resolve_shortcut(
    raw_input: str,
    registry: dict
) -> ResolvedInput:

    cleaned = raw_input.strip()

    for trigger, definition in registry.items():

        if cleaned.startswith(trigger):

            suffix = cleaned[
                len(trigger):
            ].strip()

            expanded_prompt = f"""
            {definition.expansion}

            {suffix}
            """

            return ResolvedInput(
                prompt=expanded_prompt,
                shortcut_used=trigger,
                temperature=definition.temperature,
                max_tokens=definition.max_tokens,
                use_memory=definition.use_memory
            )

    return ResolvedInput(
        prompt=raw_input
    )