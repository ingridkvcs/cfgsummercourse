from unittest import TestCase
from assessment_pratcice import find_pair

class AssessmentPracticeTest(TestCase):
    def test_givenAnEmptyList_whenCallingFindPair_AnErrorIsThrown(self):
        param1 = []
        param2 = 5

        result = find_pair(param1, param2)

        self.assertIsNone(result)

    def test_givenAValidInput_whenCallingFindPair_NoErrorIsThrown(self):
        param1 = [1, 5, 2, 5, 3, 23, 5]
        param2 = 4

        result = find_pair(param1, param2)

        self.assertEqual((1, 5), result)

    def test_givenNoParameterInput_whenCallingFindPair_ANoneResultIsThrown(self):
        param1 = [1, 5, 2, 5, 3, 23, 5]
        param2 = None

        result = find_pair(param1, param2)

        self.assertIsNone(result)

    def test_givenAStringIsPassed_whenCallingFairPair_AnErrorisThrown(self):
        param1 = [1, 5, 2, 5, 3, 23, 5]
        param2 = '4'

        result = find_pair(param1, param2)

        self.assertIsNone(result)








