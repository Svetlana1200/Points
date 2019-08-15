import copy
import os
import sys
import unittest

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             os.path.pardir))
from logic import Game, Geometry
from cell import Cell


class GameTest(unittest.TestCase):
    def test_init(self):
        game = Game(3, 3)
        for i in game.field:
            for j in i:
                self.assertEqual(j, Cell.EMPTY)

    def test_put_point(self):
        game = Game(3, 3)
        game.field[1][2] = Cell.RED
        for i in range(game.width):
            for j in range(game.height):
                if i == 1 and j == 2:
                    self.assertEqual(game.field[i][j], Cell.RED)
                else:
                    self.assertEqual(game.field[i][j], Cell.EMPTY)

    def test_change_turn(self):
        game = Game(3, 3)
        start_turn = game.turn
        game.change_turn_player()
        self.assertFalse(start_turn == game.turn)

    def test_in_border(self):
        game = Game(3, 4)
        list_points = [(0, 0), (-1, 2), (2, 2),
                       (1, -1), (7, 1), (1, 7)]
        self.assertTrue(game.in_border(*list_points[0]))
        self.assertFalse(game.in_border(*list_points[1]))
        self.assertTrue(game.in_border(*list_points[2]))
        self.assertFalse(game.in_border(*list_points[3]))
        self.assertFalse(game.in_border(*list_points[4]))
        self.assertFalse(game.in_border(*list_points[5]))

    def test_empty_cell(self):
        game = Game(2, 2)
        self.assertTrue(game.is_empty_cell_on_field())
        game.field[0][0] = Cell.RED
        game.field[1][0] = Cell.RED
        self.assertTrue(game.is_empty_cell_on_field())
        game.field[0][1] = Cell.RED
        game.field[1][1] = Cell.RED
        self.assertFalse(game.is_empty_cell_on_field())

    def test_squre_convex_polygon(self):
        list_points = [(2, 1), (1, 3), (2, 5), (4, 4), (3, 1)]
        self.assertEqual(Geometry.count_squre(list_points), 7.5)

    def test_squre_not_convex_polygon(self):
        list_points = [(2, 1), (2, 3), (1, 2),
                       (2, 4), (3, 5), (5, 3), (3, 2), (4, 1)]
        self.assertEqual(Geometry.count_squre(list_points), 7.5)

    def test_point_in_simple_convex_polygon(self):
        xp = [2, 1, 2, 4, 3]
        yp = [1, 3, 5, 4, 1]
        self.assertFalse(Geometry.point_in_polygon(0, 0, xp, yp))
        self.assertFalse(Geometry.point_in_polygon(2, 1, xp, yp))
        self.assertFalse(Geometry.point_in_polygon(-1, -1, xp, yp))
        self.assertFalse(Geometry.point_in_polygon(5, 5, xp, yp))
        self.assertTrue(Geometry.point_in_polygon(2, 3, xp, yp))
        self.assertTrue(Geometry.point_in_polygon(3, 4, xp, yp))

    def test_point_in_simple_not_convex_polygon(self):
        xp = [2, 2, 1, 2, 3, 5, 3, 4]
        yp = [1, 3, 2, 4, 5, 3, 2, 1]
        self.assertFalse(Geometry.point_in_polygon(0, 0, xp, yp))
        self.assertFalse(Geometry.point_in_polygon(1, 2, xp, yp))
        self.assertFalse(Geometry.point_in_polygon(-1, -1, xp, yp))
        self.assertFalse(Geometry.point_in_polygon(5, 5, xp, yp))
        self.assertTrue(Geometry.point_in_polygon(3, 3, xp, yp))
        self.assertTrue(Geometry.point_in_polygon(4, 3, xp, yp))

    def test_intersection(self):
        game = Game(6, 6)
        first = [(1, 1), (1, 2), (1, 3), (2, 3),
                 (2, 4), (3, 4), (3, 3), (3, 2),
                 (3, 1), (2, 1)]
        second = [(2, 3), (2, 4), (3, 4), (4, 5),
                  (5, 4), (5, 3), (4, 2), (3, 3)]
        self.assertEqual(Geometry.get_intersection(first, second),
                         [(2, 3), (2, 4), (3, 4), (3, 3)])
        for e in first:
            game.field[e[0]][e[1]] = Cell.RED
        for e in second:
            game.field[e[0]][e[1]] = Cell.RED
        game.lines.append((first, Cell.RED))
        self.assertEqual(
            game.count_square_wihtout_intersections(first), 0)
        self.assertEqual(
            game.count_square_wihtout_intersections(second), 4.0)

    def test_no_intersection(self):
        first = [(2, 3), (2, 4), (3, 4), (4, 5),
                 (5, 4), (5, 3), (4, 2), (3, 3)]
        second = [(1, 1), (2, 2), (3, 2), (4, 1), (3, 0), (2, 0)]
        self.assertEqual(Geometry.get_intersection(first, second), [])

    def test_normal_size(self):
        game = Game(3, 3)
        list_points = [(2, 2), (5, 1), (1, 3), (1, 1), (-1, 2), (2, -2)]
        changing_list = game.change_path_in_normal_size(list_points)
        self.assertEqual(
            changing_list,
            [(2, 2), (2, 1), (1, 0), (1, 1), (2, 2), (2, 1)])

    def test_count_score_and_black_points(self):
        game = Game(4, 4)
        path = [(1, 0), (2, 1), (2, 2), (1, 3), (0, 2), (0, 1)]
        for e in path:
            game.field[e[0]][e[1]] = Cell.RED
        game.field[1][1] = Cell.BLUE
        game.make_black_some_points(path)
        for i in range(game.width):
            for j in range(game.height):
                if (i, j) in [(1, 1), (1, 2)]:
                    self.assertTrue(game.field[i][j] == Cell.BLACK)
                else:
                    self.assertTrue(
                        game.field[i][j] == Cell.EMPTY or
                        game.field[i][j] == Cell.RED)
        game.count_score(path, 4.0)
        self.assertEqual(game.score_red, 4.0)
        self.assertEqual(game.score_blue, 0.0)

    def test_can_round(self):
        game = Game(4, 4)
        path = [(1, 0), (2, 1), (2, 2), (1, 3), (0, 2), (0, 1)]
        for e in path:
            game.field[e[0]][e[1]] = Cell.RED
        game.field[1][1] = Cell.BLUE
        self.assertFalse(game.can_round(path))
        game.field[1][2] = Cell.BLUE
        self.assertTrue(game.can_round(path))

    def test_neighboring_points_simple(self):
        game = Game(6, 6)
        game.field[3][2] = Cell.RED
        best_path_and_squre = game.check_neighboring_points(
            3, 2, 3, 2, [((3, 2))], [], 0)
        self.assertEqual(best_path_and_squre, (([], 0)))
        game.field[3][4] = Cell.RED
        game.field[2][3] = Cell.RED
        game.field[3][3] = Cell.BLUE
        game.field[4][3] = Cell.RED
        best_path_and_squre = game.check_neighboring_points(
            4, 3, 4, 3, [((4, 3))], [], 0)
        self.assertEqual(
            best_path_and_squre,
            (([(4, 3), (3, 4), (2, 3), (3, 2), (4, 3)], 2.0)))

    def test_neighboring_points_horiz_border(self):
        game = Game(5, 5)
        game.field[1][0] = Cell.BLUE
        game.field[1][4] = Cell.BLUE
        game.field[1][1] = Cell.RED
        game.field[0][4] = Cell.RED
        game.field[1][3] = Cell.RED
        game.field[0][0] = Cell.RED
        game.field[2][0] = Cell.RED
        game.field[2][4] = Cell.RED

        best_path_and_squre = game.check_neighboring_points(
            2, 4, 2, 4, [((2, 4))], [], 0)
        self.assertEqual(
            best_path_and_squre,
            (([(2, 4), (2, 5), (1, 6), (0, 5), (0, 4), (1, 3), (2, 4)],
                4.0)))

        best_path_and_squre = game.check_neighboring_points(
            0, 0, 0, 0, [((0, 0))], [], 0)
        self.assertEqual(
            best_path_and_squre,
            (([(0, 0), (0, -1), (1, -2), (2, -1), (2, 0), (1, 1), (0, 0)],
                4.0)))

    def test_neighboring_points_vertical_border(self):
        game = Game(5, 5)
        game.field[0][2] = Cell.BLUE
        game.field[4][2] = Cell.BLUE
        game.field[0][1] = Cell.RED
        game.field[1][2] = Cell.RED
        game.field[3][2] = Cell.RED
        game.field[0][3] = Cell.RED
        game.field[4][3] = Cell.RED
        game.field[4][1] = Cell.RED

        best_path_and_squre = game.check_neighboring_points(
            4, 1, 4, 1, [((4, 1))], [], 0)
        self.assertEqual(
            best_path_and_squre,
            (([(4, 1), (5, 1), (6, 2), (5, 3), (4, 3), (3, 2), (4, 1)], 4.0)))

        best_path_and_squre = game.check_neighboring_points(
            0, 3, 0, 3, [((0, 3))], [], 0)
        self.assertEqual(
            best_path_and_squre,
            (([(0, 3), (1, 2), (0, 1), (-1, 1), (-2, 2), (-1, 3), (0, 3)],
                4.0)))

    def test_make_step(self):
        game = Game(6, 6)
        game.field[2][2] = Cell.BLUE
        self.assertEqual(game.field[2][2], Cell.BLUE)

        game.make_step(3, 2)
        game.make_step(2, 1)
        game.make_step(1, 2)
        game.make_step(2, 3)

        for i in range(game.width):
            for j in range(game.height):
                if (i, j) in [(3, 2), (2, 1), (1, 2), (2, 3)]:
                    self.assertEqual(game.field[i][j], Cell.RED)
                elif i == 2 and j == 2:
                    self.assertEqual(game.field[i][j], Cell.BLACK)
                else:
                    self.assertEqual(game.field[i][j], Cell.EMPTY)
        self.assertTrue(game.score_blue == 0.0)
        self.assertTrue(game.score_red == 2.0)
        self.assertListEqual(
            game.lines,
            [(([(2, 3), (3, 2), (2, 1), (1, 2), (2, 3)], Cell.RED, [((2, 2), Cell.BLUE)], 2.0))])

    def test_put_point_on_not_empty(self):
        game = Game(5, 5)
        game.field[3][2] = Cell.BLUE
        game.make_step(3, 2)
        self.assertEqual(game.field[3][2], Cell.BLUE)

    def test_different_siruation(self):
        game = Game(10, 10)
        self.assertEqual(game.turn, Cell.RED)
        game.make_step(2, 3)
        game.make_step(1, 4)
        game.change_turn_player()
        self.assertEqual(game.turn, Cell.BLUE)
        game.make_step(1, 3)
        game.make_step(2, 2)
        game.change_turn_player()
        self.assertEqual(game.turn, Cell.RED)
        game.make_step(0, 3)
        game.make_step(1, 2)
        self.assertEqual(
            game.lines,
            [(([(1, 2), (2, 3), (1, 4), (0, 3), (1, 2)], Cell.RED, [((1, 3), Cell.BLUE)], 2.0))])
        game.make_step(3, 2)
        game.make_step(4, 3)
        game.make_step(2, 1)
        self.assertEqual(
            game.lines,
            [(([(1, 2), (2, 3), (1, 4), (0, 3), (1, 2)], Cell.RED, [((1, 3), Cell.BLUE)], 2.0)),
             (([(2, 1), (3, 2), (2, 3), (1, 2), (2, 1)], Cell.RED, [((2, 2), Cell.BLUE)], 2.0))])

        game.change_turn_player()
        self.assertEqual(game.turn, Cell.BLUE)
        game.make_step(9, 9)
        game.make_step(9, 8)
        game.change_turn_player()
        self.assertEqual(game.turn, Cell.RED)
        game.make_step(8, 9)
        game.make_step(8, 8)
        game.make_step(7, 8)
        game.change_turn_player()
        self.assertEqual(game.turn, Cell.BLUE)
        game.make_step(7, 7)
        game.make_step(8, 7)
        game.make_step(7, 9)
        game.make_step(6, 8)
        game.make_step(8, 0)
        self.assertEqual(
            game.lines,
            [(([(1, 2), (2, 3), (1, 4), (0, 3), (1, 2)], Cell.RED, [((1, 3), Cell.BLUE)], 2.0)),
             (([(2, 1), (3, 2), (2, 3), (1, 2), (2, 1)], Cell.RED, [((2, 2), Cell.BLUE)], 2.0)),
             (([(8, 0), (9, 9), (9, 8), (8, 7), (7, 7),
               (6, 8), (7, 9), (8, 0)], Cell.BLUE, [((7, 8), Cell.RED), ((8, 8), Cell.RED), ((8, 9), Cell.RED)], 5.5))])
        self.assertEqual(game.score_red, 4.0)
        self.assertEqual(game.score_blue, 5.5)
        self.assertEqual(game.get_winner(), Cell.BLUE)

    def test_possible_step_for_computer(self):
        game = Game(3, 2)
        game.possible_steps = game.get_possible_step()
        self.assertEqual(
            game.possible_steps,
            [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0), (2, 1)])
        game.make_step(0, 1)
        self.assertEqual(
            game.possible_steps,
            [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)])

    def test_process(self):
        game = Game(1, 2)
        self.assertEqual(game.turn, Cell.RED)
        self.assertTrue(game.process())
        self.assertEqual(game.turn, Cell.BLUE)
        game.make_step(0, 0)
        self.assertTrue(game.process())
        self.assertEqual(game.turn, Cell.RED)
        game.make_step(0, 1)
        self.assertFalse(game.process())
        self.assertEqual(game.get_winner(), Cell.EMPTY)


if __name__ == '__main__':
    unittest.main()
