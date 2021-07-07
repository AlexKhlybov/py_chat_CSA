import argparse
import unittest

from server import createParser, get_response


class TestServerFunction(unittest.TestCase):
    def test_createParser(self):
        parser = argparse.ArgumentParser
        self.assertIsInstance(createParser(), parser)

    def testsrvresponse(self):
        self.assertEqual(get_response(True), {"response": 200})
        self.assertEqual(get_response(False), {"response": 400, "error": "Bad Request"})


if __name__ == "__main__":
    unittest.main()
