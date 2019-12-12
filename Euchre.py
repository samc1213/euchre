from __future__ import unicode_literals
from enum import Enum
from random import shuffle
from collections import defaultdict, namedtuple


CLUBS = 'Clubs'
SPADES = 'Spades'
HEARTS = 'Hearts'
DIAMONDS = 'Diamonds'

SUITS = [CLUBS, SPADES, HEARTS, DIAMONDS]


class Deck(object):
    def __init__(self):
        self.cards = self.generate_deck()

    def __repr__(self):
        return '<{}: {} cards>'.format(self.__class__.__name__, len(self.cards))

    def shuffle(self):
        self.cards = self.generate_deck()
        shuffle(self.cards)

    @staticmethod
    def generate_deck():
        deck = []
        for value in Deck.get_card_values():
            for suit in SUITS:
                deck.append(Card(value, suit))
        return deck

    @staticmethod
    def get_card_values():
        return ['9', '10', 'J', 'Q', 'K', 'A']

    def draw_cards(self, num_cards):
        if len(self.cards) < num_cards:
            raise ValueError('Cannot draw {} cards. Only have {} left in deck'.format(len(self.cards), num_cards))
        res = self.cards[:num_cards]
        del self.cards[:num_cards]
        return res

    def peek_top(self):
        return self.cards[0]

class Card(object):
    def __init__(self, value, suit):
        self.value = value
        self.suit = suit

    def __repr__(self):
        return '({} of {})'.format(self.value, self.suit)

    def __eq__(self, other):
        return self.value == other.value and self.suit == other.suit

class Hand(object):
    def __init__(self, cards):
        if len(cards) != 5:
            raise ValueError('Must pass 5 cards to initialize a '
                ' hand. Given {}'.format(len(cards)))
        self.cards = cards

    def __repr__(self):
        return u'<[' + ' '.join([repr(card) for card in self.cards]) + ']>'

    def __iter__(self):
        for card in self.cards:
            yield card

    def __iadd__(self, rhs):
        self.cards.append(rhs)
        return self

    def __isub__(self, rhs):
        self.cards.remove(rhs)
        return self

    def __getitem__(self, idx):
        return self.cards[idx]

    def get_count_by_suit(self):
        ret = defaultdict(int)
        for c in self.cards:
            ret[c.suit] += 1
        return ret


def non_trump_cards(hand, trump_suit):
    for card in hand:
        if card.suit != trump_suit:
            yield card

def lowest_card_value(hand):
    return min(hand, key=lambda c: c.value)

def get_same_colored_suit(suit):
    if suit == SPADES:
        return CLUBS
    elif suit == CLUBS:
        return SPADES
    elif suit == DIAMONDS:
        return HEARTS
    elif suit == HEARTS:
        return DIAMONDS

def is_effectively_trump(card, trump_suit):
    if card.suit == trump_suit:
        return True
    if card.value == 'J' and card.suit == get_same_colored_suit(trump_suit):
        return True
    return False

def get_more_valuable_card(left, right, trump_suit):
    if is_effectively_trump(left, trump_suit) and not is_effectively_trump(right, trump_suit):
        return left
    if not is_effectively_trump(left, trump_suit) and is_effectively_trump(right, trump_suit):
        return right

    if is_effectively_trump(left, trump_suit):
        value_ordering = Deck.get_card_values()
        value_ordering.remove('J')
        card_ordering = [Card(value=v, suit=trump_suit) for v in value_ordering]
        card_ordering.append(Card(value='J', suit=get_same_colored_suit(trump_suit)))
        card_ordering.append(Card(value='J', suit=trump_suit))
        left_idx = card_ordering.index(left)
        right_idx = card_ordering.index(right)
        if left_idx > right_idx:
            return left
        elif left_idx < right_idx:
            return right
        else:
            return None

    else:
        value_ordering = Deck.get_card_values()
        left_idx = value_ordering.index(left.value)
        right_idx = value_ordering.index(right.value)
        if left_idx > right_idx:
            return left
        elif left_idx < right_idx:
            return right
        else:
            return None


class Player(object):
    def __init__(self, name):
        self.name = name
        self.hand = None
        self.partner = None

    def set_partner(self, partner):
        self.partner = partner

    def deal_hand(self, hand):
        self.hand = hand

    def declares_trump(self, potential_trump_card):
        return self.hand.get_count_by_suit()[potential_trump_card.suit] >= 2

    def pick_up_trump_card(self, trump_card):
        self.hand -= lowest_card_value(non_trump_cards(self.hand, trump_card.suit))
        self.hand += trump_card

    def play_hand(self, round_history):
        card_to_play = self.get_card_to_play(round_history)
        self.hand -= card_to_play
        return card_to_play

    def get_card_to_play(self, round_history):
        lead_suit = round_history.get_lead_suit()
        cards_matching_lead_suit = [x for x in self.hand if x.suit == lead_suit]
        if cards_matching_lead_suit:
            return cards_matching_lead_suit[0]
        else:
            return self.hand[0]

    def __repr__(self):
        return '<Player: {}>'.format(self.name)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

class PlayerCollection(object):
    def __init__(self, players):
        if len(players) != 4:
            raise ValueError('Must pass 4 players. Given {}'.format(len(players)))

        self.players = players
        self.players[0].set_partner(players[2])
        self.players[2].set_partner(players[0])
        self.players[1].set_partner(players[3])
        self.players[3].set_partner(players[1])
        self.dealer_index = 0

    def __iter__(self):
        for i in range(self.dealer_index + 1, self.dealer_index + 5):
            yield self.players[i % 4]

    def starting_at_player(self, player):
        idx = self.players.index(player)
        for i in range(idx, idx + 4):
            yield self.players[i % 4]

    @property
    def dealer(self):
        return self.players[self.dealer_index]

    def get_team_number(self, player):
        print player
        idx = self.players.index(player)
        return idx % 2

    def next_dealer(self):
        self.dealer_index += 1
        self.dealer_index = self.dealer_index % 4

    def __repr__(self):
        return '\n'.join(repr(p) for p in self.players)

class GameHistory(object):
    def __init__(self, player_collection):
        self.history = []
        self.player_collection = player_collection

    def next_round(self, round_history):
        self.history.append(round_history)

    def is_game_over(self):
        return any([v >= 10 for v in self.score.values()])

    @property
    def score(self):
        res = defaultdict(int)
        for rh in self.history:
            if rh.round_winner is not None:
                res[rh.round_winner] += rh.points

        return res

class RoundHistory(object):
    def __init__(self, trump_caller, dealer, trump_card_picked_up):
        self.trump_caller = trump_caller
        self.dealer = dealer
        self.trump_card_picked_up = trump_card_picked_up
        self.tricks = [TrickHistory()]
        self.round_winner = None
        self.points = None

    def next_trick(self, this_trick_winner):
        self.current_trick.winner = this_trick_winner
        self.tricks.append(TrickHistory())

    def set_trick_winner(self, this_trick_winner):
        self.current_trick.winner = this_trick_winner

    def set_round_winner(self, round_winner, points):
        print '{} Won with {} points'.format(round_winner, points)
        self.round_winner = round_winner
        self.points = points

    def add_play(self, play):
        self.current_trick.add_play(play)

    def get_lead_suit(self):
        try:
            return self.current_trick[0].card.suit
        except IndexError:
            return None

    @property
    def current_trick(self):
        return self.tricks[-1]

    @property
    def current_trump_suit(self):
        return self.trump_card_picked_up.suit

    def __iter__(self):
        for t in self.tricks:
            yield t

    def __repr__(self):
        return '{}'.format(self.tricks)

class TrickHistory(object):
    def __init__(self):
        self.plays = []
        self.winner = None

    def add_play(self, play):
        self.plays.append(play)

    def __getitem__(self, idx):
        return self.plays[idx]

Play = namedtuple('Play', ['player', 'card'])

def get_winner(trick_history, trump_suit):
    lead_suit = trick_history[0].card.suit
    winner = trick_history[0].player
    winning_card = trick_history[0].card
    for follower in trick_history[1:]:
        if follower.card.suit != lead_suit and follower.card.suit != trump_suit:
            continue
        new_winner = get_more_valuable_card(winning_card, follower.card, trump_suit)
        if new_winner != winning_card:
            winner = follower.player
            winning_card = follower.card

    return winner

class GameManager(object):
    def __init__(self):
        self.deck = Deck()
        self.player_collection = PlayerCollection([Player(str(i)) for i in range(4)])

    def deal(self):
        self.deck.shuffle()
        for player in self.player_collection:
            hand = Hand(self.deck.draw_cards(5))
            player.deal_hand(hand)

        print 'Hands dealt'

    def call_trump(self):
        potential_trump = self.deck.peek_top()
        print u'Potential trump: {}'.format(potential_trump)
        for player in self.player_collection:
            if player.declares_trump(potential_trump):
                print '{} declares trump as {}'.format(player, potential_trump.suit)
                self.player_collection.dealer.pick_up_trump_card(potential_trump)
                trump = potential_trump.suit
                return RoundHistory(player, self.player_collection.dealer, potential_trump)
        raise ValueError('Nobody called trump!')

    def play_round(self, round_history):
        starting_player = self.player_collection.dealer
        for i in range(5):
            for player in self.player_collection.starting_at_player(starting_player):
                card_to_play = player.play_hand(round_history)
                play = Play(player, card_to_play)
                print play
                round_history.add_play(play)
            

            winner = get_winner(round_history.current_trick, round_history.current_trump_suit)
            print '{} won the trick'.format(winner)
            print '====='
            starting_player = winner
            if i == 4:
                round_history.set_trick_winner(winner)
            else:
                round_history.next_trick(winner)

        trick_wins_by_team = defaultdict(int)
        for r in round_history:
            trick_wins_by_team[self.player_collection.get_team_number(r.winner)] += 1

        winning_team = max(trick_wins_by_team.iteritems(), key=lambda (k, v): v)[0]
        if winning_team != self.player_collection.get_team_number(round_history.trump_caller):
            # Euchre
            if len(trick_wins_by_team) == 1:
                # Sweep
                round_history.set_round_winner(trick_wins_by_team.keys()[0], 3)
            else:
                round_history.set_round_winner(trick_wins_by_team.keys()[0], 2)
        else:
            if len(trick_wins_by_team) == 1:
                # Sweep
                round_history.set_round_winner(trick_wins_by_team.keys()[0], 2)
            else:
                round_history.set_round_winner(trick_wins_by_team.keys()[0], 1)
            

    def play_game(self):
        gh = GameHistory(self.player_collection)
        while not gh.is_game_over():
            print gh.score
            self.deal()
            round_history = self.call_trump()
            self.play_round(round_history)
            gh.next_round(round_history)
            self.player_collection.next_dealer()
            import time
            time.sleep(10)

if __name__ == '__main__':
    g = GameManager()
    g.play_game()
