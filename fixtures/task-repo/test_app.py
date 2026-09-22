import unittest

from app import greeting


class GreetingTest(unittest.TestCase):
    def test_greeting(self):
        self.assertEqual(greeting("sandbox"), "hello, sandbox")
