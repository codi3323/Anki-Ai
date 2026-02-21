import sys
import unittest
from unittest.mock import MagicMock

# --- MOCK SETUP START ---
# We must mock missing dependencies before importing the module under test
sys.modules["pandas"] = MagicMock()
sys.modules["requests"] = MagicMock()
sys.modules["numpy"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["openai"] = MagicMock()
sys.modules["fitz"] = MagicMock()
sys.modules["tenacity"] = MagicMock()

# Define a Mock DataFrame that mimics pandas behavior required by deduplicate_cards
class MockLoc:
    def __init__(self, df):
        self.df = df

    def __getitem__(self, indices):
        # indices is a list of integers
        if not isinstance(indices, list):
            # fallback for single item access if needed, though not used in deduplicate_cards
            indices = [indices]

        # Filter the internal data based on indices
        # We need to make sure indices are valid, but for this mock we assume they are
        # because they come from enumerating the same dataframe.
        new_data = [self.df._data[i] for i in indices]
        return MockDataFrame(new_data)

class MockDataFrame:
    def __init__(self, data):
        # data should be a list of dicts for this mock to work easily
        self._data = data

    @property
    def empty(self):
        return len(self._data) == 0

    def iterrows(self):
        # Yields (index, row)
        # In pandas, row is a Series. Here we yield a dict which supports ['Key'] access.
        for i, row in enumerate(self._data):
            yield i, row

    @property
    def loc(self):
        return MockLoc(self)

    # For debugging/assertion convenience
    def to_dict(self, orient='records'):
        if orient == 'records':
            return self._data
        return {}

    def __len__(self):
        return len(self._data)

# Apply the mock to sys.modules
sys.modules["pandas"].DataFrame = MockDataFrame

# --- MOCK SETUP END ---

# Now import the function to test
from utils.data_processing import deduplicate_cards

class TestDeduplicateCards(unittest.TestCase):

    def test_no_existing_questions(self):
        """Test with no existing questions: should return all cards."""
        data = [
            {"Front": "Question 1", "Back": "Answer 1"},
            {"Front": "Question 2", "Back": "Answer 2"}
        ]
        df = MockDataFrame(data)
        existing = []

        result = deduplicate_cards(df, existing)

        self.assertEqual(len(result), 2)
        self.assertEqual(result.to_dict(), data)

    def test_exact_match_removal(self):
        """Test exact match removal."""
        data = [
            {"Front": "Question 1", "Back": "Answer 1"},
            {"Front": "Question 2", "Back": "Answer 2"}
        ]
        df = MockDataFrame(data)
        existing = ["Question 1"]

        result = deduplicate_cards(df, existing)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.to_dict()[0]["Front"], "Question 2")

    def test_case_insensitive_match(self):
        """Test case-insensitive and whitespace-insensitive matching."""
        data = [
            {"Front": "  question 1  ", "Back": "Answer 1"},
            {"Front": "Question 2", "Back": "Answer 2"}
        ]
        df = MockDataFrame(data)
        existing = ["Question 1"] # Matches "  question 1  "

        result = deduplicate_cards(df, existing)

        self.assertEqual(len(result), 1)
        self.assertEqual(result.to_dict()[0]["Front"], "Question 2")

    def test_internal_deduplication(self):
        """Test deduplication within the new batch of cards."""
        data = [
            {"Front": "Question 1", "Back": "Answer 1"},
            {"Front": "Question 1", "Back": "Answer 1 (Copy)"},
            {"Front": "Question 2", "Back": "Answer 2"}
        ]
        df = MockDataFrame(data)
        existing = []

        result = deduplicate_cards(df, existing)

        self.assertEqual(len(result), 2)
        # Should keep the first "Question 1"
        self.assertEqual(result.to_dict()[0]["Back"], "Answer 1")
        self.assertEqual(result.to_dict()[1]["Front"], "Question 2")

    def test_empty_input(self):
        """Test with empty input DataFrame."""
        df = MockDataFrame([])
        existing = ["Question 1"]

        result = deduplicate_cards(df, existing)

        self.assertTrue(result.empty)

    def test_mixed_scenario(self):
        """Test mixed scenario with existing matches and internal duplicates."""
        data = [
            {"Front": "Existing Q", "Back": "A1"}, # Matches existing
            {"Front": "New Q1", "Back": "A2"},    # New
            {"Front": "New Q1", "Back": "A3"},    # Internal duplicate
            {"Front": "New Q2", "Back": "A4"}     # New
        ]
        df = MockDataFrame(data)
        existing = ["existing q"]

        result = deduplicate_cards(df, existing)

        self.assertEqual(len(result), 2)
        expected = [
            {"Front": "New Q1", "Back": "A2"},
            {"Front": "New Q2", "Back": "A4"}
        ]
        self.assertEqual(result.to_dict(), expected)

if __name__ == '__main__':
    unittest.main()
