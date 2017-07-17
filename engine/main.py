from dice import TurnRoll
from game import Game, DoAction
from player import AddPlayer, ShufflePlayers, CheckGameEnd

import daiquiri

daiquiri.setup()
logger = daiquiri.getLogger()


if __name__ == '__main__':

    game = Game()
    game = AddPlayer(5).apply(game)
    game = ShufflePlayers().apply(game)

    logger.debug(game)
    while True:
        logger.debug("{} to play".format(game.next_player))
        dice, players = TurnRoll(game.players, game.next_player).apply()

        if CheckGameEnd().apply(game.players) is None:
            DoAction(game.players, game.next_player).apply(dice)
