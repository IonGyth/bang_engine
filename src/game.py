from collections import namedtuple

from bang_types import MAX_ARROWS, NO_OF_PLAYERS
from dice import Die
from player import (
    LoseLife,
    RemoveArrow,
    GainLife,
    Role,
    GetPlayer,
    PrintAllPlayers,
)


class Game(namedtuple('_Game', ['players', 'moves'])):
    @property
    def next_player(self):
        if not self.moves:
            for player in self.players:
                if player.role == Role.SHERRIF:
                    sherrif = player
                    break

            player_index = self.players.index(sherrif)
            return self.players[player_index % NO_OF_PLAYERS]

        last_move = self.moves[-1]
        last_player = last_move.player

        player_index = self.players.index(last_player)
        return self.players[(player_index + 1) % NO_OF_PLAYERS]

    @property
    def num_players(self):
        return len(self.players)


Game.__new__.__defaults__ = ([], [])


class OfferActions(namedtuple('_OfferActions', ['players', 'player'])):
    def apply(self, dice):
        while sum(self.can_resolve(dice)):
            resolve = self.prompt(dice)

            if resolve == str(Die.BEER.value):
                DoBeer(self.player).prompt(self.players)
                dice = dice.replace(resolve, '', 1)

            elif resolve == str(Die.SHOT1.value):
                DoShot1(self.player).prompt(self.players)
                dice = dice.replace(resolve, '', 1)

            elif resolve == str(Die.SHOT2.value):
                DoShot2(self.player).prompt(self.players)
                dice = dice.replace(resolve, '', 1)

            elif resolve == str(Die.GATLING.value):
                DoGatlings(self.player).prompt(self.players)
                dice = dice.replace(resolve, '', 1)

            PrintAllPlayers().apply(self.players)

    @staticmethod
    def can_resolve(dice):
        beers = dice.count(str(Die.BEER.value))
        shot1 = dice.count(str(Die.SHOT1.value))
        shot2 = dice.count(str(Die.SHOT2.value))
        gatlings = dice.count(str(Die.GATLING.value)) // 3

        return beers, shot1, shot2, gatlings

    def prompt(self, dice):
        beers, shot1, shot2, gatlings = self.can_resolve(dice)

        if beers:
            print('(0) You have rolled {} beers'.format(beers))

        if shot1:
            print('(1) You have rolled {} 1shots'.format(shot1))

        if shot2:
            print('(2) You have rolled {} 2shots'.format(shot2))

        if gatlings:
            print('(3) You have rolled {} gatlings'.format(beers))

        return input("Which would you like to resolve? ")


class DoBeer(namedtuple('_DoBeer', ['player'])):
    @staticmethod
    def prompt(players):
        for player in players:
            print("({}) player {}".format(player.player_no, player))

        while True:
            player_no = input("Which player would you like to beer?")
            player = GetPlayer(players).apply(int(player_no))

            if GainLife(player).validate(1):
                GainLife(player).apply(1)


class DoShot1(namedtuple('_DoShot1', ['player'])):
    def prompt(self, players):

        shoot_players = (
            players[(self.player.player_no - 1) % NO_OF_PLAYERS],
            players[(self.player.player_no + 1) % NO_OF_PLAYERS],
        )

        for player in shoot_players:
            print("({}) player {}".format(player.player_no, player))

        while True:
            player_no = input("Which player would you like to shoot?")
            player = GetPlayer(players).apply(int(player_no))

            if LoseLife(player).validate(1):
                LoseLife(player).apply(1)
                break


class DoShot2(namedtuple('_DoShot2', ['player'])):
    def prompt(self, players):

        shoot_players = (
            players[(self.player.player_no - 2) % NO_OF_PLAYERS],
            players[(self.player.player_no + 2) % NO_OF_PLAYERS],
        )
        for player in shoot_players:
            print("({}) player {}".format(player.player_no, player))

        while True:
            player_no = input("Which player would you like to shoot?")
            player = GetPlayer(players).apply(int(player_no))

            if LoseLife(player).validate(1):
                LoseLife(player).apply(1)
                break


class DoGatlings(namedtuple('_DoGatlings', ['player'])):
    def apply(self, players):

        for player in players:
            if player != self.player.player_no:
                LoseLife(player).apply(1)
            else:
                RemoveArrow(player).apply(MAX_ARROWS)

        return input("Which player would you like to shoot?")

    def prompt(self, players):
        pass


class ResolveArrows(namedtuple('_ResolveArrows', ['players'])):
    def apply(self):
        for player in self.players:
            ResolveArrows(player).apply()

    def validate(self):
        no_of_arrows = 0
        for player in self.players:
            no_of_arrows += player.arrows

        return no_of_arrows >= MAX_ARROWS
