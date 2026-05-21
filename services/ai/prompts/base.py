from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class PromptDefinition:
    name: str
    system: str
    parameters: dict[str, Any] = field(default_factory=dict)
    output_format: dict[str, Any] | None = None
    description: str = ""

    @property
    def temperature(self) -> float:
        return float(self.parameters.get("temperature", 0.7))

    @property
    def max_tokens(self) -> int:
        return int(self.parameters.get("max_tokens", 4096))

    def to_system_message(self, **variables: Any) -> dict[str, str]:
        content = self.system
        for key, value in variables.items():
            content = content.replace(f"{{{{{key}}}}}", str(value))
        return {"role": "system", "content": content}


class PromptTemplate:
    """Legacy .txt template with {{variable}} substitution."""

    def __init__(self, template: str, variables: list[str] | None = None) -> None:
        self.template = template
        self.variables = variables or []

    def render(self, **kwargs: Any) -> str:
        rendered = self.template
        for key, value in kwargs.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def to_message(self, role: str = "system", **kwargs: Any) -> dict[str, str]:
        return {"role": role, "content": self.render(**kwargs)}


class PromptManager:
    """Load prompts from /prompts — supports .yaml (preferred) and .txt (legacy)."""

    def __init__(self, prompts_dir: str | None = None) -> None:
        self.prompts_dir = Path(prompts_dir) if prompts_dir else Path("prompts")
        self._txt_cache: dict[str, PromptTemplate] = {}
        self._yaml_cache: dict[str, PromptDefinition] = {}

    def load_yaml(self, name: str) -> PromptDefinition:
        if name in self._yaml_cache:
            return self._yaml_cache[name]

        path = self.prompts_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"YAML prompt not found: {name}")

        with path.open(encoding="utf-8") as f:
            data = yaml.safe_load(f)

        prompt = PromptDefinition(
            name=data.get("name", name),
            system=data.get("system", ""),
            parameters=data.get("parameters", {}),
            output_format=data.get("output_format"),
            description=data.get("description", ""),
        )
        self._yaml_cache[name] = prompt
        return prompt

    def load_txt(self, name: str) -> PromptTemplate:
        if name in self._txt_cache:
            return self._txt_cache[name]

        path = self.prompts_dir / "system" / f"{name}.txt"
        if not path.exists():
            path = self.prompts_dir / f"{name}.txt"
        if not path.exists():
            raise FileNotFoundError(f"Text prompt not found: {name}")

        template = path.read_text(encoding="utf-8")
        prompt = PromptTemplate(template=template)
        self._txt_cache[name] = prompt
        return prompt

    def load(self, name: str) -> PromptDefinition | PromptTemplate:
        yaml_path = self.prompts_dir / f"{name}.yaml"
        if yaml_path.exists():
            return self.load_yaml(name)
        return self.load_txt(name)

    def get_system_prompt(self, name: str, **variables: Any) -> str:
        loaded = self.load(name)
        if isinstance(loaded, PromptDefinition):
            return loaded.to_system_message(**variables)["content"]
        return loaded.render(**variables)

    def list_prompts(self) -> list[str]:
        names: set[str] = set()
        for path in self.prompts_dir.glob("*.yaml"):
            names.add(path.stem)
        system_dir = self.prompts_dir / "system"
        if system_dir.exists():
            for path in system_dir.glob("*.txt"):
                names.add(path.stem)
        return sorted(names)


def get_prompt_manager() -> PromptManager:
    try:
        from app.config import settings

        return PromptManager(prompts_dir=settings.prompts_dir)
    except ImportError:
        return PromptManager()


prompt_manager = get_prompt_manager()
