import random
from collections import namedtuple, Counter
from enum import Enum

from bang_types import (
    NO_OF_DICE,
    SIDES_OF_DICE,
    NO_OF_REROLLS,
)
from player import (
    GetPlayer,
    TakeArrow,
    LoseLife,
)


class Die(Enum):
    BEER = 0
    SHOT1 = 1
    SHOT2 = 2
    ARROW = 3
    GATLING = 4
    DYNAMITE = 5


class Dice(namedtuple('_Dice', ['dice'])):
    def __str__(self):
        return ' '.join([Die(int(die)).name for die in self.current_roll])

    def __len__(self):
        return len(self.current_roll)

    @property
    def current_roll(self):
        return self.dice[-1] if len(self.dice) else ''

    def add(self, roll):
        return self.dice + (roll,)

    def arrows(self):
        c_current_roll = Counter(self.current_roll)
        return c_current_roll[str(Die.ARROW.value)]

    def dynamites(self):
        c_current_roll = Counter(self.current_roll)
        return c_current_roll[str(Die.DYNAMITE.value)]

    def blown_up(self):
        return self.dynamites() // 3

    def roll(self):
        roll = ''
        for _ in range(len(self), NO_OF_DICE):
            roll += str(random.randint(0, SIDES_OF_DICE - 1))

        return self.add(self.current_roll + roll)

    def pick_reroll(self, reroll):
        current_roll = self.current_roll
        for num in list(reroll):
            current_roll = current_roll.replace(num, '')

        return self.add(current_roll)


Dice.__new__.__defaults__ = ((),)


class TurnRoll(namedtuple('_TurnRoll', ['players', 'player'])):
    def apply(self):
        dice = ()
        players = self.players

        print("**** ROLLING ****")
        dice = Dice(dice).roll()

        players = self.check_arrows(dice, players)
        players = self.check_blown_up(dice, players)

        for reroll in range(0, NO_OF_REROLLS):
            dice = self.reroll(dice)

            players = self.check_arrows(dice, players)
            players = self.check_blown_up(dice, players)
            if len(dice) < 3 + (2*reroll):
                # if no dice have been rerolled
                break

        return dice, players

    def reroll(self, dice):
        while True:
            print(Dice(dice))

            reroll_hint = ''.join(['{}={}, '.format(die.value, die.name) for die in Die])
            reroll = input("Reroll what? " + reroll_hint)

            if not self.validate(dice, reroll):
                print("Invalid choice. Try again.")
            elif reroll:
                dice = Dice(dice).pick_reroll(reroll)
                dice = Dice(dice).roll()
                break
            else:
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
        c_dice = Counter(Dice(dice).current_roll)
        c_reroll = Counter(reroll)

        return (
            str(Die.DYNAMITE.value) not in reroll
            and all([c_dice[dice] >= num for dice, num in c_reroll.most_common()])
        )

    def check_arrows(self, dice, players):
        player = GetPlayer(players).apply(int(self.player.player_no))

        return TakeArrow(self.players, player).apply(Dice(dice).arrows())

    def check_blown_up(self, dice, players):
        player = GetPlayer(players).apply(int(self.player.player_no))

        if Dice(dice).blown_up():
            if LoseLife(player).validate(1):
                return LoseLife(player).apply(1)
        return players
