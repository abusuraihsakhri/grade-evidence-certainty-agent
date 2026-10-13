"""Deterministic local demo responder (no external model provider is implemented)."""
from .base import PHIGuard


class MockLLM:
    def __init__(self, system_name: str = "Grade Evidence Certainty Agent"):
        self.system_name = system_name

    def invoke(self, prompt: str) -> str:
        PHIGuard.assert_no_phi(prompt)
        return (
            f"[{self.system_name} local demo]: Query received: {prompt[:60]!r}. "
            "No scientific verification, diagnosis, or model inference has been performed."
        )


class LLMFactory:
    """Only the local mock responder is currently available."""

    @staticmethod
    def create(provider: str = "mock", system_name: str = "Grade Evidence Certainty Agent"):
        if str(provider).lower() in ("mock", "deterministic", "test"):
            return MockLLM(system_name)
        raise ValueError("External LLM providers are not implemented; use provider='mock'")
