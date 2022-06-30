from unittest import TestCase
from assessment_2 import find_pair


class TestFindPairSum(TestCase):
    def test_givenAValidInput_whenCallingFindPairFunction_thenNoErrorIsThrown(self):
        num_list = [3, 5, -4, 8, 11, 1, -1, 6]
        target_sum = 10

        result = find_pair(num_list, target_sum)

        self.assertEqual([11, -1], result)

    def test_givenAnEmptyArray_whenCallingFindPairFunction_thenAnEmptyArrayIsReturned(self):
        num_list = []
        target_sum = 10

        result = find_pair(num_list, target_sum)

        self.assertEqual([], result)

    def test_givenANoneVariable_WhenCallingPairFunction_thenAnErrorIsThrown(self):
        num_list = [3, 5, -4, 8, 11, 1, -1, 6]
        target_sum = None

        with self.assertRaises(TypeError) as ex:
            find_pair(num_list, target_sum)
        self.assertTrue(ex.exception)

    def test_givenANoneList_WhenCallingPairFunction_thenAnErrorIsThrown(self):
        num_list = None
        target_sum = 10

        with self.assertRaises(TypeError) as ex:
            find_pair(num_list, target_sum)
        self.assertTrue(ex.exception)
