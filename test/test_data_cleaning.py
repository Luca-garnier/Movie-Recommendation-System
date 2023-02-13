import configparser
import unittest
from data.data_cleaning import DataCleaning
from data.db import get_connection


class TestMethods(unittest.TestCase):
    config = configparser.ConfigParser()

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.dataCleaning = DataCleaning(True)
        get_connection()

    def test_verifyMovieExists(self):
        print(self.dataCleaning.verifyMovieExistsSave("twelve+monkeys+1995"))
        self.assertTrue(self.dataCleaning.verifyMovieExistsSave("twelve+monkeys+1995"))
        self.assertFalse(self.dataCleaning.verifyMovieExistsSave("emma+1996"))

    def test_verifyUserExists(self):
        self.assertTrue(self.dataCleaning.verifyUserExistsSave(134243))
        self.assertFalse(self.dataCleaning.verifyUserExistsSave(0))

    def test_save_non_existing_user(self):
        pass

    def test_incorrect_data(self):
        pass


if __name__ == '__main__':
    unittest.main()
