from collections import Counter
from enum import Enum
from random import shuffle
from typing import NamedTuple, Tuple

from bang_types import MAX_HEALTH, MAX_ARROWS

import daiquiri

daiquiri.setup()
logger = daiquiri.getLogger()


class Role(Enum):
    SHERIFF = 0
    VICE = 1
    RENEGADE = 2
    OUTLAW = 3


add_which_role = {
    1: Role.SHERIFF,
    2: Role.RENEGADE,
    3: Role.OUTLAW,
    4: Role.OUTLAW,
    5: Role.VICE,
    6: Role.OUTLAW,
    7: Role.VICE,
    8: Role.RENEGADE,
}


class _Player(NamedTuple):
    player_no: int = None
    life: int = 8
    arrows: int = 0
    role: Role = None


class Player(_Player):
    def __str__(self):
        return "Player {} hp:{} ap:{}".format(self.player_no, self.life, self.arrows)

    def to_dict(self):
        return dict(
            life=self.life,
            arrows=self.arrows,
            role=self.role.name,
        )


class _AddPlayer(NamedTuple):
    num: int


class AddPlayer(_AddPlayer):
    def apply(self, game):
        """
        This is used to add a new player to the game

        :param game: add the player to this game
        :return: the game with the added player
        """
        if self.isvalid(game):
            for _ in range(0, self.num):
                player_no = game.num_players + 1
                new_role = add_which_role[player_no]

                game.players.append(Player(player_no=player_no, role=new_role))
        else:
            logger.debug("Can't add more players to the game!")

        return game

    def isvalid(self, game):
        return game.num_players + self.num <= max(add_which_role.keys())


class ShufflePlayers(object):
    @staticmethod
    def apply(game):
        """
        Shuffle the players in the game
        :param game: shuffle the players in the game
        :return: the game with the players shuffled
        """
        shuffle(game.players)

        return game


class PrintAllPlayers(object):
    @staticmethod
    def apply(players):
        for player in players:
            logger.debug(player)


class PrintPlayer(object):
    @staticmethod
    def apply(player):
        logger.debug(player)


class CheckGameEnd(object):
    def apply(self, players):
        return self.prompt(players)

    @staticmethod
    def prompt(players):
        alive_roles = [player.role for player in players if player.life >= 0]
        alive_roles = Counter(alive_roles)

        if (
            not (alive_roles[Role.OUTLAW] + alive_roles[Role.RENEGADE]) and
            alive_roles[Role.SHERIFF]
        ):
            logger.debug("SHERIFF WINS")
            return Role.SHERIFF
        elif (
                alive_roles[Role.RENEGADE] == 1 and
            not (
                alive_roles[Role.SHERIFF] +
                alive_roles[Role.VICE] +
                alive_roles[Role.OUTLAW]
            )
        ):
            logger.debug("RENEGADE WIN")
            return Role.RENEGADE
        elif (
            not (alive_roles[Role.SHERIFF]) and
                alive_roles[Role.RENEGADE] != 1
        ):
            logger.debug("OUTLAW_WIN")
            return Role.OUTLAW

        return None


class _GetPlayer(NamedTuple):
    players: Tuple[Player]


class GetPlayer(_GetPlayer):
    def apply(self, player_no):
        for player in self.players:
            if player.player_no == player_no:
                return player


class _UpdatePlayer(NamedTuple):
    players: Tuple[Player]
    player: Player


class UpdatePlayers(_UpdatePlayer):
    def apply(self):
        return [player if player.player_no != self.player.player_no else self.player for player in self.players]


class _ResolveArrows(NamedTuple):
    players: Tuple[Player]
    player: Player


class ResolveArrows(_ResolveArrows):
    def apply(self):
        new_life = self.player.life - self.player.arrows
        player = self.player._replace(life=new_life)
        player = player._replace(arrows=0)

        return player


class _TakeArrow(NamedTuple):
    players: Tuple[Player]
    player: Player


class TakeArrow(_TakeArrow):
    def apply(self, quantity):
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        for _ in range(0, quantity):
            player = player._replace(arrows=player.arrows + 1)

            if self.check_resolve(players):
                player = ResolveArrows(players).apply()

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def check_resolve(players):
        no_of_arrows = 0
        for player in players:
            no_of_arrows += player.arrows

        return no_of_arrows >= MAX_ARROWS


class _RemoveArrow(NamedTuple):
    players: Tuple[Player]
    player: Player


class RemoveArrow(_RemoveArrow):
    def apply(self, quantity):
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        if self.isvalid(player, quantity):
            new_arrows = player.arrows - quantity
            player = player._replace(arrows=new_arrows)
        else:
            logger.debug("Not able to remove an arrow from player {}".format(player.player_no))

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def isvalid(player, quantity):
        return player.arrows - quantity >= 0


class _LoseLife(NamedTuple):
    players: Tuple[Player]
    player: Player


class LoseLife(_LoseLife):
    def apply(self, quantity):
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        if self.isvalid(player, quantity):
            new_life = player.life - quantity
            player = player._replace(life=new_life)
        else:
            logger.debug("This player is dead!")

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def isvalid(player, quantity):
        return player.life - quantity >= 0


class _GainLife(NamedTuple):
    players: Tuple[Player]
    player: Player


class GainLife(_GainLife):
    def apply(self, quantity):
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        if self.isvalid(player, quantity):
            new_life = player.life + quantity
            player = player._replace(life=new_life)
        else:
            logger.debug("This player is on max health!")

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def isvalid(player, quantity):
        return player.life + quantity <= MAX_HEALTH


class _BlowUp(NamedTuple):
    players: Tuple[Player]
    player: Player


class BlowUp(_BlowUp):
    def apply(self, quantity):
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        new_life = player.life - quantity
        player = player._replace(life=new_life)

        return UpdatePlayers(players, player).apply()
