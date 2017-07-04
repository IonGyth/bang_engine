import unittest
from unittest import (
    TestCase,
)

from game import Game
from player import (
    AddPlayer,
    ShufflePlayers,
    GetPlayer,
    TakeArrow,
    UpdatePlayers,
    RemoveArrow,
    LoseLife,
    GainLife,
    BlowUp,
)


class TestPlayer(TestCase):
    def setUp(self):
        game = Game()
        if not game.num_players:
            game = AddPlayer(1).apply(game)
        self.game = ShufflePlayers().apply(game)
        self.players = self.game.players
        self.player = self.game.next_player

    def tearDown(self):
        self.game = None
        self.players = None
        self.player = None

    def test_get_player(self):
        self.assertEqual(
            GetPlayer(self.players).apply(int(self.player.player_no)),
            self.player
        )

    def test_take_arrow(self):
        self.assertEqual(
            TakeArrow(self.players, self.player).apply(5),
            UpdatePlayers(self.players, self.player._replace(arrows=5)).apply()
        )

    def test_remove_arrow(self):
        players = UpdatePlayers(self.players, self.player._replace(arrows=5)).apply()
        self.assertEqual(
            RemoveArrow(players, self.player).apply(5),
            UpdatePlayers(self.players, self.player._replace(arrows=0)).apply()
        )

    def test_lose_life(self):
        self.assertEqual(
            LoseLife(self.players, self.player).apply(5),
            UpdatePlayers(self.players, self.player._replace(life=3)).apply()
        )

    def test_gain_life(self):
        players = UpdatePlayers(self.players, self.player._replace(life=3)).apply()
        self.assertEqual(
            GainLife(players, self.player).apply(5),
            self.players
        )

    def test_blow_up(self):
        self.assertEqual(
            BlowUp(self.players, self.player).apply(1),
            UpdatePlayers(self.players, self.player._replace(life=7)).apply()
        )


if __name__ == '__main__':
    unittest.main()
