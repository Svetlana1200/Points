import copy
import random
import contextlib
from rivals import Rival
from cell import Cell
import time


class Game:
    LENGTH_ROUND = 10
    UNDO_COUNT = 5
    LENGTH_FOR_API = 10
    MAX_TIME = 10

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.field = []
        self.lines = []
        self.score_blue = 0.0
        self.score_red = 0.0
        self.turn = Cell.RED
        self.possible_steps = []

        self.step_enemy_red = []
        self.curent_point_red = None
        self.neigbour_red = set()

        self.step_enemy_blue = []
        self.curent_point_blue = None
        self.neigbour_blue = set()

        self.cancellation = []
        self.repetitions = []

        self.count_red = 0
        self.count_blue = 0

        self.last_red = None
        self.last_blue = None

        self.undo_count = 0

        for x in range(self.width):
            self.field.append([])
            for _y in range(self.height):
                self.field[x].append(Cell.EMPTY)

    def make_step(self,
                  x, y,
                  queue=None,
                  curent_point=None,
                  count_poins=None):
        if not self.in_border(x, y):
            if queue is not None:
                queue.put(False)
            return False
        if self.field[x][y] == Cell.EMPTY:
            self.field[x][y] = self.turn
            if self.turn == Cell.RED:
                self.last_red = (x, y)
            else:
                self.last_blue = (x, y)

            if self.undo_count != 0:
                self.undo_count -= 1
            self.cancellation.append(((x, y), curent_point, count_poins))
            print("MAKE STEP", self.turn, x, y)
            del self.repetitions[:]
            if len(self.cancellation) > Game.UNDO_COUNT * 2 + 2:
                del self.cancellation[0]

            with contextlib.suppress(ValueError):
                self.possible_steps.remove((x, y))

            if self.turn == Cell.RED:
                self.step_enemy_blue.append((x, y))
            else:
                self.step_enemy_red.append((x, y))

            best_path_and_squre = self.check_neighboring_points(
                x, y, x, y, [((x, y))], [], 0, time.time())
            if best_path_and_squre[0]:
                if self.turn == Cell.BLUE:
                    self.curent_point_blue = None
                    self.neigbour_blue = set()
                else:
                    self.curent_point_red = None
                    self.neigbour_red = set()
                jump_list = self.check_intersection_lines(
                    copy.copy(best_path_and_squre[0]))

                if best_path_and_squre[0] != jump_list:
                    square = self.count_square_wihtout_intersections(jump_list)
                    jump_list.append(jump_list[0])
                    best_path_and_squre = (jump_list, square)
                else:
                    best_path_and_squre[0].append(best_path_and_squre[0][0])

                self.count_score(best_path_and_squre[0],
                                 best_path_and_squre[1])
                black_points = self.make_black_some_points(
                    best_path_and_squre[0])
                self.lines.append(
                    (self._change_path_in_normal_size(best_path_and_squre[0]),
                     self.turn,
                     black_points,
                     best_path_and_squre[1]))
                print(self.lines[-1][0], self.lines[-1][1], self.lines[-1][3])
            if queue is not None:
                queue.put(self)
            return True
        if queue is not None:
            queue.put(False)
        return False

    def check_neighboring_points(self, statr_x,
                                 start_y, present_x,
                                 present_y, jump_list,
                                 best_path, best_square, start_time):
        directions = [(-1, -1), (-1, 0), (-1, 1),
                      (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
        for i, j in directions:
            if time.time() - start_time > Game.MAX_TIME:
                return best_path, best_square

            if present_x + i >= self.width:
                xk = present_x + i - self.width
            elif present_x + i == -1:
                xk = self.width - 1
            else:
                xk = present_x + i
            if present_y + j >= self.height:
                yk = present_y + j - self.height
            elif present_y + j == -1:
                yk = self.height - 1
            else:
                yk = present_y + j

            if (abs(xk) < self.width and
                abs(yk) < self.height and
                self.field[xk][yk] == self.field[statr_x][start_y] and
                    (present_x + i, present_y + j) not in jump_list and
                    len(jump_list) < Game.LENGTH_ROUND):
                jump_list.append((present_x + i, present_y + j))
                path_squre = self.check_neighboring_points(
                    statr_x, start_y, present_x + i, present_y + j, jump_list,
                    best_path, best_square, start_time)
                best_path, best_square = path_squre
                jump_list.pop()

        for i, j in directions:
            if time.time() - start_time > Game.MAX_TIME:
                return best_path, best_square

            if (present_x + i == statr_x and
                present_y + j == start_y and
                    len(jump_list) > 2):
                if self.can_round(jump_list):
                    square = self.count_square_wihtout_intersections(jump_list)
                    if (square > best_square or
                        (square == best_square and
                            len(jump_list) < len(best_path))):
                        best_square = square
                        best_path = copy.copy(jump_list)
                        return best_path, best_square
        return best_path, best_square

    def check_intersection_lines(self, path):
        def get_result_of_condition(index, first, second, third, forth):
            if ((second[0] - first[0], second[1] - first[1]),
                (forth[0] - third[0], forth[1] - third[1]),
                (third[0] - second[0], third[1] - second[1])) in [
                    ((-1, -1), (-1, 1), (1, 0)),
                    ((-1, -1), (1, -1), (0, 1)),
                    ((1, 1), (-1, 1), (0, -1)),
                    ((1, 1), (1, -1), (-1, 0)),
                    ((-1, 1), (-1, -1), (1, 0)),
                    ((-1, 1), (1, 1), (0, -1)),
                    ((1, -1), (-1, -1), (0, 1)),
                    ((1, -1), (1, 1), (-1, 0))
                    ]:
                path[index] = third
                path[index + 1] = second
                second, third = third, second
            return second, third

        first, second, third, forth = path[0], path[1], path[2], path[3]
        second, third = get_result_of_condition(1, first, second, third, forth)

        for ind in range(len(path[4:])):
            first, second, third, forth = second, third, forth, path[ind + 4]
            second, third = get_result_of_condition(
                ind + 2, first, second, third, forth)

        first, second, third, forth = second, third, forth, path[0]
        second, third = get_result_of_condition(
            -2, first, second, third, forth)

        first, second, third, forth = second, third, forth, path[1]
        second, third = get_result_of_condition(
            -1, first, second, third, forth)

        first, second, third, forth = second, third, forth, path[2]
        second, third = get_result_of_condition(
            0, first, second, third, forth)

        return path

    def can_round(self, path):
        xp = []
        yp = []
        has_point_larger_size = False
        has_point_smaller_size = False
        for (x, y) in path:
            if (not has_point_larger_size and
               (x >= self.width or y >= self.height)):
                has_point_larger_size = True
            if not has_point_smaller_size and (x < 0 or y < 0):
                has_point_smaller_size = True
            xp.append(x)
            yp.append(y)
        if self.field[xp[0]][yp[0]] == Cell.RED:
            color = Cell.BLUE
        else:
            color = Cell.RED

        all_point = 0
        enemy_point = 0
        for x in range(self.width):
            for y in range(self.height):
                if (Geometry.point_in_polygon(x, y, xp, yp) or
                    (has_point_larger_size and
                    (Geometry.point_in_polygon(x + self.width, y, xp, yp) or
                     Geometry.point_in_polygon(x, y + self.height, xp, yp))) or
                    (has_point_smaller_size and
                    (Geometry.point_in_polygon(x - self.width, y, xp, yp) or
                     Geometry.point_in_polygon(x, y - self.height, xp, yp)))):
                    all_point += 1
                    if self.field[x][y] == color:
                        enemy_point += 1
        return all_point > 0 and enemy_point / all_point >= 0.75

    def count_square_wihtout_intersections(self, present_path):
        x_present = []
        y_present = []
        for (x, y) in present_path:
            x_present.append(x)
            y_present.append(y)

        squre = Geometry.count_squre(present_path)
        changing_path = self._change_path_in_normal_size(present_path)
        for element in self.lines:
            path = element[0]
            intersection = Geometry.get_intersection(
                path, changing_path, present_path)
            if intersection:
                x_another = []
                y_another = []
                for (x, y) in path:
                    x_another.append(x)
                    y_another.append(y)
                change = []
                change.append((intersection[0]))
                for x, y in intersection[1:]:
                    if change[-1][0] - x > self.width/2:
                        xk = self.width + x
                    elif change[-1][0] - x < -self.width/2:
                        xk = x - self.width
                    else:
                        xk = x
                    if change[-1][1] - y > self.height/2:
                        yk = self.height + y
                    elif change[-1][1] - y < -self.height/2:
                        yk = y - self.height
                    else:
                        yk = y
                    change.append((xk, yk))
                squre -= Geometry.count_squre(change)
        return squre

    def count_score(self, path, square):
        if self.field[path[0][0]][path[0][1]] == Cell.RED:
            self.score_red += square
        else:
            self.score_blue += square

    def make_black_some_points(self, path):
        black_points = []
        xp = []
        yp = []
        has_point_larger_size = False
        has_point_smaller_size = False
        for (x, y) in path[:-1]:
            if (not has_point_larger_size and
               (x >= self.width or y >= self.height)):
                has_point_larger_size = True
            if not has_point_smaller_size and (x < 0 or y < 0):
                has_point_smaller_size = True
            xp.append(x)
            yp.append(y)

        for x in range(self.width):
            for y in range(self.height):
                if (Geometry.point_in_polygon(x, y, xp, yp) or
                   (has_point_larger_size and
                   (Geometry.point_in_polygon(x + self.width, y, xp, yp) or
                    Geometry.point_in_polygon(x, y + self.height, xp, yp))) or
                    (has_point_smaller_size and
                    (Geometry.point_in_polygon(x - self.width, y, xp, yp) or
                     Geometry.point_in_polygon(x, y - self.height, xp, yp))) or
                    (has_point_larger_size or has_point_smaller_size) and
                        (Geometry.point_in_polygon(
                            x - self.width, y - self.height, xp, yp) or
                         Geometry.point_in_polygon(
                             x + self.width, y - self.height, xp, yp) or
                         Geometry.point_in_polygon(
                             x - self.width, y + self.height, xp, yp) or
                         Geometry.point_in_polygon(
                             x + self.width, y + self.height, xp, yp))):
                    black_points.append(((x, y), self.field[x][y]))
                    self.field[x][y] = Cell.BLACK
                    with contextlib.suppress(ValueError):
                        self.possible_steps.remove((x, y))
                    with contextlib.suppress(ValueError):
                        if self.turn == Cell.BLUE:
                            self.step_enemy_blue.remove((x, y))
                        else:
                            self.step_enemy_red.remove((x, y))
        return black_points

    def change_turn_player(self):
        if self.turn == Cell.RED:
            self.turn = Cell.BLUE
        else:
            self.turn = Cell.RED

    def process(self):
        self.change_turn_player()

    def is_empty_cell_on_field(self):
        for x in range(self.width):
            for y in range(self.height):
                if self.field[x][y] == Cell.EMPTY:
                    return True
        return False

    def in_border(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height

    def get_winner(self):
        if self.score_red > self.score_blue:
            return Cell.RED
        elif self.score_red < self.score_blue:
            return Cell.BLUE
        return Cell.EMPTY

    def _change_path_in_normal_size(self, path):
        normal = []
        for (x, y) in path:
            if 0 <= x < self.width and 0 <= y < self.height:
                normal.append((x, y))
            elif x >= self.width:
                if y >= self.height:
                    normal.append((x - self.width, y - self.height))
                elif y < 0:
                    normal.append((x - self.width, y + self.height))
                else:
                    normal.append((x - self.width, y))
            elif x < 0:
                if y >= self.height:
                    normal.append((x + self.width, y - self.height))
                elif y < 0:
                    normal.append((x + self.width, y + self.height))
                else:
                    normal.append((x + self.width, y))
            elif y >= self.height:
                normal.append((x, y - self.height))
            elif y < 0:
                normal.append((x, y + self.height))
        return normal

    def get_random_step(self):
        return random.choice(self.possible_steps)

    def get_possible_step(self):
        return [(i, j) for i in range(self.width) for j in range(self.height)]

    def make_easy_or_normal_step(self, ai, queue):
        if ai != Rival.AIeasy and ai != Rival.AInormal:
            print("Ошибка. Этот метод только для AIeasy и AInormal")
        directions = [(-1, 0), (0, 1), (1, 0), (0, -1),
                      (-1, -1), (-1, 1), (1, 1), (1, -1)]
        if self.turn == Cell.BLUE:
            curent_point = self.curent_point_blue
            neigbour = self.neigbour_blue
            steps_enemy = self.step_enemy_blue
        else:
            curent_point = self.curent_point_red
            neigbour = self.neigbour_red
            steps_enemy = self.step_enemy_red
        if self.turn == Cell.RED:
            self.count_red += 1
        else:
            self.count_blue += 1
        while True:
            if (curent_point is None or
                curent_point not in steps_enemy or
                ((self.count_blue >= Game.LENGTH_FOR_API + 1 and
                    self.turn == Cell.BLUE) or
                 (self.count_red >= Game.LENGTH_FOR_API + 1 and
                    self.turn == Cell.RED)) and
                    ai == Rival.AInormal):  # меняем curent_point
                if (neigbour and
                    ((ai == Rival.AInormal and curent_point is None) or
                     ai == Rival.AIeasy)):
                    curent_point = neigbour.pop()
                    neigbour.add(curent_point)
                elif ((self.count_blue >= Game.LENGTH_FOR_API + 1 and
                        self.turn == Cell.BLUE or
                        self.count_red >= Game.LENGTH_FOR_API + 1 and
                        self.turn == Cell.RED)
                        and curent_point is not None
                        and ai == Rival.AInormal):
                    if steps_enemy:
                        curent_point = Geometry.get_farthest_point(
                            steps_enemy, *curent_point,
                            self.width, self.height)
                        neigbour = set()
                        neigbour.add(curent_point)
                        if self.turn == Cell.RED:
                            self.count_red = 1
                        else:
                            self.count_blue = 1
                    else:
                        queue.put(False)
                        return False
                else:
                    if steps_enemy:
                        curent_point = steps_enemy[0]
                        neigbour = set()
                        neigbour.add(curent_point)
                        if self.turn == Cell.RED:
                            self.count_red = 1
                        else:
                            self.count_blue = 1
                    else:
                        queue.put(False)
                        return False
            for i, j in directions:
                if curent_point[0] + i >= self.width:
                    xk = curent_point[0] + i - self.width
                elif curent_point[0] + i == -1:
                    xk = self.width - 1
                else:
                    xk = curent_point[0] + i
                if curent_point[1] + j >= self.height:
                    yk = curent_point[1] + j - self.height
                elif curent_point[1] + j == -1:
                    yk = self.height - 1
                else:
                    yk = curent_point[1] + j

                if self.turn == Cell.RED:
                    count_poins = self.count_red
                else:
                    count_poins = self.count_blue
                count_lines = len(self.lines)
                if self.make_step(xk, yk,
                                  curent_point=curent_point,
                                  count_poins=count_poins):
                    print("BLUE: ", self.count_blue, ", RED: ", self.count_red)
                    if count_lines == len(self.lines):
                        if self.turn == Cell.BLUE:
                            self.curent_point_blue = curent_point
                            self.neigbour_blue = neigbour
                            self.step_enemy_blue = steps_enemy
                        else:
                            self.curent_point_red = curent_point
                            self.neigbour_red = neigbour
                            self.step_enemy_red = steps_enemy
                    elif ai == Rival.AInormal:
                        if self.turn == Cell.BLUE:
                            self.count_blue = 0
                        else:
                            self.count_red = 0
                    queue.put(self)
                    return True

                if ((self.turn == Cell.BLUE and
                     self.field[xk][yk] == Cell.RED) or
                        (self.turn == Cell.RED and
                         self.field[xk][yk] == Cell.BLUE) and
                        ((xk, yk)) in steps_enemy):
                    neigbour.add((xk, yk))

            with contextlib.suppress(KeyError):
                neigbour.remove(curent_point)
            with contextlib.suppress(ValueError):
                steps_enemy.remove(curent_point)
            curent_point = None

    def _get_neigbours_steps_enemys(self, color_undo_point):
        if color_undo_point == Cell.RED:
            return (self.neigbour_red, self.step_enemy_red,
                    self.neigbour_blue,  self.step_enemy_blue)
        else:
            return (self.neigbour_blue, self.step_enemy_blue,
                    self.neigbour_red, self.step_enemy_red)

    def undo(self, enemy):
        if self.undo_count > Game.UNDO_COUNT * 2:
            raise IndexError
        (x, y), curent_point, count_poins = self.cancellation.pop()
        print("UNDO ", x, y)
        if enemy == Rival.AInormal and len(self.cancellation) > 0:
            ((next_x, next_y),
             _next_curent_point,
             _next_count_poins) = self.cancellation[-1]
        else:
            next_x, next_y = None, None
        self.possible_steps.append((x, y))
        find_line = False
        color_undo_point = self.field[x][y]
        self.field[x][y] = Cell.EMPTY
        (neigbour, step_enemy,
         neigbour_another,
         step_enemy_another) = self._get_neigbours_steps_enemys(
             color_undo_point)

        for line in self.lines:
            if (x, y) in line[0]:
                find_line = True
                self.repetitions.append(
                    ((x, y), color_undo_point, line,
                     curent_point, count_poins))
                self.lines.remove(line)
                if enemy == Rival.AIeasy or enemy == Rival.AInormal:
                    neigbour.add(curent_point)
                    step_enemy.insert(0, curent_point)
                    if color_undo_point == Cell.RED:
                        self.curent_point_red = curent_point
                    else:
                        self.curent_point_blue = curent_point
                for ((black_x, black_y), color_early) in line[2]:  # черные т.
                    self.field[black_x][black_y] = color_early
                if line[1] == Cell.BLUE:  # цвет
                    self.score_blue -= line[3]  # площадь
                else:
                    self.score_red -= line[3]
                break
        if not find_line:
            self.repetitions.append(
                ((x, y), color_undo_point, (), curent_point, count_poins))
        try:
            if color_undo_point == Cell.RED:
                self.last_red = self.cancellation[-2][0]
            else:
                self.last_blue = self.cancellation[-2][0]
        except IndexError:
            if color_undo_point == Cell.RED:
                self.last_red = None
            else:
                self.last_blue = None
        self.undo_count += 1
        if enemy == Rival.AIrandom:
            return

        if curent_point is not None:
            if (enemy == Rival.AIeasy or
                    enemy == Rival.AInormal and
                    curent_point == (next_x, next_y)):
                if color_undo_point == Cell.RED:
                    self.curent_point_red = None
                    self.neigbour_red = set()
                else:
                    self.curent_point_blue = None
                    self.neigbour_blue = set()
            elif enemy == Rival.AInormal:
                if curent_point not in step_enemy:
                    step_enemy.append(curent_point)
                if color_undo_point == Cell.RED:
                    self.curent_point_red = curent_point
                    self.neigbour_red = set()
                else:
                    self.curent_point_blue = curent_point
                    self.neigbour_blue = set()
            if enemy == Rival.AInormal:
                if color_undo_point == Cell.RED:
                    self.count_red -= 1
                    if self.count_red <= 0:
                        self.count_red = count_poins - 1
                else:
                    self.count_blue -= 1
                    if self.count_blue <= 0:
                        self.count_blue = count_poins - 1
        with contextlib.suppress(KeyError):
            neigbour_another.remove((x, y))
        with contextlib.suppress(ValueError):
            step_enemy_another.remove((x, y))
        print("BLUE: ", self.count_blue, ", RED: ", self.count_red)

    def redo(self, enemy):
        ((x, y), color_undo_point,
         line, curent_point, count_poins) = self.repetitions.pop()
        print("REDO ", x, y)
        self.cancellation.append(((x, y), curent_point, count_poins))
        if enemy == Rival.AInormal and len(self.repetitions) > 0:
            ((next_x, next_y), _next_color_undo_point,
             _next_line, _next_curent_point,
             _next_count_poins) = self.repetitions[-1]
        else:
            next_x, next_y = None, None
        self.possible_steps.remove((x, y))
        self.field[x][y] = color_undo_point
        (neigbour, step_enemy,
         neigbour_another,
         step_enemy_another) = self._get_neigbours_steps_enemys(
             color_undo_point)

        if len(line) > 0:
            self.lines.append(line)
            if enemy == Rival.AIeasy or enemy == Rival.AInormal:
                with contextlib.suppress(KeyError):
                    neigbour.remove(curent_point)
                with contextlib.suppress(ValueError):
                    step_enemy.remove(curent_point)
            if color_undo_point == Cell.BLUE:  # цвет
                self.score_blue += line[3]  # площадь
                self.curent_point_blue = None
                self.neigbour_blue = set()
            else:
                self.score_red += line[3]
                self.curent_point_red = None
                self.neigbour_red = set()
            for ((black_x, black_y), _color) in line[2]:  # черные точки
                self.field[black_x][black_y] = Cell.BLACK
        if color_undo_point == Cell.RED:
            self.last_red = (x, y)
        else:
            self.last_blue = (x, y)
        self.undo_count -= 1
        if enemy == Rival.AIrandom:
            return

        if curent_point is not None:
            if (enemy == Rival.AIeasy or
                    enemy == Rival.AInormal and
                    curent_point == (next_x, next_y)):
                if color_undo_point == Cell.RED:
                    self.curent_point_red = curent_point
                else:
                    self.curent_point_blue = curent_point
            if enemy == Rival.AInormal:
                if color_undo_point == Cell.RED:
                    self.count_red += 1
                    if self.count_red > count_poins:
                        self.count_red = 1
                else:
                    self.count_blue += 1
                    if self.count_blue > count_poins:
                        self.count_blue = 1
        with contextlib.suppress(KeyError):
            neigbour_another.add((x, y))
        with contextlib.suppress(ValueError):
            step_enemy_another.append((x, y))
        print("BLUE: ", self.count_blue, ", RED: ", self.count_red)


class Geometry:
    @staticmethod
    def get_intersection(path, c_present_path, present_path):
        xp = []
        yp = []
        for (x, y) in present_path[:-1]:
            xp.append(x)
            yp.append(y)
        intersection = []

        for point_path in path:
            for point_present_path in c_present_path:
                if (point_path == point_present_path or
                    Geometry.point_in_polygon(
                        point_path[0], point_path[1], xp, yp)):
                    intersection.append(point_path)
                    break
        return intersection

    @staticmethod
    def point_in_polygon(x, y, xp, yp):
        c = False
        for i in range(len(xp)):
            if x == xp[i] and y == yp[i]:
                return False
            if (((yp[i] <= y and y < yp[i-1]) or
                (yp[i-1] <= y and y < yp[i])) and
                (x > (xp[i-1] - xp[i]) * (y - yp[i]) /
                    (yp[i-1] - yp[i]) + xp[i])):
                c = not c
        return c

    @staticmethod
    def count_squre(path):
        res = 0
        for i in range(len(path)):
            k = (i + 1) % len(path)
            res += path[i][0] * path[k][1] - path[k][0]*path[i][1]
        return abs(res) / 2

    @staticmethod
    def get_farthest_point(list_points, curent_x, curent_y, width, height):
        farthest_point_x = curent_x
        farthest_point_y = curent_y
        max_dist = 0
        for x, y in list_points:
            dist = min(
                ((abs(x - curent_x))**2 +
                 (abs(y - curent_y))**2)**(1/2),
                ((width - abs(x - curent_x))**2 +
                 (abs(y - curent_y))**2)**(1/2),
                ((abs(x - curent_x))**2 +
                 (height - abs(y - curent_y))**2)**(1/2),
                ((width - abs(x - curent_x))**2 +
                 (height - abs(y - curent_y))**2)**(1/2)
                )
            if dist > max_dist:
                max_dist = dist
                farthest_point_x = x
                farthest_point_y = y
        return farthest_point_x, farthest_point_y
