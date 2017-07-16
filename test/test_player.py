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
    Role,
    CheckGameEnd,
)


class TestPlayer(TestCase):
    def setUp(self):
        game = Game()
        if not game.num_players:
            game = AddPlayer(1).apply(game)
        self.game = ShufflePlayers().apply(game)
        self.players = self.game.players
        self.player = self.game.next_player

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


class TestDeadPlayers(TestCase):
    def setUp(self):
        game = Game()
        if not game.num_players:
            game = AddPlayer(3).apply(game)
        self.game = ShufflePlayers().apply(game)
        self.players = self.game.players
        self.player = self.game.next_player

    def test_dead_players_removed(self):
        self.assertEqual(
            len(self.players),
            3,
        )
        players = UpdatePlayers(self.players, self.player._replace(life=0)).apply()
        self.assertEqual(
            len(players),
            2,
        )


class TestGameEnd(TestCase):
    def setUp(self):
        self.game = Game()

    def test_sherrif_last_player(self):
        game = AddPlayer(1).apply(self.game)

        self.assertEqual(
            CheckGameEnd().apply(game.players),
            Role.SHERIFF,
        )

    def test_outlaw_last_player(self):
        game = AddPlayer(3).apply(self.game)
        players = game.players
        for player in players:
            if player.role != Role.OUTLAW:
                players = UpdatePlayers(players, player._replace(life=0)).apply()

        self.assertEqual(
            CheckGameEnd().apply(players),
            Role.OUTLAW,
        )

    def test_vice_last_player(self):
        game = AddPlayer(8).apply(self.game)
        players = game.players
        for player in players:
            if player.role != Role.VICE:
                players = UpdatePlayers(players, player._replace(life=0)).apply()

        self.assertEqual(
            CheckGameEnd().apply(players),
            Role.OUTLAW,
        )

    def test_sherrif_vice_last_player(self):
        game = AddPlayer(8).apply(self.game)
        players = game.players
        for player in players:
            if player.role not in [Role.VICE, Role.SHERIFF]:
                players = UpdatePlayers(players, player._replace(life=0)).apply()

        self.assertEqual(
            CheckGameEnd().apply(players),
            Role.SHERIFF,
        )

    def test_renegade_last_player(self):
        game = AddPlayer(3).apply(self.game)
        players = game.players
        for player in players:
            if player.role != Role.RENEGADE:
                players = UpdatePlayers(players, player._replace(life=0)).apply()

        self.assertEqual(
            CheckGameEnd().apply(players),
            Role.RENEGADE,
        )

    def test_two_renegade_last_players(self):
        game = AddPlayer(8).apply(self.game)
        players = game.players
        for player in players:
            if player.role != Role.RENEGADE:
                players = UpdatePlayers(players, player._replace(life=0)).apply()

        self.assertEqual(
            CheckGameEnd().apply(players),
            Role.OUTLAW,
        )

    def test_everybody_dead(self):
        self.assertEqual(
            CheckGameEnd().apply(()),
            Role.OUTLAW,
        )


if __name__ == '__main__':
    unittest.main()
