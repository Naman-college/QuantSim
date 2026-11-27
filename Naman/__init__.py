"""
Naman/__init__.py - Package initializer for Naman's Backend & Application Bridge module.
Member: Naman (Backend and Bridging Everyone's Work to Complete the Final App).

Note: Submodules (metrics, engine, api, app) are imported directly to prevent
circular import chains between Rounak's strategies and Naman's BacktestEngine.
"""

__all__ = ["metrics", "engine", "api", "app"]  # Public submodules in Naman's package
