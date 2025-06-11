import unittest
import os

try:
    from farg.insight_generation_recommendation.insight_generator import InsightGenerator
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))
    from farg.insight_generation_recommendation.insight_generator import InsightGenerator

class TestInsightGenerator(unittest.TestCase):
    """
    Unit tests for the InsightGenerator class.
    """

    def setUp(self):
        """Initialize the generator for each test."""
        self.generator = InsightGenerator()
        self.sample_financial_analysis = {"ratios": {"npm": 0.1}, "trends": {"revenue": "up"}}
        self.sample_competitor_analysis = {"comparison": "on_par"}
        self.sample_swot = {"strengths": ["S1"], "weaknesses": ["W1"], "opportunities": ["O1"], "threats": ["T1"]}

    def test_import_insight_generator(self):
        """Test that InsightGenerator can be imported and instantiated."""
        self.assertIsInstance(self.generator, InsightGenerator)

    def test_generate_insights_returns_list_of_strings(self):
        """Test that generate_insights returns a list of strings."""
        result = self.generator.generate_insights(
            self.sample_financial_analysis, self.sample_competitor_analysis, self.sample_swot
        )
        self.assertIsInstance(result, list)
        if result: # If list is not empty
            self.assertIsInstance(result[0], str)
        # Check if it returns the expected number of placeholder insights
        # This depends on the dummy implementation, adjust if it changes
        self.assertTrue(len(result) >= 3, "Should return a few placeholder insights.")


    def test_generate_insights_invalid_input_types(self):
        """Test generate_insights with invalid input types."""
        with self.assertRaises(TypeError):
            self.generator.generate_insights("bad", {}, {}) # type: ignore
        with self.assertRaises(TypeError):
            self.generator.generate_insights({}, "bad", {}) # type: ignore
        with self.assertRaises(TypeError):
            self.generator.generate_insights({}, {}, "bad") # type: ignore

    def test_generate_insights_empty_inputs(self):
        """Test generate_insights with empty dictionaries as inputs."""
        try:
            result = self.generator.generate_insights({}, {}, {})
            self.assertIsInstance(result, list, "Should return a list even with empty inputs.")
            # Depending on implementation, it might return an empty list or specific "no data" insights
            # For current dummy, it returns the standard placeholder list.
            self.assertTrue(len(result) > 0 if not result else True)
        except Exception as e:
            self.fail(f"generate_insights failed with empty dict inputs: {e}")


if __name__ == '__main__':
    unittest.main()
