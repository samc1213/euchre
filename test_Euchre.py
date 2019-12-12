import unittest
from mock import MagicMock
from Euchre import RoundHistory, Player, Card, SPADES, \
    DIAMONDS, CLUBS, HEARTS, Play, Hand, get_winner, get_more_valuable_card

class RoundHistoryTests(unittest.TestCase):
    def test_get_lead_suit(self):
        trump_caller = Player('George')
        dealer = Player('Jack')
        card_picked_up = Card(value='9', suit=DIAMONDS)
        rh = RoundHistory(trump_caller, dealer, card_picked_up)
        aj = Player('AJ')
        play = Play(aj, Card(value='10', suit=CLUBS))
        rh.add_play(play)
        play2 = Play(trump_caller, Card(value='Q', suit=HEARTS))
        rh.add_play(play2)
        self.assertEqual(rh.get_lead_suit(), CLUBS)

class PlayerTests(unittest.TestCase):
    def test_follows_suit(self):
        p = Player('Sam')
        p.deal_hand(Hand([
            Card(value='Q', suit=SPADES),
            Card(value='9', suit=DIAMONDS),
            Card(value='10', suit=CLUBS),
            Card(value='K', suit=SPADES),
            Card(value='Q', suit=DIAMONDS)
        ]))
        
        round_history = MagicMock()
        round_history.get_lead_suit.return_value = CLUBS

        self.assertEqual(CLUBS, p.get_card_to_play(round_history).suit)
        
class RandomTests(unittest.TestCase):
    def test_get_winner(self):
        trick_history = [
            Play(Player(1), Card(value='K', suit=SPADES)),
            Play(Player(2), Card(value='10', suit=CLUBS)),
            Play(Player(3), Card(value='9', suit=SPADES)),
            Play(Player(3), Card(value='Q', suit=SPADES)),
        ]
        self.assertEqual(trick_history[0].player, get_winner(trick_history, HEARTS))

    def test_get_more_valuable_card_nontrump(self):
        vc = get_more_valuable_card(Card(value='K', suit=SPADES), Card(value='9', suit=SPADES), HEARTS)
        self.assertEqual(Card(value='K', suit=SPADES), vc)

    def test_get_more_valuable_card_trump_nontrump(self):
        vc = get_more_valuable_card(Card(value='9', suit=HEARTS), Card(value='A', suit=SPADES), HEARTS)
        self.assertEqual(Card(value='9', suit=HEARTS), vc)

        vc = get_more_valuable_card(Card(value='A', suit=SPADES), Card(value='9', suit=HEARTS), HEARTS)
        self.assertEqual(Card(value='9', suit=HEARTS), vc)

    def test_get_more_valuable_card_trump(self):
        vc = get_more_valuable_card(Card(value='9', suit=HEARTS), Card(value='A', suit=HEARTS), HEARTS)
        self.assertEqual(Card(value='A', suit=HEARTS), vc)

        vc = get_more_valuable_card(Card(value='A', suit=HEARTS), Card(value='9', suit=HEARTS), HEARTS)
        self.assertEqual(Card(value='A', suit=HEARTS), vc)

    def test_get_more_valuable_card_trump_bower(self):
        vc = get_more_valuable_card(Card(value='J', suit=HEARTS), Card(value='J', suit=DIAMONDS), HEARTS)
        self.assertEqual(Card(value='J', suit=HEARTS), vc)

        vc = get_more_valuable_card(Card(value='J', suit=DIAMONDS), Card(value='J', suit=HEARTS), HEARTS)
        self.assertEqual(Card(value='J', suit=HEARTS), vc)

    def test_get_more_valuable_card_trump_left(self):
        vc = get_more_valuable_card(Card(value='A', suit=HEARTS), Card(value='J', suit=DIAMONDS), HEARTS)
        self.assertEqual(Card(value='J', suit=DIAMONDS), vc)

        vc = get_more_valuable_card(Card(value='J', suit=DIAMONDS), Card(value='A', suit=HEARTS), HEARTS)
        self.assertEqual(Card(value='J', suit=DIAMONDS), vc)
