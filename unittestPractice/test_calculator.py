import unittest
from calculator import *

class TestCalculator(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        print("start test")

    @classmethod
    def tearDownClass(self):
        print("end test")

    
    def test_add(self):
        self.assertEqual(add(3,5),8)
        self.assertEqual(add(-1,1),0)

    def test_subtract(self):
        self.assertEqual(subtract(10,5),5)
        self.assertEqual(subtract(-1,1),-2)

    def test_multiply(self):
        self.assertEqual(multiply(3,5),15)
        self.assertEqual(multiply(-1,1),-1)

    def test_divide(self):
        self.assertEqual(divide(10,5),2)
        self.assertEqual(divide(-1,1),-1)

# if __name__ == "__main__":
#     unittest.main()