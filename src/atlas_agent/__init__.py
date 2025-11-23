"""ATLAS Agent - AI Testing and Automation System using Claude's computer-use."""

__version__ = "0.1.0"

from atlas_agent.core import AtlasAgent, TestResult
from atlas_agent.config import AtlasConfig

__all__ = ["AtlasAgent", "TestResult", "AtlasConfig"]
