import random
from enum import Enum
import contextlib
from logic import Game, Geometry
from rivals import Rival
from cell import Cell


class AI:
    def __init__(self, game, rival):
        self.game = game
        self.rival = rival
    
    def get_next_step(self, current_player):
        if current_player == Rival.AIr:
            point = self._get_next_step_random()
        elif current_player == Rival.AIc or current_player == Rival.AInormal:
            point = self._get_next_step_easy(current_player)
        return point
    
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

    def _get_next_easy_or_normal_step(self, ai):
        if ai != Rival.AIeasy and ai != Rival.AInormal:
            print("Ошибка. Этот метод только для AIeasy и AInormal")
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
        
        if self.game.turn == Cell.RED:
            self.game.count_red += 1
        else:
            self.game.count_blue += 1
        
        start = curent_point
        while True:
            if (curent_point is None 
                or curent_point not in steps_enemy
                or ((self.game.count_blue >= Game.LENGTH_FOR_API + 1 and self.game.turn == Cell.BLUE) 
                     or (self.game.count_red >= Game.LENGTH_FOR_API + 1 and self.game.turn == Cell.RED)) 
                     and ai == Rival.AInormal): # меняем curent_point
                if neigbour and ((ai == Rival.AInormal and curent_point is None) or ai == Rival.game.AIeasy):
                    curent_point = neigbour.pop()
                    neigbour.add(curent_point)
                elif ((self.game.count_blue >= Game.LENGTH_FOR_API + 1 and self.game.turn == Cell.BLUE
                       or self.game.count_red >= Game.LENGTH_FOR_API + 1 and self.game.turn == Cell.RED)
                       and curent_point is not None
                       and ai == Rival.AInormal):
                    if steps_enemy:                  
                        curent_point = Geometry.get_farthest_point(steps_enemy, *curent_point, self.game.width, self.game.height)
                        neigbour = set()
                        neigbour.add(curent_point)
                        if self.game.turn == Cell.RED:
                            self.count_red = 1
                        else:
                            self.count_blue = 1
                    else:
                        return None
                else:
                    if steps_enemy:
                        curent_point = steps_enemy[0]
                        neigbour = set()
                        neigbour.add(curent_point)
                        if self.game.turn == Cell.RED:
                            self.count_red = 1
                        else:
                            self.count_blue = 1
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
                
                if self.game.turn == Cell.RED:
                    count_poins = self.count_red
                else:
                    count_poins = self.game.count_blue
                #count_lines = len(self.game.lines)

                if self.game.in_border(xk, yk) and self.game.field[x][y] == Cell.EMPTY:
                    return xk, yk, curent_point, count_poins
                    #self.game.make_step(xk, yk, curent_point, count_poins)
                #if self.game.make_step(xk, yk, curent_point, count_poins):
                    #print("BLUE: ", self.count_blue, ", RED: ", self.count_red) 
                    """if self.turn == Cell.BLUE:
                        #self.curent_point_blue = curent_point
                        self.neigbour_blue = neigbour
                        self.step_enemy_blue = steps_enemy
                    else:
                        #self.curent_point_red = curent_point
                        self.neigbour_red = neigbour
                        self.step_enemy_red = steps_enemy"""
                    """if count_lines == len(self.game.lines):
                        if self.game.turn == Cell.BLUE:
                            self.curent_point_blue = curent_point
                            self.neigbour_blue = neigbour
                            self.step_enemy_blue = steps_enemy
                        else:
                            self.curent_point_red = curent_point
                            self.neigbour_red = neigbour
                            self.step_enemy_red = steps_enemy       
                    elif ai == Rival.AInormal:
                        if self.game.turn == Cell.BLUE:
                            self.count_blue = 0
                        else:
                            self.count_red = 0
                    return True"""

                if ((self.game.turn == Cell.BLUE and self.game.field[xk][yk] == Cell.RED)
                     or (self.game.turn == Cell.RED and self.game.field[xk][yk] == Cell.BLUE)
                     and ((xk, yk)) in steps_enemy):
                    neigbour.add((xk, yk))

            with contextlib.suppress(KeyError):
                neigbour.remove(curent_point)
            with contextlib.suppress(ValueError):
                steps_enemy.remove(curent_point)
            curent_point = None

    
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
    

    def undo(self):
        pass

    def redo(self):
        pass


