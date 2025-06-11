import unittest
import os

try:
    from farg.insight_generation_recommendation.recommendation_engine import RecommendationEngine
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.insight_generation_recommendation.recommendation_engine import RecommendationEngine

class TestRecommendationEngine(unittest.TestCase):
    """
    Unit tests for the RecommendationEngine class.
    """

    def setUp(self):
        """Initialize the engine for each test."""
        self.engine = RecommendationEngine()
        self.sample_insights = ["Insight 1", "Insight 2"]
        self.sample_strategic_issues = {"issue1": "Strategic problem A"}
        self.sample_operational_issues = {"issueA": "Operational problem X"}

    def test_import_recommendation_engine(self):
        """Test that RecommendationEngine can be imported and instantiated."""
        self.assertIsInstance(self.engine, RecommendationEngine)

    def test_generate_recommendations_returns_list_of_dicts(self):
        """Test that generate_recommendations returns a list of dictionaries."""
        result = self.engine.generate_recommendations(
            self.sample_insights, self.sample_strategic_issues, self.sample_operational_issues
        )
        self.assertIsInstance(result, list)
        if result: # If list is not empty
            self.assertIsInstance(result[0], dict)
            self.assertIn("recommendation_id", result[0])
            self.assertIn("category", result[0])
            self.assertIn("recommendation", result[0])
            self.assertIn("justification", result[0])
        # Current dummy implementation returns a fixed number of recommendations
        self.assertTrue(len(result) >= 2, "Should return a few placeholder recommendations.")

    def test_generate_recommendations_invalid_input_types(self):
        """Test generate_recommendations with invalid input types."""
        with self.assertRaises(TypeError):
            self.engine.generate_recommendations("bad", {}, {}) # type: ignore
        with self.assertRaises(TypeError):
            self.engine.generate_recommendations([], "bad", {}) # type: ignore
        with self.assertRaises(TypeError):
            self.engine.generate_recommendations([], {}, "bad") # type: ignore
        with self.assertRaises(TypeError):
            self.engine.generate_recommendations(["bad_item_type", 123], {}, {}) # type: ignore

    def test_generate_recommendations_empty_inputs(self):
        """Test generate_recommendations with empty inputs."""
        try:
            result = self.engine.generate_recommendations([], {}, {})
            self.assertIsInstance(result, list)
            # Current dummy implementation adds a specific "further data analysis required" recommendation
            self.assertTrue(len(result) > 0, "Should return at least one generic recommendation for empty inputs.")
            if result:
                self.assertIn("further data analysis required", result[0].get("recommendation", "").lower())
        except Exception as e:
            self.fail(f"generate_recommendations failed with empty inputs: {e}")

if __name__ == '__main__':
    unittest.main()
