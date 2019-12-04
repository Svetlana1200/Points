from enum import Enum
from cell import Cell
import contextlib
from logic import Game, Geometry

class AI:
    def __init__(self):
        pass

    def make_step(self, game):
        pass


class AIrandom(AI):
    def __init__(self):
        self.name = "AIrandom"
    
    def make_step(self, game, q):
        coordinats = game.get_random_step()
        game.make_step(*coordinats, q)
        print("OK")


class AIeasy(AI):
    def __init__(self):
        self.name = "AIeasy"
    
    def make_step(self, game, queue):
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1),
                      (-1, -1), (-1, 1), (1, 1), (1, -1)]
        if game.turn == Cell.BLUE:
            curent_point = game.curent_point_blue
            neigbour = game.neigbour_blue
            steps_enemy = game.step_enemy_blue
        else:
            curent_point = game.curent_point_red
            neigbour = game.neigbour_red
            steps_enemy = game.step_enemy_red
        if game.turn == Cell.RED:
            game.count_red += 1
        else:
            game.count_blue += 1
        while True:
            if (curent_point is None or
                curent_point not in steps_enemy):  # меняем curent_point
                if neigbour:
                    curent_point = neigbour.pop()
                    neigbour.add(curent_point)
                else:
                    if steps_enemy:
                        curent_point = steps_enemy[0]
                        neigbour = set()
                        neigbour.add(curent_point)
                        if game.turn == Cell.RED:
                            game.count_red = 1
                        else:
                            game.count_blue = 1
                    else:
                        queue.put(False)
                        return False
            for i, j in directions:
                if curent_point[0] + i >= game.width:
                    xk = curent_point[0] + i - game.width
                elif curent_point[0] + i == -1:
                    xk = game.width - 1
                else:
                    xk = curent_point[0] + i
                if curent_point[1] + j >= game.height:
                    yk = curent_point[1] + j - game.height
                elif curent_point[1] + j == -1:
                    yk = game.height - 1
                else:
                    yk = curent_point[1] + j

                if game.turn == Cell.RED:
                    count_poins = game.count_red
                else:
                    count_poins = game.count_blue
                count_lines = len(game.lines)
                if game.make_step(xk, yk,
                                  curent_point=curent_point,
                                  count_poins=count_poins):
                    print("BLUE: ", game.count_blue, ", RED: ", game.count_red)
                    if count_lines == len(game.lines):
                        if game.turn == Cell.BLUE:
                            game.curent_point_blue = curent_point
                            game.neigbour_blue = neigbour
                            game.step_enemy_blue = steps_enemy
                        else:
                            game.curent_point_red = curent_point
                            game.neigbour_red = neigbour
                            game.step_enemy_red = steps_enemy
                    queue.put(game)
                    return True

                if ((game.turn == Cell.BLUE and
                     game.field[xk][yk] == Cell.RED) or
                        (game.turn == Cell.RED and
                         game.field[xk][yk] == Cell.BLUE) and
                        ((xk, yk)) in steps_enemy):
                    neigbour.add((xk, yk))

            with contextlib.suppress(KeyError):
                neigbour.remove(curent_point)
            with contextlib.suppress(ValueError):
                steps_enemy.remove(curent_point)
            curent_point = None


class AInormal(AI):
    def __init__(self):
        self.name = "AInormal"
    
    def make_step(self, game, queue):
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1),
                      (-1, -1), (-1, 1), (1, 1), (1, -1)]
        if game.turn == Cell.BLUE:
            curent_point = game.curent_point_blue
            neigbour = game.neigbour_blue
            steps_enemy = game.step_enemy_blue
        else:
            curent_point = game.curent_point_red
            neigbour = game.neigbour_red
            steps_enemy = game.step_enemy_red
        if game.turn == Cell.RED:
            game.count_red += 1
        else:
            game.count_blue += 1
        while True:
            if (curent_point is None or
                curent_point not in steps_enemy or
                ((game.count_blue >= Game.LENGTH_FOR_API + 1 and
                    game.turn == Cell.BLUE) or
                 (game.count_red >= Game.LENGTH_FOR_API + 1 and
                    game.turn == Cell.RED))):  # меняем curent_point
                if neigbour and curent_point is None:
                    curent_point = neigbour.pop()
                    neigbour.add(curent_point)
                elif ((game.count_blue >= Game.LENGTH_FOR_API + 1 and
                        game.turn == Cell.BLUE or
                        game.count_red >= Game.LENGTH_FOR_API + 1 and
                        game.turn == Cell.RED)
                        and curent_point is not None):
                    if steps_enemy:
                        curent_point = Geometry.get_farthest_point(
                            steps_enemy, *curent_point,
                            game.width, game.height)
                        neigbour = set()
                        neigbour.add(curent_point)
                        if game.turn == Cell.RED:
                            game.count_red = 1
                        else:
                            game.count_blue = 1
                    else:
                        queue.put(False)
                        return False
                else:
                    if steps_enemy:
                        curent_point = steps_enemy[0]
                        neigbour = set()
                        neigbour.add(curent_point)
                        if game.turn == Cell.RED:
                            game.count_red = 1
                        else:
                            game.count_blue = 1
                    else:
                        queue.put(False)
                        return False
            for i, j in directions:
                if curent_point[0] + i >= game.width:
                    xk = curent_point[0] + i - game.width
                elif curent_point[0] + i == -1:
                    xk = game.width - 1
                else:
                    xk = curent_point[0] + i
                if curent_point[1] + j >= game.height:
                    yk = curent_point[1] + j - game.height
                elif curent_point[1] + j == -1:
                    yk = game.height - 1
                else:
                    yk = curent_point[1] + j

                if game.turn == Cell.RED:
                    count_poins = game.count_red
                else:
                    count_poins = game.count_blue
                count_lines = len(game.lines)
                if game.make_step(xk, yk,
                                  curent_point=curent_point,
                                  count_poins=count_poins):
                    print("BLUE: ", game.count_blue, ", RED: ", game.count_red)
                    if count_lines == len(game.lines):
                        if game.turn == Cell.BLUE:
                            game.curent_point_blue = curent_point
                            game.neigbour_blue = neigbour
                            game.step_enemy_blue = steps_enemy
                        else:
                            game.curent_point_red = curent_point
                            game.neigbour_red = neigbour
                            game.step_enemy_red = steps_enemy
                    else:
                        if game.turn == Cell.BLUE:
                            game.count_blue = 0
                        else:
                            game.count_red = 0
                    queue.put(game)
                    return True

                if ((game.turn == Cell.BLUE and
                     game.field[xk][yk] == Cell.RED) or
                        (game.turn == Cell.RED and
                         game.field[xk][yk] == Cell.BLUE) and
                        ((xk, yk)) in steps_enemy):
                    neigbour.add((xk, yk))

            with contextlib.suppress(KeyError):
                neigbour.remove(curent_point)
            with contextlib.suppress(ValueError):
                steps_enemy.remove(curent_point)
            curent_point = None


class HUMAN:
    def __init__(self):
        self.name = "HUMAN"
    
    def make_step(self):
        self.game.make_step(*coordinats)


class ONLINE:
    def __init__(self):
        self.name = "ONLINE"
    
    def make_step(self):
        pass


def sort(first, second):
    if first.name < second.name:
        return first, second
    return second, first
