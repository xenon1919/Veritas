class ResearchAgentError(Exception):
    """Base class for all agent_core errors."""


class SearchError(ResearchAgentError):
    """Raised when the web search provider fails."""


class LLMError(ResearchAgentError):
    """Raised when the LLM call fails."""
