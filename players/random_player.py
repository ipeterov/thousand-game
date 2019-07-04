import random

from core import AbstractPlayer


class RandomPlayer(AbstractPlayer):
    def _bid(self, current_bid):
        if random.random() > 0.5:
        	return current_bid + 5
        else:
        	return None

    def _give_stock_cards(self):
        return random.sample(self.cards, 2)

    def _move(self, round):
        return random.choice(self.cards), None