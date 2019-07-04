from core import Game
from players.random_player import RandomPlayer


players = [RandomPlayer(), RandomPlayer(), RandomPlayer()]
game = Game(players)
print(game.play())