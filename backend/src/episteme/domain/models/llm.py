"""The LLM port."""

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Sequence

    from episteme.domain.agents.state import Message
    from episteme.domain.data_policy.levels import DataLevel


@runtime_checkable
class LLM(Protocol):
    """A language model that streams its reply as text chunks."""

    @property
    def max_data_level(self) -> DataLevel:
        """The most sensitive data level this model may receive."""
        ...

    def stream(self, messages: Sequence[Message]) -> AsyncIterator[str]:
        """Stream the reply to the conversation, chunk by chunk."""
        ...
