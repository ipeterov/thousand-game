import random
import itertools


SUIT = ['ace', 'ten', 'king', 'queen', 'jack', 'nine']
SUIT_NAMES = ['diamonds', 'clubs', 'hearts', 'spades']
TRUMP_NAMES = SUIT_NAMES + ['aces']
MOVE_COUNT = 8
RANK_VALUES = {
    'ace': 11,
    'ten': 10,
    'king': 4,
    'queen': 3,
    'jack': 2,
    'nine': 0,
}
TRUMP_VALUES = {
    'diamonds': 200,
    'clubs': 100,
    'hearts': 80,
    'spades': 60,
    'aces': 40,
}


class Card:
    def __init__(self, rank, suit):
        assert rank in SUIT
        self.rank = rank
        assert suit in SUIT_NAMES
        self.suit = suit

    def __repr__(self):
        return f'<Card {self.rank} of {self.suit}>'

    def __int__(self):
        return RANK_VALUES[self.rank]

    def __eq__(self, other):
        return self.rank == other.rank and self.suit == other.suit


class Deck:
    def cards(self):
        cards = [Card(rank, suit) for rank, suit in itertools.product(SUIT, SUIT_NAMES)]
        assert len(cards) == 24
        return cards

    def shuffled_cards(self):
        cards = self.cards()
        random.shuffle(cards)
        return cards

    def deal(self):
        """Return stock, player1, player2, player3"""
        cards = self.shuffled_cards()
        return cards[:3], cards[3:10], cards[10:17], cards[17:]


class Round:
    def __init__(self, players):
        self.players = players
        self.history = []
        self.trumps = {}
        self.trump = None
        self.leading_player = None
        self.winning_bid = None

    def remaining_players(self, leading_player):
        leading_index = self.players.index(leading_player)
        return self.players[leading_index + 1:] + self.players[:leading_index]

    def deal_cards(self):
        deck = Deck()
        stock, *player_deals = deck.deal()

        for player, cards in zip(self.players, player_deals):
            player.receive_deal(cards)

        return stock

    def bidding(self):
        current_bid = 100
        bid_winner = self.players[0]
        while sum(player.is_bidding for player in self.players) > 1:
            for player in self.players:
                if not player.is_bidding:
                    continue
                new_bid = player.bid(current_bid)
                if new_bid is None:
                    player.is_bidding = False
                else:
                    bid_winner = player
                    current_bid = new_bid
        return bid_winner, current_bid

    def pre_game(self, bid_winner, stock):
        bid_winner.receive_stock(stock)

        card1, card2 = bid_winner.give_stock_cards()
        player1, player2 = (player for player in self.players if player != bid_winner)
        player1.receive_stock_card(card1)
        player2.receive_stock_card(card2)        

    def moves(self, starting_player):
        leading_player = starting_player
        for i in range(MOVE_COUNT):
            move = Move(self.trump)

            card, new_trump = leading_player.move(self, leading_move=True)            
            if new_trump:
                # Checks are performed in Player.move
                self.trump = new_trump
                self.trumps[new_trump] = leading_player

            move.add_submove(leading_player, card)
            
            for player in self.remaining_players(leading_player):
                card, _ = player.move(self, leading_move=False)
                move.add_submove(player, card)

            leading_player = move.winner()

            self.history.append(move)

    def get_results(self):
        results = {player: 0 for player in self.players}
        for move in self.history:
            results[move.winner()] += int(move)
        for trump, player in self.trumps.items():
            results[player] += TRUMP_VALUES[trump]
        return results

    def play(self):
        for player in self.players:
            player.start_round()
        stock = self.deal_cards()
        bid_winner, winning_bid = self.bidding()
        self.winning_bid = winning_bid
        self.pre_game(bid_winner, stock)
        self.moves(starting_player=bid_winner)
        return self.get_results()


class Game:
    def __init__(self, players):
        assert all(issubclass(type(player), AbstractPlayer) for player in players), 'all players must be subclasses of AbstractPlayer'
        assert len(players) == 3, 'only 3 players can play'
        self.players = players
        self.results = {player: 0 for player in players}

    def move_players(self):
        self.players.insert(self.players.pop(), 0)

    def play(self):
        while all(result < 1000 for result in self.results.values()):
            results = Round(self.players).play()
            for player, result in results.items():
                self.results[player] += result
        return self.results


class Move:
    def __init__(self, trump):
        self.submoves = []
        self.trump = trump

    def __repr__(self):
        return ', '.join(
            f'{player} played {card}'
            for player, card in self.submoves
        )

    def add_submove(self, player, card):
        assert len(self.submoves) < 3, 'can\'t add more than 3 submoves'
        self.submoves.append([player, card])

    def __int__(self):
        return sum(int(card) for player, card in self.submoves)

    def winner(self):
        assert len(self.submoves) == 3, 'move is not finished yet'
        submoves = sorted(
            self.submoves,
            reverse=True,
            key=lambda submove: (submove[1].suit == self.trump, int(submove[1])),
        )
        return submoves[0][0]


class AbstractPlayer:
    def __init__(self):
        self.is_bidding = True
        self.cards = []

    def start_round(self):
        self.is_bidding = True
        self.cards = []

    def _bid(self, current_bid):
        raise NotImplementedError()

    def bid(self, current_bid):
        new_bid = self._bid(current_bid)
        assert new_bid is None or isinstance(new_bid, int), 'new bid must be None or int'
        if new_bid is not None:
            assert self.is_bidding, 'player is out of bidding'
            assert new_bid > current_bid, 'new bid must be higher than the current bid'
            assert new_bid % 5 == 0, 'new bid must be divisible by five'
        return new_bid

    def receive_deal(self, cards):
        self.cards = cards

    def receive_stock(self, stock):
        self.cards += stock

    def receive_stock_card(self, stock_card):
        self.cards.append(stock_card)

    def _give_stock_cards(self):
        raise NotImplementedError()

    def give_stock_cards(self):
        assert len(self.cards) == 10
        card1, card2 = self._give_stock_cards()
        self.cards.remove(card1)
        self.cards.remove(card2)
        return card1, card2

    def _move(self, round):
        raise NotImplementedError()

    def move(self, round, leading_move):
        card, new_trump = self._move(round)

        assert card in self.cards, 'can\'t make a move with a card you don\'t have'

        assert new_trump is None or isinstance(new_trump, str), 'new trump must be None or str'
        if new_trump is not None:
            assert new_trump in TRUMP_NAMES, f'invalid trump name {new_trump}'
            if not leading_move:
                assert not new_trump, 'can\'t declare trump in a non-leading move'

            marriage_ranks = ['king', 'queen']
            if card.rank in marriage_ranks:
                marriage_ranks.remove(card.rank)
                other_rank = marriage_ranks.pop()
                other = Card(other_rank, card.suit)
                assert other in self.cards, f'{other_rank} needed for marriage'
            elif card.rank == 'ace':
                assert sum(card.rank == 'ace' for card in self.cards) == 4, '4 aces needed for ace trump'

        self.cards.remove(card)

        return card, new_trump
