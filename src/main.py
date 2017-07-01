from dice import RollDice, OfferReRoll
from game import Game, OfferActions
from player import AddPlayer, ShufflePlayers, CheckGameEnd

if __name__ == '__main__':

    game = Game()
    game = AddPlayer(5).apply(game)
    game = ShufflePlayers().apply(game)

    print(game)
    while True:
        print("{} to play".format(game.next_player))
        dice = RollDice().apply('')

        if CheckGameEnd().apply(game.players) is None:
            dice = OfferReRoll().apply(dice)
            OfferActions(game.players, game.next_player).apply(dice)
