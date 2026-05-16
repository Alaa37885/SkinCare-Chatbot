from pydantic import BaseModel


class ShortcutDefinition(BaseModel):

    trigger: str

    expansion: str

    temperature: float = 0.3

    max_tokens: int = 500

    use_memory: bool = True


class ResolvedInput(BaseModel):

    prompt: str

    shortcut_used: str | None = None

    temperature: float = 0.3

    max_tokens: int = 500

    use_memory: bool = True