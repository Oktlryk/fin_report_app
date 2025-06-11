# insight_generation_recommendation/__init__.py

"""
The insight_generation_recommendation package is responsible for synthesizing
analysis results into actionable insights and generating strategic or
operational recommendations.

Modules:
    insight_generator: Generates insights from compiled analysis data.
    recommendation_engine: Produces recommendations based on insights and issues.
"""

from .insight_generator import InsightGenerator
from .recommendation_engine import RecommendationEngine

__all__ = [
    "InsightGenerator",
    "RecommendationEngine",
]

print("farg.insight_generation_recommendation package initialized")
