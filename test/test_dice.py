import unittest
from unittest import (
    TestCase,
)

from dice import Dice


class TestDice(TestCase):

    def test_dice_add_once(self):
        self.assertEqual(
            Dice().add('01234'),
            ('01234',),
        )

    def test_dice_add_twice(self):
        dice = Dice().add('01234')

        self.assertEqual(
            Dice(dice).add('01'),
            ('01234', '01'),
        )

    def test_dice_check_blown_up_false(self):
        dice = Dice().add('01234')

        self.assertFalse(
            Dice(dice).blown_up(),
        )

    def test_dice_check_blown_up_almost(self):
        dice = Dice().add('01255')

        self.assertFalse(
            Dice(dice).blown_up(),
        )

    def test_dice_check_blown_up_true(self):
        dice = Dice().add('01555')

        self.assertTrue(
            Dice(dice).blown_up(),
        )

    def test_dice_to_dict_simple(self):
        dice = Dice().add('01234')

        self.assertEqual(
            Dice(dice).to_dict(),
            dict(BEER=1, SHOT1=1, SHOT2=1, ARROW=1, GATLING=1, DYNAMITE=0)
        )

    def test_dice_to_dict_all_arrows(self):
        dice = Dice().add('33333')

        self.assertEqual(
            Dice(dice).to_dict(),
            dict(BEER=0, SHOT1=0, SHOT2=0, ARROW=5, GATLING=0, DYNAMITE=0)
        )


if __name__ == '__main__':
    unittest.main()
