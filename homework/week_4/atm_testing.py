from unittest import TestCase, main
from unittest.mock import patch

from homework.week_4.week_4 import validate_pin, withdraw, atm


class TestPinValidation(TestCase):
    def test_givenThePinIsValid_whenCallingValidatePin_thenNoExceptionIsThrown(self):
        correct_pin = 1234
        input_pin = 1234

        validate_pin(correct_pin, input_pin)

    def test_givenThatThePinIsNone_whenCallingValidatePin_thenAnExceptionIsThrown(self):
        correct_pin = 1234
        input_pin = None

        with self.assertRaises(AttributeError) as ex:
            validate_pin(correct_pin, input_pin)

        self.assertTrue(ex.exception)

    def test_givenThatThePinIsIncorrect_whenCallingIncorrectPin_thenAnExceptionIsThrown(self):
        correct_pin = 1234
        input_pin = 4321

        with self.assertRaises(ValueError) as ex:
            validate_pin(correct_pin, input_pin)

        self.assertTrue(ex.exception)


class TestWithdrawal(TestCase):
    def test_givenThatTheAmountRequestedIsValid_whenCallingValidAmount_thenNoExceptionIsThrown(self):
        requested_amount = 10
        account_balance = 100

        withdraw(requested_amount, account_balance)

    def test_givenTheRequestedAmountIsNegative_whenCallingNegativeAmount_thenAnExceptionIsThrown(self):
        requested_amount = -10
        account_balance = 100

        with self.assertRaises(ValueError) as ex:
            withdraw(requested_amount, account_balance)

        self.assertTrue(ex.exception)

    def test_givenThatTheRequestIsLargerThanAccountBalance_whenCallingLargerAmount_thenAnExceptionIsThrown(self):
        requested_amount = 150
        account_balance = 100

        with self.assertRaises(ValueError) as ex:
            withdraw(requested_amount, account_balance)

        self.assertTrue(ex.exception)


class TestAtm(TestCase):
    @patch('builtins.input', side_effect=[2846, 70])
    def test_givenAValidWithdrawalOf70_whenUsingTheAtm_thenTheRemainingAmountIs30(self, inputs):
        result = atm()
        self.assertEqual(result, 30)
        self.assertEqual(inputs.call_count, 2)

    @patch('builtins.input', side_effect=[2876, 3456, 3412])
    def test_giveAFailedAttemptToValidatePIN_whenUsingAtm_thenAnExceptionIsThrown(self, inputs):
        with self.assertRaises(ValueError) as ex:
            atm()
        self.assertEqual(inputs.call_count, 3)

    @patch('builtins.input', side_effect=[2846, None, -1, 0, 20])
    def test_givenThreeInvalidRequestedAmountFollowedByAValidAmount_whenUsingAtm_thenTheRemainingAmountIs80(self, inputs):
        result = atm()
        self.assertEqual(result, 80)


if __name__ == '__main__':
    main()

