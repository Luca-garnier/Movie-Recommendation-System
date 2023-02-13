import unittest
from api import verifyUserID

class TestAPIMethods(unittest.TestCase):

    def test_verifyUserId(self):
        self.assertEqual(verifyUserID('123'), 123)
        self.assertEqual(verifyUserID('1e123'), None)
        self.assertEqual(verifyUserID('-1'), None)

if __name__ == '__main__':
    unittest.main()
