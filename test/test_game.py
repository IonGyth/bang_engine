import unittest
from unittest import (
    TestCase,
)
from unittest.mock import patch

from game import Game, DoBeer, DoShot1, DoShot2, AddPlayer
from player import (
    UpdatePlayers,
    GetPlayer,
)


class TestGame(TestCase):
    def setUp(self):
        game = Game()
        if not game.num_players:
            game = AddPlayer(4).apply(game)
        self.game = game
        self.players = self.game.players
        self.player = self.game.next_player

    def tearDown(self):
        self.game = None
        self.players = None
        self.player = None

    @patch('game.DoShot1.get_response', return_value=2)
    def test_do_shot1(self, get_response):
        player2 = GetPlayer(self.players).apply(2)

        self.assertEqual(
            DoShot1(self.player).prompt(self.players),
            UpdatePlayers(self.players, player2._replace(life=7)).apply()
        )

    # HINT: Must end on a legal target or else there's an infinite loop.
    @patch('game.DoShot1.get_response', side_effect=[3, 2])
    def test_do_shot1_validates_target(self, get_response):
        DoShot1(self.player).prompt(self.players)

        self.assertEqual(get_response.call_count, 2)

    @patch('game.DoShot2.get_response', return_value=3)
    def test_do_shot2(self, get_response):
        player3 = GetPlayer(self.players).apply(3)

        self.assertEqual(
            DoShot2(self.player).prompt(self.players),
            UpdatePlayers(self.players, player3._replace(life=7)).apply()
        )

    @patch('game.DoShot2.get_response', side_effect=[2, 3])
    def test_do_shot2_validates_target(self, get_response):
        DoShot2(self.player).prompt(self.players)

        self.assertEqual(get_response.call_count, 2)

    @patch('game.DoBeer.get_response', return_value=2)
    def test_do_beer(self, get_response_b):
        player2 = GetPlayer(self.players).apply(2)
        players = UpdatePlayers(self.players, player2._replace(life=7)).apply()
        self.assertEqual(
            DoBeer(self.player).prompt(players),
            self.players
        )


class TestGame1v1(TestCase):
    def setUp(self):
        game = Game()
        if not game.num_players:
            game = AddPlayer(2).apply(game)
        self.game = game
        self.players = self.game.players
        self.player = self.game.next_player

    def tearDown(self):
        self.game = None
        self.players = None
        self.player = None

    @patch('game.DoShot2.get_response', side_effect=[1, 2])
    def test_do_shot2_not_self_in_1v1(self, get_response):
        player2 = GetPlayer(self.players).apply(2)

        self.assertEqual(
            DoShot2(self.player).prompt(self.players),
            UpdatePlayers(self.players, player2._replace(life=7)).apply()
        )
        self.assertEqual(get_response.call_count, 2)

if __name__ == '__main__':
    unittest.main()
