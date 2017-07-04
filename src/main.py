from dice import TurnRoll
from game import Game, OfferActions
from player import AddPlayer, ShufflePlayers, CheckGameEnd

if __name__ == '__main__':

    game = Game()
    game = AddPlayer(5).apply(game)
    game = ShufflePlayers().apply(game)

    print(game)
    while True:
        print("{} to play".format(game.next_player))
        dice = TurnRoll(game.players, game.next_player).apply()

        if CheckGameEnd().apply(game.players) is None:
            OfferActions(game.players, game.next_player).apply(dice)
