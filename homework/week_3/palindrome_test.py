from unittest import TestCase

from palindrome import is_palindrome


class TestPalindrome(TestCase):
    def test_givenAStringThatIsNone_whenCallingIsaPalindrome_thenITReturnsFalse(self):
        self.assertEqual(is_palindrome(None), False)

    def test_givenAStringThatIsBlank_whenCallingIsaPalindrome_thenItReturnsFalse(self):
        self.assertEqual(is_palindrome(' '), False)

    #     this is a blank string

    def test_givenAStringThatIsEmpty_whenCallingIsaPalindrome_thenItReturnsFalse(self):
        self.assertEqual(is_palindrome(''), False)

    def test_givenAPalindrome_whenCallingIsPalindrome_thenItReturnsTrue(self):
        self.assertEqual(is_palindrome("hannah"), True)

    def test_givenAStringThatIsNotAPalindrome_whenCallingIsPalindrome_thenItReturnsFalse(self):
        self.assertEqual(is_palindrome("ingrid"), False)

    def test_givenAPalindromeWithAnExtraSpace_whenCallingIsPalindrome_thenItReturnsTrue(self):
        self.assertEqual(is_palindrome("hannah "), True)

    def test_givenAPalindromeStartingWithACapitalLetter_whenCallingIsPalindrome_thenItReturnsTrue(self):
        self.assertEqual(is_palindrome("Hannah"), True)

    def test_givenAPalindromeWithEvenNoCharacters_whenCallingIsPalindrome_thenItReturnsTrue(self):
        self.assertEqual(is_palindrome("hannah"), True)

    def test_givenAPalindromeWithOddNoCharacters_whenCallingIsPalindrome_thenItReturnsTrue(self):
        self.assertEqual(is_palindrome("Capac"), True)



