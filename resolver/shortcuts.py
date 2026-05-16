from resolver.models import ShortcutDefinition


SHORTCUT_REGISTRY = {

    "/routine": ShortcutDefinition(
        trigger="/routine",

        expansion="""
        Build a professional dermatologist skincare routine.

        Include:
        - cleanser
        - treatment
        - moisturizer
        - sunscreen

        Consider the following user request:
        """,

        temperature=0.3,
        max_tokens=700,
        use_memory=True
    ),

    "/ingredient": ShortcutDefinition(
        trigger="/ingredient",

        expansion="""
        Explain this skincare ingredient scientifically.

        Include:
        - benefits
        - risks
        - irritation potential
        - suitable skin types

        Ingredient:
        """,

        temperature=0.2,
        max_tokens=500,
        use_memory=False
    ),

    "/acne": ShortcutDefinition(
        trigger="/acne",

        expansion="""
        Provide professional skincare guidance for acne concerns.

        Avoid medical diagnosis.

        Include gentle skincare recommendations.

        User request:
        """,

        temperature=0.3,
        max_tokens=600,
        use_memory=True
    ),

    "/safe": ShortcutDefinition(
        trigger="/safe",

        expansion="""
        Analyze skincare safety and allergy concerns.

        Mention possible irritants and patch testing advice.

        User request:
        """,

        temperature=0.2,
        max_tokens=600,
        use_memory=True
    )
}