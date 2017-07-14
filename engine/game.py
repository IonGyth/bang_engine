from random import shuffle
from typing import NamedTuple, Tuple, List

from bang_types import MAX_ARROWS, NO_OF_PLAYERS
from dice import Die, Dice
from player import (
    LoseLife,
    RemoveArrow,
    GainLife,
    Role,
    GetPlayer,
    PrintAllPlayers,
    Player,
)

import daiquiri

daiquiri.setup()
logger = daiquiri.getLogger()

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


class _Game(NamedTuple):
    players: Tuple[Player] = ()
    moves: tuple = ()


class Game(_Game):
    def __new__(cls, players=None, moves=None):
        return super(Game, cls).__new__(cls, players or []  , moves or [])

    @property
    def next_player(self):
        if not self.moves:
            for player in self.players:
                if player.role == Role.SHERIFF:
                    sheriff = player
                    break

            player_index = self.players.index(sheriff)
            return self.players[player_index % NO_OF_PLAYERS]

        last_move = self.moves[-1]
        last_player = last_move.player
        return clockwise_player(self.players, last_player, 1)

    @property
    def num_players(self):
        return len(self.players)

    def to_dict(self):
        return dict(
            players=[{p.player_no: p.to_dict()} for p in self.players],
            moves=[]
        )


def clockwise_player(players: List[Player], player: Player, n: int) -> Player:
    i = players.index(player)
    while n:
        i = (i + 1) % len(players)
        if players[i] is not player:
            n -= 1
    return players[i]


def counterclockwise_player(players: List[Player], player: Player, n: int) -> Player:
    i = players.index(player)
    while n:
        i = (i - 1 if i > 0 else len(players) - 1) % len(players)
        if players[i] is not player:
            n -= 1
    return players[i]


class _AddPlayer(NamedTuple):
    num: int


class AddPlayer(_AddPlayer):
    def apply(self, game: Game) -> Game:
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

    def isvalid(self, game: Game) -> bool:
        return game.num_players + self.num <= max(add_which_role.keys())


class ShufflePlayers(object):
    @staticmethod
    def apply(game: Game) -> Game:
        """
        Shuffle the players in the game
        :param game: shuffle the players in the game
        :return: the game with the players shuffled
        """
        shuffle(game.players)

        return game


class _OfferActions(NamedTuple):
    players: Tuple[Player] = ()
    player: Player = None


class OfferActions(_OfferActions):
    def apply(self, dice: ()) -> List[Player]:
        while sum(self.can_resolve(dice)):
            players = self.players
            resolve = self.prompt(dice)

            if resolve == str(Die.BEER.value):
                players = DoBeer(self.player).prompt(players)
            elif resolve == str(Die.SHOT1.value):
                players = DoShot1(self.player).prompt(players)
            elif resolve == str(Die.SHOT2.value):
                players = DoShot2(self.player).prompt(players)
            elif resolve == str(Die.GATLING.value):
                players = DoGatlings(self.player).prompt(players)

            dice = Dice(dice).resolve(resolve)

            PrintAllPlayers().apply(self.players)

        return players

    @staticmethod
    def can_resolve(dice: ()):
        beers = Dice(dice).check_resolve(str(Die.BEER.value))
        shot1 = Dice(dice).check_resolve(str(Die.SHOT1.value))
        shot2 = Dice(dice).check_resolve(str(Die.SHOT2.value))
        gatlings = Dice(dice).check_resolve(str(Die.GATLING.value)) // 3

        return beers, shot1, shot2, gatlings

    def prompt(self, dice: ()):
        beers, shot1, shot2, gatlings = self.can_resolve(dice)

        if beers:
            logger.debug('(0) You have rolled {} beers'.format(beers))

        if shot1:
            logger.debug('(1) You have rolled {} 1shots'.format(shot1))

        if shot2:
            logger.debug('(2) You have rolled {} 2shots'.format(shot2))

        if gatlings:
            logger.debug('(3) You have rolled {} gatlings'.format(beers))

        return input("Which would you like to resolve? ")


class _DoBeer(NamedTuple):
    player: Player


class DoBeer(_DoBeer):
    def prompt(self, players: List[Player]) -> List[Player]:
        for player in players:
            logger.debug("({}) player {}".format(player.player_no, player))

        while True:
            player_no = self.get_response()
            player = GetPlayer(players).apply(int(player_no))

            if GainLife(players, player).isvalid(player, 1):
                players = GainLife(players, player).apply(1)
                break

        return players

    @staticmethod
    def get_response():
        return input("Which player would you like to beer?")


class _DoShot1(NamedTuple):
    player: Player


class DoShot1(_DoShot1):
    def prompt(self, players: List[Player]) -> List[Player]:

        shoot_players = {
            clockwise_player(players, self.player, 1),
            counterclockwise_player(players, self.player, 1),
        }

        for player in shoot_players:
            logger.debug("({}) player {}".format(player.player_no, player))

        while True:
            player_no = self.get_response()
            player = GetPlayer(players).apply(int(player_no))

            if player not in shoot_players:
                logger.debug("Invalid choice. Try again.")
                continue

            if LoseLife(players, player).isvalid(player, 1):
                players = LoseLife(players, player).apply(1)
                break

        return players

    @staticmethod
    def get_response():
        return input("Which player would you like to shoot?")


class _DoShot2(NamedTuple):
    player: Player


class DoShot2(_DoShot2):
    def prompt(self, players: List[Player]) -> List[Player]:

        shoot_players = {
            clockwise_player(players, self.player, 2),
            counterclockwise_player(players, self.player, 2),
        }
        for player in shoot_players:
            logger.debug("({}) player {}".format(player.player_no, player))

        while True:
            player_no = self.get_response()
            player = GetPlayer(players).apply(int(player_no))

            if player not in shoot_players:
                logger.debug("Invalid choice. Try again.")
                continue

            if LoseLife(player, player).isvalid(player, 1):
                players = LoseLife(players, player).apply(1)
                break

        return players

    @staticmethod
    def get_response():
        return input("Which player would you like to shoot?")


class _DoGatlings(NamedTuple):
    player: Player


class DoGatlings(_DoGatlings):
    def apply(self, players: List[Player]) -> List[Player]:

        for player in players:
            if player != self.player.player_no:
                players = LoseLife(player, player).apply(1)
            else:
                players = RemoveArrow(players, player).apply(MAX_ARROWS)

        return players

    def prompt(self, players):
        return self.apply(players)


class _ResolveArrows(NamedTuple):
    players: Tuple[Player]


class ResolveArrows(_ResolveArrows):
    def apply(self):
        for player in self.players:
            ResolveArrows(player).apply()

    def isvalid(self):
        no_of_arrows = 0
        for player in self.players:
            no_of_arrows += player.arrows

        return no_of_arrows >= MAX_ARROWS
