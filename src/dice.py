import random
from collections import namedtuple, Counter
from enum import Enum

from const import (
    NO_OF_DICE,
    SIDES_OF_DICE,
    NO_OF_REROLLS,
)


class Die(Enum):
    BEER = 0
    SHOT1 = 1
    SHOT2 = 2
    ARROW = 3
    GATLING = 4
    DYNAMITE = 5


class Dice(namedtuple('_Dice', ['dice'])):
    pass

Dice.__new__.__defaults__ = ("",)


class RollDice(object):
    @staticmethod
    def apply(dice):
        print("**** REROLLING ****")
        reroll_how_many = NO_OF_DICE - len(dice)

        for _ in range(0, reroll_how_many):
            dice += str(random.randint(0, SIDES_OF_DICE - 1))

        return dice


class OfferReRoll(object):
    def apply(self, dice):
        for reroll in range(0, NO_OF_REROLLS):
            dice = self.prompt(dice)

            if len(dice) == NO_OF_DICE:
                # if no dice have been rerolled
                break

            dice = RollDice().apply(dice)

        return dice

    def prompt(self, dice):
        while True:
            print(' '.join([Die(int(die)).name for die in dice]))

            reroll_hint = ''.join(['{} = {}, '.format(die.value, die.name) for die in Die])
            reroll = input("Reroll what? " + reroll_hint)

            if not self.validate(dice, reroll):
                print("Invalid choice. Try again.")
            else:
                for num in list(reroll):
                    dice = dice.replace(num, '')

                break

        return dice

    @staticmethod
    def validate(dice, reroll):
        """
        Validate the dice we have been told to reroll

        :param dice: current dice that have been rolled
        :param reroll: values of dice we have been told to reroll
        :return: True if it is valid otherwise False
        """
        c_dice = Counter(dice)
        c_reroll = Counter(reroll)

        return (
            str(Die.DYNAMITE.value) not in reroll
            and all([c_dice[dice] >= num for dice, num in c_reroll.most_common()])
        )
