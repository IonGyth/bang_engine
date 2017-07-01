from collections import namedtuple, Counter
from enum import Enum
from random import shuffle

from const import MAX_HEALTH


class Role(Enum):
    SHERRIF = 0
    VICE = 1
    RENEGADE = 2
    OUTLAW = 3


add_which_role = {
    1: Role.SHERRIF,
    2: Role.RENEGADE,
    3: Role.OUTLAW,
    4: Role.OUTLAW,
    5: Role.VICE,
    6: Role.OUTLAW,
    7: Role.VICE,
    8: Role.RENEGADE,
}



class Player(namedtuple('_Player', ['player_no', 'life', 'arrows', 'role'])):
    def __str__(self):
        return "Player {} hp:{} ap:{}".format(self.player_no, self.life, self.arrows)

Player.__new__.__defaults__ = (None, 8, 0, None)


class AddPlayer(namedtuple('_AddPlayer', ['num'])):
    def apply(self, game):
        for _ in range(0, self.num):
            player_no = game.num_players + 1
            new_role = add_which_role[player_no]

            game.players.append(Player(player_no=player_no, role=new_role))

        return game


class ShufflePlayers(object):
    @staticmethod
    def apply(game):
        shuffle(game.players)

        return game


class PrintAllPlayers(object):
    @staticmethod
    def apply(players):
        for player in players:
            print(player)


class PrintPlayer(object):
    @staticmethod
    def apply(player):
        print(player)


class CheckGameEnd(object):
    def apply(self, players):
        return self.prompt(players)

    @staticmethod
    def prompt(players):
        alive_roles = [player.role for player in players if player.life >= 0]
        alive_roles = Counter(alive_roles)

        if (
            not (alive_roles[Role.OUTLAW] + alive_roles[Role.RENEGADE]) and
            alive_roles[Role.SHERRIF]
        ):
            print("SHERRIF WINS")
            return Role.SHERRIF
        elif (
            alive_roles[Role.RENEGADE] == 1 and
            not (
                alive_roles[Role.SHERRIF] +
                alive_roles[Role.VICE] +
                alive_roles[Role.OUTLAW]
            )
        ):
            print("RENEGADE WIN")
            return Role.RENEGADE
        elif (
            not (alive_roles[Role.SHERRIF]) and
            alive_roles[Role.RENEGADE] != 1
        ):
            print("OUTLAW_WIN")
            return Role.OUTLAW

        return None


class GetPlayer(namedtuple('_GetPlayer', ['players'])):
    def apply(self, player_no):
        for player in self.players:
            if player.player_no == player_no:
                return player


class TakeArrow(namedtuple('_TakeArrow', ['player'])):
    def apply(self, quantity):
        new_arrows = self.player.arrows + quantity
        self.player._replace(arrows=new_arrows)

        return self.player


class RemoveArrow(namedtuple('_RemoveArrow', ['player'])):
    def apply(self, quantity):
        if self.validate(quantity):
            new_arrows = self.player.arrows - quantity
            self.player._replace(arrows=new_arrows)
        else:
            print("Not able to remove an arrow from player {}".format(self.player.player_no))

        return self.player

    def validate(self, quantity):
        return self.player.arrows - quantity >= 0


class LoseLife(namedtuple('_LoseLife', ['player'])):
    def apply(self, quantity):
        if self.validate(quantity):
            new_life = self.player.life - quantity
            self.player._replace(life=new_life)
        else:
            print("This player is dead!")

        return self.player

    def validate(self, quantity):
        return self.player.life - quantity >= 0


class GainLife(namedtuple('_GainLife', ['player'])):
    def apply(self, quantity):
        if self.validate(quantity):
            new_life = self.player.life + quantity
            self.player._replace(life=new_life)
        else:
            print("This player is on max health!")

        return self.player

    def validate(self, quantity):
        return self.player.life + quantity < MAX_HEALTH


class BlowUp(namedtuple('_BlowUp', ['player'])):
    def apply(self, quantity):
        new_life = self.player.life - quantity
        self.player._replace(life=new_life)

        return self.player
