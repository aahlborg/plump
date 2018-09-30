#!/usr/bin/env python3

import argparse
import random


class Card:
    SUITES = ["Clubs", "Diamonds", "Spades", "Hearts"]
    RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

    def __init__(self, suite=None, rank=None):
        self.suite = self.SUITES[0]
        self.rank = self.RANKS[0]
        if suite:
            self.suite = self.SUITES.index(suite)
        if rank:
            self.rank = self.RANKS.index(rank)
    
    def __str__(self):
        return self.RANKS[self.rank] + " of " + self.SUITES[self.suite]


class CardDeck:
    def __init__(self):
        self.cards = list()

        for suite in Card.SUITES:
            for rank in Card.RANKS:
                self.cards.append(Card(suite, rank))
        random.shuffle(self.cards)
    
    def __str__(self):
        s = "Deck holds {} cards: [".format(len(self.cards))
        for card in self.cards:
            s += str(card) + ", "
        return s + "]"
    
    def shuffle(self):
        random.shuffle(self.cards)

    def pop(self):
        return self.cards.pop(0)


class Player:
    def __init__(self, name):
        self.name = name
        self.cards = list()
        self.bids = list()
        self.outcome = list()

    def __str__(self):
        s = "Player {} holds {} cards: [".format(self.name, len(self.cards))
        for card in self.cards:
            s += str(card) + ", "
        return s + "]"
    
    def deal(self, card):
        self.cards.append(card)

    def doBid(self, bid):
        self.bids.append(bid)

    def lastBid(self):
        return self.bids[-1]

    def setOutcome(self, outcome):
        self.outcome.append(outcome == True)

    def getPoints(self):
        points = list()
        for i in range(len(self.outcome)):
            if self.outcome[i]:
                bid = self.bids[i]
                if bid == 0:
                    points.append(5)
                elif bid < 10:
                    points.append(10 + bid)
                elif bid < 100:
                    points.append(100 + bid)
            else:
                points.append(0)
        return points

    def sumPoints(self):
        return sum(self.getPoints())


class PlumpGame:
    MAX_CARDS = 52
    ACTIONS = ["BID", "PLAY"]

    def __init__(self):
        self.players = list()
        self.deck = CardDeck()
        self.cardsLeft = 0
        self.maxCards = 1
        self.numberOfRounds = 1
        self.currentRound = 0
        self.currentAction = self.ACTIONS[0]
        self.currentPlayer = 0
        self.firstPlayer = 0
    
    def addPlayer(self, name):
        for player in self.players:
            if player.name == name:
                print("Player {} is already participating in the game".format(name))
                return False
        self.players.append(Player(name))
        # Set max possible number of rounds
        self.setMaxCards(100)
        return True
    
    def setMaxCards(self, n):
        # Cap at MAX_CARDS / nPlayers
        cards = min(n, self.MAX_CARDS // len(self.players))
        # Min 1 round
        cards = max(cards, 1)
        self.maxCards = cards
        self.numberOfRounds = self.maxCards
        return (self.maxCards == n)

    def __str__(self):
        s = "Game has {} players:\n".format(len(self.players))
        for player in self.players:
            s += str(player) + "\n"
        s += "Rounds: {}\n".format(self.numberOfRounds)
        s += "Status: {}\n".format(self.status())
        s += "Bids: {}\n".format(self.currentBids())
        return s

    def start(self):
        self.currentRound = 0
        self.currentAction = self.ACTIONS[0]
        self.currentPlayer = self.firstPlayer

    def status(self):
        if self.cardsLeft == 0:
            return (False, self.currentRound, None, None)
        else:
            return (True, self.currentRound, self.currentAction, self.currentPlayer)

    def currentBids(self):
        bids = list()
        playerOrder = self.getPlayerOrder()
        for i in playerOrder:
            if (self.currentAction == "BID") and (i == self.currentPlayer):
                break
            bids.append(self.players[i].lastBid())
        return bids

    def getPlayerOrder(self):
        # PLayer indices sorted according to position this round
        players = list()
        for j in range(len(self.players)):
            players.append((self.firstPlayer + j) % len(self.players))
        return players

    def deal(self):
        nCards = 0
        if self.currentRound < self.maxCards:
            nCards = self.maxCards - self.currentRound
        elif self.currentRound < (self.maxCards + len(self.players)):
            nCards = 1
        for _ in range(nCards):
            for j in self.getPlayerOrder():
                p = self.players[j]
                p.deal(self.deck.pop())
        self.cardsLeft = nCards
        return nCards

    def action(self, player, action, data):
        validAction = True
        reason = "Success"
        # Validity check
        if player != self.currentPlayer:
            reason = "Player {} is not the current player".format(player)
            validAction = False
        if action != self.currentAction:
            reason = "Action {} not allowed".format(action)
            validAction = False
        
        if action == "BID":
            player = self.players[self.currentPlayer]
            bid = data
            nextPlayer = (self.currentPlayer + 1) % len(self.players)
            if bid > self.cardsLeft:
                reason = "Bid {} is more than number of cards {}".format(bid, self.cardsLeft)
                validAction = False
            if nextPlayer == self.firstPlayer:
                print("Last bid {}, total bid is {}".format(bid, sum(self.currentBids()) + bid))
                if sum(self.currentBids()) + bid == self.cardsLeft:
                    reason = "Bid {} not allowed".format(bid)
                    validAction = False
            if validAction:
                player.doBid(bid)
        
        if not validAction:
            print("{} failed: {}".format(action, reason))
            return False
        else:
            print("{} pass: {}".format(action, reason))
            self.currentPlayer = (self.currentPlayer + 1) % len(self.players)

        # Check if end of round
        if self.currentPlayer == self.firstPlayer:
            if self.currentAction == "BID":
                self.currentAction = "PLAY"
            if self.currentAction == "PLAY":
                pass
        return True


def main():
    print("Welcome to plump")

    parser = argparse.ArgumentParser(description="Plump card game")
    parser.add_argument("--cards", "-c", type=int, help="Number of cards to start with")
    parser.add_argument("players", nargs='+', help="Player name")
    args = parser.parse_args()

    print(args)

    game = PlumpGame()
    for name in args.players:
        game.addPlayer(name)
    if args.cards:
        game.setMaxCards(args.cards)

    print("========\nStart")
    game.start()
    print(game)

    print("========\nDeal")
    game.deal()
    print(game)


if __name__ == "__main__":
    main()
