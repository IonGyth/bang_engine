from collections import Counter
from enum import Enum
from typing import NamedTuple, Tuple, Optional

from bang_types import MAX_HEALTH, MAX_ARROWS

import daiquiri

logger = daiquiri.getLogger()


class Role(Enum):
    SHERIFF = 0
    VICE = 1
    RENEGADE = 2
    OUTLAW = 3


class _Player(NamedTuple):
    p_id: int = None
    life: int = 8
    arrows: int = 0
    role: Role = None


class Player(_Player):
    def __str__(self):
        return "Player {} hp:{} ap:{}".format(self.p_id, self.life, self.arrows)

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
    def apply(self, p_id: int) -> Player:
        for player in self.players:
            if player.p_id == p_id:
                return player


class _UpdatePlayer(NamedTuple):
    players: Tuple[Player]
    player: Player


class UpdatePlayers(_UpdatePlayer):
    def apply(self) -> Tuple[Player, ...]:
        return tuple(player if player.p_id != self.player.p_id else self.player for player in self.players)


class ResolveAllArrows:
    def apply(self, players: Tuple[Player, ...]) -> Tuple[Player, ...]:
        if self.isvalid(players):
            upd_players = ()
            for player in players:
                upd_players = upd_players + (ResolveArrows().apply(player),)

        return upd_players

    @staticmethod
    def isvalid(players: Tuple[Player, ...]) -> bool:
        no_of_arrows = 0
        for player in players:
            no_of_arrows += player.arrows

        return no_of_arrows >= MAX_ARROWS


class ResolveArrows:
    @staticmethod
    def apply(player: Player) -> Player:
        new_life = player.life - player.arrows
        return player._replace(life=new_life, arrows=0)


class _TakeArrow(NamedTuple):
    quantity: int


class TakeArrow(_TakeArrow):
    def apply(self, players: Tuple[Player, ...], player: Player) -> Tuple[Player, ...]:
        for _ in range(0, self.quantity):
            player = player._replace(arrows=player.arrows + 1)
            players = UpdatePlayers(players, player).apply()

            if self.check_resolve(players):
                players = ResolveAllArrows().apply(players)
                player = GetPlayer(players).apply(player.p_id)

        return UpdatePlayers(players, player).apply()

    @staticmethod
    def check_resolve(players: Tuple[Player, ...]) -> bool:
        no_of_arrows = 0
        for player in players:
            no_of_arrows += player.arrows

        return no_of_arrows >= MAX_ARROWS


class _RemoveArrow(NamedTuple):
    quantity: int


class RemoveArrow(_RemoveArrow):
    def apply(self, players: Tuple[Player], player: Player) -> Tuple[Player, ...]:
        player = GetPlayer(players).apply(int(player.p_id))

        if self.isvalid(player, self.quantity):
            new_arrows = player.arrows - self.quantity
            player = player._replace(arrows=new_arrows)
        else:
            logger.debug("Not able to remove an arrow from player {}".format(player.p_id))

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
        player = GetPlayer(players).apply(int(self.player.p_id))

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
    quantity: int


class GainLife(_GainLife):
    def apply(self, players: Tuple[Player], player: Player) -> Tuple[Player, ...]:
        player = GetPlayer(players).apply(player.p_id)

        if self.isvalid(player, self.quantity):
            new_life = player.life + self.quantity
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
        player = GetPlayer(players).apply(int(self.player.p_id))

        new_life = player.life - quantity
        player = player._replace(life=new_life)

        return UpdatePlayers(players, player).apply()
