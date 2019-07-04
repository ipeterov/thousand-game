from core import AbstractPlayer


class TrivialPlayer(AbstractPlayer):
    def _bid(self, current_bid):
        # Settle on 100, or just don't bid
        return None        

    def _give_stock_cards(self):
        # Give away 2 least ranked cards
        return sorted(self.cards, key=lambda c: int(c))[:2]

    def _move(self, round, moveable_cards, leading_move):
        # Move with highest ranked card, use marriage if we have it
        card = sorted(moveable_cards, key=lambda c: int(c))[-1]
        marriage = None
        if leading_move:
            others = [
                other for other in moveable_cards
                if {card.rank, other.rank} == {'queen', 'king'}
                and card.suit == other.suit 
            ]
            if others:
                marriage = card.suit

        return card, marriage