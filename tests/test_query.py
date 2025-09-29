import unittest
from utils.vector_db import VectorDB

class TestQuery(unittest.TestCase):
    def test_query(self):
        vector_db = VectorDB()
        result = vector_db.query("What is my name?")
        self.assertEqual(result["documents"][0], "Daniel Halwell")