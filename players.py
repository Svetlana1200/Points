import random
from enum import Enum
import contextlib

class Cell(Enum):
    RED = 1
    BLUE = 2
    EMPTY = 3
    BLACK = 4

class Rival(Enum):
    HUMAN = 1
    AIr = 2
    AIc = 3
    AInormal = 4

class AI:
    def __init__(self, game, red_players):
        self.game = game
        self.red_players = red_players
    
    def get_next_step(self):
        if self.enemy == Rival.AIr:
            point = _get_next_step_random()
        elif self.enemy == Rival.AIc:
            point = _get_next_step_easy()
        elif self.enemy == Rival.AInormal:
            point = _get_next_step_normal()

    def undo(self):
        pass

    def redo(self):
        pass

    
    def _get_next_step_random(self):
        return random.choice(self.game.possible_steps)

    def _get_next_step_easy(self):
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1),
                      (-1, -1), (-1, 1), (1, 1), (1, -1)]
        if self.game.turn == Cell.BLUE:
            curent_point = self.game.curent_point_blue
            neigbour = self.game.neigbour_blue
            steps_enemy = self.game.step_enemy_blue
        else:
            curent_point = self.game.curent_point_red
            neigbour = self.game.neigbour_red
            steps_enemy = self.game.step_enemy_red
        start = curent_point
        while True:
            if curent_point is None or curent_point not in steps_enemy:
                if neigbour:
                    curent_point = neigbour.pop()
                    neigbour.add(curent_point)
                else:
                    if steps_enemy:
                        curent_point = steps_enemy[0]
                        neigbour = set()
                        neigbour.add(curent_point)
                    else:
                        return None

                if curent_point == start:
                    return None
           
            for i, j in directions:
                if curent_point[0] + i >= self.game.width:
                    xk = curent_point[0] + i - self.game.width
                elif curent_point[0] + i == -1:
                    xk = self.game.width - 1
                else:
                    xk = curent_point[0] + i
                if curent_point[1] + j >= self.game.height:
                    yk = curent_point[1] + j - self.game.height
                elif curent_point[1] + j == -1:
                    yk = self.game.height - 1
                else:
                    yk = curent_point[1] + j
                
                if self.game.in_border(xk, yk) and self.game.field[xk][yk] == Cell.EMPTY:
                    return xk, yk, curent_point

                """count_lines = len(self.lines)
                if self.make_step(xk, yk, curent_point):
                    if count_lines == len(self.lines):
                        if self.turn == Cell.BLUE:
                            self.curent_point_blue = curent_point
                            self.neigbour_blue = neigbour
                            self.step_enemy_blue = steps_enemy
                        else:
                            self.curent_point_red = curent_point
                            self.neigbour_red = neigbour
                            self.step_enemy_red = steps_enemy
                    return True"""
                if ((self.game.turn == Cell.BLUE and self.game.field[xk][yk] == Cell.RED and
                     ((xk, yk)) in steps_enemy) or (self.game.turn == Cell.RED and
                     self.game.field[xk][yk] == Cell.BLUE and ((xk, yk)) in steps_enemy)):
                    neigbour.add((xk, yk))

            with contextlib.suppress(KeyError):
                neigbour.remove(curent_point)
            with contextlib.suppress(ValueError):
                steps_enemy.remove(curent_point)
            curent_point = None

    def _get_next_step_normal(self):
        pass


    def _undo_random(self):
        pass

    def _undo_easy(self):
        pass

    def _undo_normal(self):
        pass

        
    def _redo_random(self):
        pass

    def _redo_easy(self):
        pass

    def _redo_normal(self):
        pass

    


