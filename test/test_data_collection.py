import unittest
from data.data_collection import MovieLogConsumer

class TestMethods(unittest.TestCase):

    def __init__(self, methodName: str = ...):
        super().__init__(methodName)
        self.movieLogConsumer = MovieLogConsumer(True)

    def test_processRateRequest(self):
        # Correct
        self.assertEqual(self.movieLogConsumer.processRateRequest(
            "2020-10-19T20:23:21,126786,GET /rate/a+civil+action+1998=3").user_id,
                         126786)
        self.assertEqual(self.movieLogConsumer.processRateRequest(
            "2020-10-19T20:23:21,126786,GET /rate/a+civil+action+1998=3").movie_id,
                         "a+civil+action+1998")
        self.assertEqual(self.movieLogConsumer.processRateRequest(
            "2020-10-19T20:23:21,126786,GET /rate/a+civil+action+1998=3").rate, 3)

        # rate < 0
        self.assertEqual(self.movieLogConsumer.processRateRequest(
            "2020-10-19T20:23:21,126786,GET /rate/a+civil+action+1998=-1"), {})
        # rate > 5
        self.assertEqual(self.movieLogConsumer.processRateRequest(
            "2020-10-19T20:23:21,126786,GET /rate/a+civil+action+1998=7"), {})
        # rate str
        self.assertEqual(self.movieLogConsumer.processRateRequest(
            "2020-10-19T20:23:21,126786,GET /rate/a+civil+action+1998=o"), {})
        # user_id str
        self.assertEqual(self.movieLogConsumer.processRateRequest(
            "2020-10-19T20:23:21,12s786,GET /rate/a+civil+action+1998=3"), {})

    def test_processDataRequest(self):
        # Correct
        print(self.movieLogConsumer.processDataRequest(
            "2020-10-16T00:50:09,940360,GET /data/m/psycho+1960/75.mpg"))
        print(self.movieLogConsumer.processDataRequest(
            "2020-10-16T00:50:09,940360,GET /data/m/psycho+1960/75.mpg"))
        self.assertEqual(self.movieLogConsumer.processDataRequest(
            "2020-10-16T00:50:09,940360,GET /data/m/psycho+1960/75.mpg").user_id, 940360)
        self.assertEqual(self.movieLogConsumer.processDataRequest(
            "2020-10-16T00:50:09,940360,GET /data/m/psycho+1960/75.mpg").movie_id,
                         "psycho+1960")
        self.assertEqual(self.movieLogConsumer.processDataRequest(
            "2020-10-16T00:50:09,940360,GET /data/m/psycho+1960/75.mpg").clips[0].clip,
                         "75.mpg")

        # user_id str
        self.assertEqual(self.movieLogConsumer.processDataRequest(
            "2020-10-16T00:50:09,940jj60,GET /data/m/psycho+1960/75.mpg"), {})


if __name__ == '__main__':
    unittest.main()
