from core import AbstractPlayer


class TrivialPlayer(AbstractPlayer):
    def _bid(self, current_bid):
        return None        

    def _give_stock_cards(self):
        return sorted(self.cards, key=lambda c: int(c))[:2]

    def _move(self, round, leading_move):
        card = sorted(self.cards, key=lambda c: int(c))[-1]
        marriage = None
        if leading_move:
            others = [
                other for other in self.cards
                if {card.rank, other.rank} == {'queen', 'king'}
                and card.suit == other.suit 
            ]
            if others:
                marriage = card.suit

        return card, marriage