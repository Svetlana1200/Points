from enum import Enum
from cell import Cell
import contextlib
from logic import Game, Geometry
import multiprocessing as mp
from PyQt5 import QtWidgets, QtCore, QtTest


class AI:
    def __init__(self):
        pass

    def make_step(self, game, coordinats=None):
        pass

    def undo_reaction(self, game):
        if game.undo_count > Game.UNDO_COUNT * 2:
            raise IndexError
        (self.x, self.y), self.curent_point, self.count_poins = game.cancellation.pop()
        print("UNDO ", self.x, self.y)
        game.possible_steps.append((self.x, self.y))
        find_line = False
        self.color_undo_point = game.field[self.x][self.y]
        game.field[self.x][self.y] = Cell.EMPTY

        for line in game.lines:
            if (self.x, self.y) in line[0]:
                find_line = True
                game.repetitions.append(
                    ((self.x, self.y), self.color_undo_point, line,
                     self.curent_point, self.count_poins))
                game.lines.remove(line)
                for ((black_x, black_y), color_early) in line[2]:  # черные т.
                    game.field[black_x][black_y] = color_early
                if line[1] == Cell.BLUE:  # цвет
                    game.score_blue -= line[3]  # площадь
                else:
                    game.score_red -= line[3]
                break
        if not find_line:
            game.repetitions.append(
                ((self.x, self.y), self.color_undo_point, (), self.curent_point, self.count_poins))
        try:
            if self.color_undo_point == Cell.RED:
                game.last_red = game.cancellation[-2][0]
            else:
                game.last_blue = game.cancellation[-2][0]
        except IndexError:
            if self.color_undo_point == Cell.RED:
                game.last_red = None
            else:
                game.last_blue = None
        game.undo_count += 1

    def redo_reaction(self, game):
        ((self.x, self.y), self.color_undo_point,
         self.line, self.curent_point, self.count_poins) = game.repetitions.pop()
        print("REDO ", self.x, self.y)
        game.cancellation.append(((self.x, self.y), self.curent_point, self.count_poins))
        game.possible_steps.remove((self.x, self.y))
        game.field[self.x][self.y] = self.color_undo_point

        if len(self.line) > 0:
            game.lines.append(self.line)
            if self.color_undo_point == Cell.BLUE:  # цвет
                game.score_blue += self.line[3]  # площадь
                game.curent_point_blue = None
                game.neigbour_blue = set()
            else:
                game.score_red += self.line[3]
                game.curent_point_red = None
                game.neigbour_red = set()
            for ((black_x, black_y), _color) in self.line[2]:  # черные точки
                game.field[black_x][black_y] = Cell.BLACK
        if self.color_undo_point == Cell.RED:
            game.last_red = (self.x, self.y)
        else:
            game.last_blue = (self.x, self.y)
        game.undo_count -= 1

    def process_step(self, field, game, current_player, current_turn):
        res = None
        is_first = False
        while res is None:
            res = make_move_in_another_pro(
                field, game, current_player)
            if game.turn != current_turn:
                is_first = True
                break
        field, game, _made_step, _coordinats = res
        return field, game, is_first

class AIrandom(AI):
    def __init__(self):
        self.name = "AIrandom"
    
    def make_step(self, game, q, coordinats=None):
        coordinats = game.get_random_step()
        game.make_step(*coordinats, q)

    def undo_reaction(self, game):
        super().undo_reaction(game)
    
    def redo_reaction(self, game):
        super().redo_reaction(game)


class AIeasy(AI):
    def __init__(self):
        self.name = "AIeasy"
    
    def make_step(self, game, queue, coordinats=None):
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

    def undo_reaction(self, game):
        super().undo_reaction(game)

        (neigbour, step_enemy,
         neigbour_another,
         step_enemy_another) = game._get_neigbours_steps_enemys(
             self.color_undo_point)

        for line in game.lines:
            if (self.x, self.y) in line[0]:
                neigbour.add(self.curent_point)
                step_enemy.insert(0, self.curent_point)
                if self.color_undo_point == Cell.RED:
                    game.curent_point_red = self.curent_point
                else:
                    game.curent_point_blue = self.curent_point
                break

        if self.curent_point is not None:
            if self.color_undo_point == Cell.RED:
                game.curent_point_red = None
                game.neigbour_red = set()
            else:
                game.curent_point_blue = None
                game.neigbour_blue = set()
        with contextlib.suppress(KeyError):
            neigbour_another.remove((self.x, self.y))
        with contextlib.suppress(ValueError):
            step_enemy_another.remove((self.x, self.y))
        print("BLUE: ", game.count_blue, ", RED: ", game.count_red)

    def redo_reaction(self, game):
        super().redo_reaction(game)
        (neigbour, step_enemy,
         neigbour_another,
         step_enemy_another) = game._get_neigbours_steps_enemys(
             self.color_undo_point)

        if len(self.line) > 0:
            with contextlib.suppress(KeyError):
                neigbour.remove(self.curent_point)
            with contextlib.suppress(ValueError):
                step_enemy.remove(self.curent_point)


        if self.curent_point is not None:
            if self.color_undo_point == Cell.RED:
                game.curent_point_red = self.curent_point
            else:
                game.curent_point_blue = self.curent_point
        with contextlib.suppress(KeyError):
            neigbour_another.add((self.x, self.y))
        with contextlib.suppress(ValueError):
            step_enemy_another.append((self.x, self.y))
        print("BLUE: ", game.count_blue, ", RED: ", game.count_red)

class AInormal(AI):
    def __init__(self):
        self.name = "AInormal"
    
    def make_step(self, game, queue, coordinats=None):
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

    def undo_reaction(self, game):
        super().undo_reaction(game)

        if len(game.cancellation) > 0:
            ((next_x, next_y),
             _next_curent_point,
             _next_count_poins) = game.cancellation[-1]
        else:
            next_x, next_y = None, None
        (neigbour, step_enemy,
         neigbour_another,
         step_enemy_another) = game._get_neigbours_steps_enemys(
             self.color_undo_point)

        for line in game.lines:
            if (self.x, self.y) in line[0]:
                neigbour.add(self.curent_point)
                step_enemy.insert(0, self.curent_point)
                if self.color_undo_point == Cell.RED:
                    game.curent_point_red = self.curent_point
                else:
                    game.curent_point_blue = self.curent_point
                break

        if self.curent_point is not None:
            if self.curent_point == (next_x, next_y):
                if self.color_undo_point == Cell.RED:
                    game.curent_point_red = None
                    game.neigbour_red = set()
                else:
                    game.curent_point_blue = None
                    game.neigbour_blue = set()
            else:
                if self.curent_point not in step_enemy:
                    step_enemy.append(self.curent_point)
                if self.color_undo_point == Cell.RED:
                    game.curent_point_red = self.curent_point
                    game.neigbour_red = set()
                else:
                    game.curent_point_blue = self.curent_point
                    game.neigbour_blue = set()  
            if self.color_undo_point == Cell.RED:
                game.count_red -= 1
                if game.count_red <= 0:
                    game.count_red = self.count_poins - 1
            else:
                game.count_blue -= 1
                if game.count_blue <= 0:
                    game.count_blue = self.count_poins - 1
        with contextlib.suppress(KeyError):
            neigbour_another.remove((self.x, self.y))
        with contextlib.suppress(ValueError):
            step_enemy_another.remove((self.x, self.y))
        print("BLUE: ", game.count_blue, ", RED: ", game.count_red)

    def redo_reaction(self, game):
        super().redo_reaction(game)
        if len(game.repetitions) > 0:
            ((next_x, next_y), _next_color_undo_point,
             _next_line, _next_curent_point,
             _next_count_poins) = game.repetitions[-1]
        else:
            next_x, next_y = None, None
        (neigbour, step_enemy,
         neigbour_another,
         step_enemy_another) = game._get_neigbours_steps_enemys(
             self.color_undo_point)

        if len(self.line) > 0:
            game.lines.append(self.line)
            with contextlib.suppress(KeyError):
                neigbour.remove(self.curent_point)
            with contextlib.suppress(ValueError):
                step_enemy.remove(self.curent_point)

        if self.curent_point is not None:
            if self.curent_point == (next_x, next_y):
                if self.color_undo_point == Cell.RED:
                    game.curent_point_red = self.curent_point
                else:
                    game.curent_point_blue = self.curent_point
            if self.color_undo_point == Cell.RED:
                game.count_red += 1
                if game.count_red > self.count_poins:
                    game.count_red = 1
            else:
                game.count_blue += 1
                if game.count_blue > self.count_poins:
                    game.count_blue = 1
        with contextlib.suppress(KeyError):
            neigbour_another.add((self.x, self.y))
        with contextlib.suppress(ValueError):
            step_enemy_another.append((self.x, self.y))
        print("BLUE: ", game.count_blue, ", RED: ", game.count_red)

class HUMAN:
    def __init__(self):
        self.name = "HUMAN"
    
    def make_step(self, game, queue, coordinats=None):
        game.make_step(*coordinats, queue)

    def process_step(self, field, game, is_first, start=None):
        field.x, field.y = -1, -1
        coordinats = field.get_coordinats()
        made_step = False
        while (not field.exit and not field.results and
                (field.name_win is None or
                    field.name_win['size'] is None) and
                not made_step):
            res = None
            while res is None:
                res = make_move_in_another_pro(
                    field, game, HUMAN(), coordinats)
                if not (game.turn == Cell.RED and isinstance(field.rival_obj[1], HUMAN) or game.turn == Cell.BLUE and isinstance(field.rival_obj[0], HUMAN)):
                    is_first = True
                    break
            if not (game.turn == Cell.RED and isinstance(field.rival_obj[1], HUMAN) or game.turn == Cell.BLUE and isinstance(field.rival_obj[0], HUMAN)):
                break
            field, game, made_step, coordinats = res
            res = None
        return field, game, is_first


class ONLINE(HUMAN):
    def __init__(self):
        self.name = "ONLINE"
    
    def process_step(self, field, game, is_first, start):
        if game.turn == field.saving_for_online["color"]:
            field, game = self.make_step(start, field, game)
        else:
            field, game = self.get_step(start, field, game)
        return field, game, is_first

    def make_step(self, start, field, game):
        field.x, field.y = -1, -1
        coordinats = field.get_coordinats()
        while (not field.exit and
                (field.name_win is None or
                field.name_win['size'] is None) and
                not field.results):
            (field, game, made_step,
                coordinats) = make_move_in_another_pro(
                field, game, HUMAN(), coordinats)
            if made_step:
                break
            if (start.socket.sock is not None and
                    start.socket.accept() is not None):
                start.socket.send_color_and_size(
                    field.saving_for_online['color'],
                    field.saving_for_online['size'])
                QtWidgets.QMessageBox.information(
                    field, 'Start', 'Enemy connected')
                print("START")
            if start.socket.conn is not None:
                data = start.socket.recv()
                start.check_finish_game_of_enemy(field, game, data)
        if (field.name_win is None or
                field.name_win['size'] is None):
            if start.socket.conn is None:
                start.start_connection(field)
            if (not field.exit and
                    (field.name_win is None or
                        field.name_win['size'] is None) and
                    not field.results):
                start.socket.send(coordinats)
        elif start.socket.conn is not None:
            with contextlib.suppress(OSError):
                start.socket.send('CHANGING_RIVAL')
        return field, game

    def get_step(self, start, field, game):
        if start.socket.conn is None:
            start.start_connection(field)
        coordinats = None
        while (coordinats is None and
                not field.exit and
                (field.name_win is None or
                field.name_win['size'] is None) and
                not field.results):
            coordinats = start.socket.recv()
            start.check_finish_game_of_enemy(
                field, game, coordinats)
            QtCore.QCoreApplication.processEvents()
        if (not field.exit and
                (field.name_win is None or
                    field.name_win['size'] is None) and
                not field.results):
            field, game, _made_step, _coordinats = (
                make_move_in_another_pro(
                    field, game, HUMAN(), coordinats))
        elif (not (field.name_win is None or
                field.name_win['size'] is None) and
                start.socket.conn is not None):
            with contextlib.suppress(OSError):
                start.socket.send('CHANGING_RIVAL')
        return field, game


def sort(first, second):
    if first.name < second.name:
        return first, second
    return second, first

def make_move_in_another_pro(field, game, ai, coordinats=None):
    made_step = False
    q = mp.Queue()
    p = mp.Process(target=ai.make_step, args=(game, q, coordinats))
    p.start()
    while q.empty() and not field.undo_redo_step:
        QtCore.QCoreApplication.processEvents()
    if field.undo_redo_step:
        field.undo_redo_step = False
        return None
    element = q.get()
    if element:
        field.game = game = element 
        made_step = True
    elif isinstance(ai, HUMAN):
        coordinats = field.get_coordinats()
    else:
        q = mp.Queue()
        p = mp.Process(target=AIrandom().make_step, args=(game, q, coordinats))
        p.start()
        while q.empty():
            QtCore.QCoreApplication.processEvents()
        field.game = game = q.get()
    return (field, game,
            made_step, coordinats)