import unittest
from unittest import (
    TestCase,
)

from game import Game, AddPlayer, ShufflePlayers, clockwise_player
from player import (
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
            GetPlayer(self.players).apply(int(self.player.p_id)),
            self.player
        )

    def test_take_arrow_simple(self):
        self.assertEqual(
            TakeArrow(5).apply(self.players, self.player),
            UpdatePlayers(self.players, self.player._replace(arrows=5)).apply()
        )

    def test_remove_arrow_simple(self):
        players = UpdatePlayers(self.players, self.player._replace(arrows=5)).apply()
        self.assertEqual(
            RemoveArrow(5).apply(players, self.player),
            UpdatePlayers(self.players, self.player._replace(arrows=0)).apply()
        )

    def test_remove_arrow_with_no_arrows(self):
        players = UpdatePlayers(self.players, self.player._replace(arrows=0)).apply()
        self.assertEqual(
            RemoveArrow(1).apply(players, self.player),
            UpdatePlayers(self.players, self.player).apply()
        )

    def test_lose_life_simple(self):
        self.assertEqual(
            LoseLife(self.players, self.player).apply(5),
            UpdatePlayers(self.players, self.player._replace(life=3)).apply()
        )

    def test_gain_life_simple(self):
        players = UpdatePlayers(self.players, self.player._replace(life=3)).apply()
        self.assertEqual(
            GainLife(5).apply(players, self.player),
            self.players
        )

    def test_gain_life_max(self):
        self.assertEqual(
            GainLife(1).apply(self.players, self.player),
            self.players
        )

    def test_blow_up(self):
        self.assertEqual(
            BlowUp(self.players, self.player).apply(1),
            UpdatePlayers(self.players, self.player._replace(life=7)).apply()
        )


class TestPlayers(TestCase):
    def setUp(self):
        game = Game()
        if not game.num_players:
            game = AddPlayer(2).apply(game)
        self.game = ShufflePlayers().apply(game)
        self.players = self.game.players
        self.player = self.game.next_player

    def tearDown(self):
        self.game = None
        self.players = None
        self.player = None

    def test_take_arrow_resolve(self):
        players = self.players

        players = TakeArrow(5).apply(players, self.player)
        player = GetPlayer(players).apply(self.player.p_id)

        next_player = clockwise_player(players, player, 1)
        players = TakeArrow(5).apply(players, next_player)

        self.assertEqual(
            GetPlayer(players).apply(next_player.p_id).arrows,
            1,
        )
        self.assertEqual(
            GetPlayer(players).apply(next_player.p_id).life,
            4,
        )
        self.assertEqual(
            GetPlayer(players).apply(player.p_id).life,
            3,
        )


if __name__ == '__main__':
    unittest.main()
