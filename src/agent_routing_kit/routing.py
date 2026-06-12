from dataclasses import dataclass, field
from re import findall


Risk = str


@dataclass(frozen=True)
class Capability:
    name: str
    domain: str
    description: str
    keywords: tuple[str, ...]
    risk: Risk = "public"


@dataclass(frozen=True)
class RouteResult:
    task: str
    matches: tuple[tuple[Capability, int], ...] = field(default_factory=tuple)

    @property
    def primary(self) -> Capability | None:
        return self.matches[0][0] if self.matches else None

    def to_dict(self) -> dict:
        return {
            "task": self.task,
            "primary": self.primary.name if self.primary else None,
            "matches": [
                {
                    "name": capability.name,
                    "domain": capability.domain,
                    "description": capability.description,
                    "risk": capability.risk,
                    "score": score,
                }
                for capability, score in self.matches
            ],
        }

    def to_markdown(self) -> str:
        if not self.matches:
            return f"Task: {self.task}\n\nNo matching public capability found."

        lines = [f"Task: {self.task}", "", "Route:"]
        for capability, score in self.matches:
            lines.append(
                f"- {capability.name} ({capability.domain}, score {score}): "
                f"{capability.description}"
            )
        return "\n".join(lines)


def default_capabilities() -> tuple[Capability, ...]:
    return (
        Capability(
            name="backend-engineering",
            domain="engineering",
            description="APIs, services, persistence, auth boundaries, and testable backend logic.",
            keywords=("api", "backend", "service", "database", "auth", "server", "endpoint"),
        ),
        Capability(
            name="frontend-engineering",
            domain="engineering",
            description="Interfaces, dashboards, browser behavior, accessibility, and interaction design.",
            keywords=("ui", "frontend", "react", "dashboard", "browser", "component", "css"),
        ),
        Capability(
            name="python-packaging",
            domain="engineering",
            description="Python packages, CLIs, pyproject metadata, import boundaries, and tests.",
            keywords=("python", "package", "cli", "pytest", "pyproject", "wheel", "module"),
        ),
        Capability(
            name="documentation",
            domain="publishing",
            description="READMEs, contributing guides, public positioning, release notes, and handoffs.",
            keywords=("readme", "docs", "documentation", "contributing", "license", "release"),
        ),
        Capability(
            name="quality-review",
            domain="quality",
            description="Code review, regression checks, risk notes, and verification gates.",
            keywords=("review", "test", "verify", "qa", "lint", "regression", "coverage"),
        ),
        Capability(
            name="research-synthesis",
            domain="research",
            description="Source review, comparison, summarization, and technical synthesis.",
            keywords=("research", "compare", "summarize", "synthesis", "paper", "source"),
        ),
        Capability(
            name="private-corridor",
            domain="governance",
            description="Private-only work that should not be published as a standalone utility.",
            keywords=("secret", "credential", "private", "broker", "payload", "reverse", "corp"),
            risk="private",
        ),
        Capability(
            name="restricted-operation",
            domain="governance",
            description="Restricted workflows that require a separate private module and review lane.",
            keywords=("exploit", "evasion", "persistence", "live", "covert", "offensive"),
            risk="restricted",
        ),
    )


def route_task(
    task: str,
    capabilities: tuple[Capability, ...] | None = None,
    *,
    include_private: bool = False,
    max_results: int = 3,
) -> RouteResult:
    if max_results <= 0:
        raise ValueError("max_results must be positive")

    catalog = capabilities or default_capabilities()
    words = set(findall(r"[a-z0-9]+", task.lower()))
    scored: list[tuple[Capability, int]] = []

    for capability in catalog:
        if capability.risk != "public" and not include_private:
            continue
        score = sum(1 for keyword in capability.keywords if keyword.lower() in words)
        if capability.name.replace("-", " ") in task.lower():
            score += 2
        if score:
            scored.append((capability, score))

    scored.sort(key=lambda item: (-item[1], item[0].name))
    return RouteResult(task=task, matches=tuple(scored[:max_results]))
