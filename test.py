from core import Game
from players.trivial_player import TrivialPlayer


players = [TrivialPlayer(), TrivialPlayer(), TrivialPlayer()]
game = Game(players)
print(game.play())