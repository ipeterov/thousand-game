from core import Game
from players.trivial_player import TrivialPlayer


players = [TrivialPlayer(), TrivialPlayer(), TrivialPlayer()]
result = Game(players).play(with_prints=True)