#!/usr/bin/env python3

import unittest
import plump

class TestPlumpInit(unittest.TestCase):

    def test_init(self):
        game = plump.PlumpGame()

        self.assertEqual(len(game.players), 0)
        self.assertEqual(len(game.deck.cards), 0)

    def test_addPlayer(self):
        game = plump.PlumpGame()
        self.assertTrue(game.addPlayer("Alice"))
        self.assertTrue(game.addPlayer("Bob"))

        self.assertEqual(len(game.players), 2)
        self.assertEqual(game.maxCards, 26)
        self.assertEqual(game.players[0].name, "Alice")
        self.assertEqual(game.players[1].name, "Bob")

    def test_duplicatePlayer(self):
        game = plump.PlumpGame()
        self.assertTrue(game.addPlayer("Alice"))
        self.assertFalse(game.addPlayer("Alice"))

        self.assertEqual(len(game.players), 1)
        self.assertEqual(game.players[0].name, "Alice")

    def test_deal(self):
        n = 5
        game = plump.PlumpGame()
        self.assertTrue(game.addPlayer("Alice"))
        self.assertTrue(game.addPlayer("Bob"))
        self.assertTrue(game.setMaxCards(n))
        self.assertTrue(game.deal(1), n)

        self.assertEqual(len(game.deck.cards), 52 - 2 * n)
        self.assertEqual(len(game.players[0].cards), n)
        self.assertEqual(len(game.players[1].cards), n)

        self.assertFalse(game.addPlayer("Eve"), "Cannot add player after game has started")
        self.assertEqual(len(game.players), 2)

        self.assertFalse(game.setMaxCards(n + 1), "Cannot change max cards after game has started")
        self.assertEqual(game.maxCards, n)


class TestPlumpBid(unittest.TestCase):

    def setUp(self):
        # Set up a game to initial bidding round
        n = 5
        self.game = plump.PlumpGame()
        self.assertTrue(self.game.addPlayer("Alice"))
        self.assertTrue(self.game.addPlayer("Bob"))
        self.assertTrue(self.game.setMaxCards(n))
        self.assertTrue(self.game.deal(), n)

    def test_bid(self):
        # Test bidding round
        self.assertTrue(self.game.action(0, "BID", 3))
        self.assertEqual(self.game.currentBids(), [3])

        self.assertTrue(self.game.action(1, "BID", 1))
        self.assertEqual(self.game.currentBids(), [3, 1])
        self.assertEqual(self.game.currentAction, "PLAY")

    def test_biddingRules(self):
        n = self.game.maxCards
        self.assertFalse(self.game.action(0, "BID", n + 1), "Cannot bid more than number of cards")
        self.assertEqual(self.game.currentBids(), [])

        self.assertTrue(self.game.action(0, "BID", n), "Bid can be same as number of cards")
        self.assertEqual(self.game.currentBids(), [n])

        self.assertFalse(self.game.action(0, "BID", 1), "Player 0 cannot bid twice")
        self.assertEqual(self.game.currentBids(), [n])

        self.assertFalse(self.game.action(1, "BID", 0), "Cannot let total bid equal number of cards")
        self.assertEqual(self.game.currentBids(), [n])


class TestPlumpPlay(unittest.TestCase):

    def setUp(self):
        # Set up a game to initial play round
        n = 5
        self.game = plump.PlumpGame()
        self.assertTrue(self.game.addPlayer("Alice"))
        self.assertTrue(self.game.addPlayer("Bob"))
        self.assertTrue(self.game.setMaxCards(n))
        self.assertTrue(self.game.deal(), n)
        self.assertTrue(self.game.action(0, "BID", 3))
        self.assertTrue(self.game.action(1, "BID", 1))

    def test_playCard(self):
        self.assertTrue(self.game.action(0, "PLAY", 0))


def plumpTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(TestPlumpInit("test_init"))
    suite.addTest(TestPlumpInit("test_addPlayer"))
    suite.addTest(TestPlumpInit("test_duplicatePlayer"))
    suite.addTest(TestPlumpInit("test_deal"))

    suite.addTest(TestPlumpBid("test_bid"))
    suite.addTest(TestPlumpBid("test_biddingRules"))

    suite.addTest(TestPlumpPlay("test_playCard"))

    return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    runner.run(plumpTestSuite())
