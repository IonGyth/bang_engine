from collections import Counter
from enum import Enum
from typing import NamedTuple, Tuple, Optional

from bang_types import MAX_HEALTH, MAX_ARROWS

import daiquiri

daiquiri.setup()
logger = daiquiri.getLogger()


class Role(Enum):
    SHERIFF = 0
    VICE = 1
    RENEGADE = 2
    OUTLAW = 3


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


class PrintAllPlayers(object):
    @staticmethod
    def apply(players: Tuple[Player]):
        for player in players:
            logger.debug(player)


class PrintPlayer(object):
    @staticmethod
    def apply(player: Player):
        logger.debug(player)


class CheckGameEnd(object):
    def apply(self, players: Tuple[Player, ...]):
        return self.prompt(players)

    @staticmethod
    def prompt(players: Tuple[Player, ...]) -> Optional[Role]:
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
    def apply(self, player_no: int) -> Player:
        for player in self.players:
            if player.player_no == player_no:
                return player


class _UpdatePlayer(NamedTuple):
    players: Tuple[Player]
    player: Player


class UpdatePlayers(_UpdatePlayer):
    def apply(self) -> Tuple[Player, ...]:
        return tuple(player if player.player_no != self.player.player_no else self.player for player in self.players)


class _ResolveArrows(NamedTuple):
    players: Tuple[Player]
    player: Player


class ResolveArrows(_ResolveArrows):
    def apply(self) -> Player:
        new_life = self.player.life - self.player.arrows
        player = self.player._replace(life=new_life)
        player = player._replace(arrows=0)

        return player


class _TakeArrow(NamedTuple):
    players: Tuple[Player, ...]
    player: Player


class TakeArrow(_TakeArrow):
    def apply(self, quantity: int) -> Tuple[Player, ...]:
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        for _ in range(0, quantity):
            player = player._replace(arrows=player.arrows + 1)

            if self.check_resolve(players):
                player = ResolveArrows(players).apply()

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def check_resolve(players: Tuple[Player, ...]) -> bool:
        no_of_arrows = 0
        for player in players:
            no_of_arrows += player.arrows

        return no_of_arrows >= MAX_ARROWS


class _RemoveArrow(NamedTuple):
    players: Tuple[Player]
    player: Player


class RemoveArrow(_RemoveArrow):
    def apply(self, quantity: int) -> Tuple[Player, ...]:
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        if self.isvalid(player, quantity):
            new_arrows = player.arrows - quantity
            player = player._replace(arrows=new_arrows)
        else:
            logger.debug("Not able to remove an arrow from player {}".format(player.player_no))

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def isvalid(player, quantity: int) -> bool:
        return player.arrows - quantity >= 0


class _LoseLife(NamedTuple):
    players: Tuple[Player, ...]
    player: Player


class LoseLife(_LoseLife):
    def apply(self, quantity: int) -> Tuple[Player, ...]:
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        if self.isvalid(player, quantity):
            new_life = player.life - quantity
            player = player._replace(life=new_life)
        else:
            logger.debug("This player is dead!")

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def isvalid(player: Player, quantity: int) -> bool:
        return player.life - quantity >= 0


class _GainLife(NamedTuple):
    players: Tuple[Player]
    player: Player


class GainLife(_GainLife):
    def apply(self, quantity: int) -> Tuple[Player, ...]:
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        if self.isvalid(player, quantity):
            new_life = player.life + quantity
            player = player._replace(life=new_life)
        else:
            logger.debug("This player is on max health!")

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def isvalid(player: Player, quantity: int) -> bool:
        return player.life + quantity <= MAX_HEALTH


class _BlowUp(NamedTuple):
    players: Tuple[Player]
    player: Player


class BlowUp(_BlowUp):
    def apply(self, quantity: int) -> Tuple[Player, ...]:
        players = self.players
        player = GetPlayer(players).apply(int(self.player.player_no))

        new_life = player.life - quantity
        player = player._replace(life=new_life)

        return UpdatePlayers(players, player).apply()
