from core import Game
from players.trivial_player import TrivialPlayer
from players.random_player import RandomPlayer


players = [TrivialPlayer(), TrivialPlayer(), RandomPlayer()]
result = Game(players).play(with_prints=True)