import random
from collections import Counter
from enum import Enum
from typing import NamedTuple, Tuple

from bang_types import (
    NO_OF_DICE,
    SIDES_OF_DICE,
    NO_OF_REROLLS,
)
from player import (
    GetPlayer,
    TakeArrow,
    LoseLife,
    Player,
)

import daiquiri

daiquiri.setup()
logger = daiquiri.getLogger()


class Die(Enum):
    BEER = 0
    SHOT1 = 1
    SHOT2 = 2
    ARROW = 3
    GATLING = 4
    DYNAMITE = 5


class _Dice(NamedTuple):
    dice: tuple = ()


class Dice(_Dice):
    def __str__(self):
        return ' '.join([Die(int(die)).name for die in self.current_roll])

    def __len__(self):
        return len(self.current_roll)

    @property
    def current_roll(self) -> ():
        """
        Get the current state of the dice

        :return: dice roll
        """
        return self.dice[-1] if len(self.dice) else ''

    def add(self, roll: ()) -> ():
        """
        Add a roll to the history of rolls

        :param roll: the roll to add
        :return: the dice history
        """
        return self.dice + (roll,)

    def resolve(self, d_type: Die) -> ():
        """
        Remove a single dice from the pool of rolled dice.
        This is probably because that die has been resolved.

        :param d_type: type of die that has been resolved
        :return: active dice that can be resolved.
        """
        return self.add(self.current_roll.replace(str(d_type.value), '', 1))

    def check_resolve(self, d_type: Die) -> int:
        """
        Check how many of a certain type of die can be resolved

        :param d_type: type of die
        :return: number of dice
        """
        c_current_roll = Counter(self.current_roll)
        return c_current_roll[str(d_type.value)]

    def arrows(self) -> int:
        c_current_roll = Counter(self.current_roll)
        return c_current_roll[str(Die.ARROW.value)]

    def dynamites(self) -> int:
        c_current_roll = Counter(self.current_roll)
        return c_current_roll[str(Die.DYNAMITE.value)]

    def blown_up(self) -> bool:
        """
        Check if the player should have blown up.
        """
        return bool(self.dynamites() // 3)

    def roll(self) -> ():
        """
        Roll the unwanted dice

        :return: dice history
        """
        roll = ''
        for _ in range(len(self), NO_OF_DICE):
            roll += str(random.randint(0, SIDES_OF_DICE - 1))

        return self.add(self.current_roll + roll)

    def pick_reroll(self, reroll: str) -> ():
        current_roll = self.current_roll
        for num in list(reroll):
            current_roll = current_roll.replace(num, '')

        return self.add(current_roll)

    def to_dict(self) -> dict:
        """
        Return a dict of the current state of the dice.

        :return: dict of dice
        """
        c_current_roll = Counter(self.current_roll)
        return {d.name: c_current_roll[str(d.value)] for d in Die}


class _TurnRoll(NamedTuple):
    players = Tuple[Player, ...]
    player = Player


class TurnRoll(_TurnRoll):
    def apply(self):
        dice = ()
        players = self.players

        logger.debug("**** ROLLING ****")
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

    def reroll(self, dice: ()) -> ():
        while True:
            logger.debug(Dice(dice))

            reroll_hint = ', '.join(['{}={}'.format(die.value, die.name) for die in Die])
            reroll = input("Reroll what? " + reroll_hint)

            if not self.isvalid(dice, reroll):
                logger.debug("Invalid choice. Try again.")
            elif reroll:
                dice = Dice(dice).pick_reroll(reroll)
                dice = Dice(dice).roll()
                break
            else:
                break

        return dice

    @staticmethod
    def isvalid(dice: (), reroll: ()) -> bool:
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

    def check_arrows(self, dice: (), players: Tuple[Player, ...]) -> Tuple[Player, ...]:
        player = GetPlayer(players).apply(int(self.player.p_id))

        return TakeArrow(Dice(dice).arrows()).apply(self.players, player)

    def check_blown_up(self, dice: (), players: Tuple[Player, ...]) -> Tuple[Player, ...]:
        player = GetPlayer(players).apply(int(self.player.p_id))

        if Dice(dice).blown_up():
            if LoseLife(players, player).isvalid(player, 1):
                return LoseLife(players, player).apply(1)
        return players
