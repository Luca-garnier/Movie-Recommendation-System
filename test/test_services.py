import unittest
from api import get_recommendations
from api.utils import DATA_PATH, MODEL_PATH, load_pickle

MODEL = load_pickle(MODEL_PATH)
DATA = load_pickle(DATA_PATH)


class TestSERVICESMethods(unittest.TestCase):
    def test_verifyUserId(self):
        self.assertEqual(len(set(get_recommendations(MODEL, DATA, 1))), 10)


if __name__ == "__main__":
    unittest.main()
