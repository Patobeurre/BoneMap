import ast
import unittest

class TestAst(unittest.TestCase):

    def test_literal_eval(self):
        s = "VAR=(1,1)"
        splited = s.strip().split('=')

        value = ast.literal_eval(splited[1])
        print(type(value))
        self.assertIsInstance(value, tuple)
