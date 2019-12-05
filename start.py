import sys
from PyQt5 import QtWidgets, QtCore, QtTest
import os
import pickle
import operator
from logic import Game
from cell import Cell
from gui import Field, RecordsWin, Rival
from soket import Socket
import contextlib
import multiprocessing as mp
from players import AIrandom, AIeasy, AInormal, HUMAN, ONLINE, AI


class Start:
    def __init__(self):
        self.socket = None

    def start_game(self):
        _app = QtWidgets.QApplication(sys.argv)
        game = Game(20, 20)
        high_scores = Start.get_high_scores(game)
        rival = Rival.HUMAN, Rival.HUMAN
        field = Field(game, high_scores, rival)
        is_first = True
        game.possible_steps = game.get_possible_step()
        
        while not field.exit:
            if not is_first:
                game.process()
            field.update()
            is_first = False

            if game.turn == Cell.BLUE:
                current_player = field.rival_obj[0]
            else:
                current_player = field.rival_obj[1]
            current_turn = game.turn

            if isinstance(current_player, AI):
                field, game, is_first = current_player.process_step(field, game, current_player, current_turn)
            else:
                field, game, is_first = current_player.process_step(field, game, is_first, self)

            if field.results or not game.is_empty_cell_on_field():
                if (rival == (Rival.ONLINE, Rival.ONLINE) and
                        self.socket.conn is not None):
                    with contextlib.suppress(OSError):
                        self.socket.send('RESULTS')
                        print("send results")
                    with contextlib.suppress(AttributeError):
                        self.socket.sock.close()
                    with contextlib.suppress(AttributeError):
                        self.socket.conn.close()
                field.winner = game.get_winner()
                field.update()
                if ((isinstance(field.rival_obj[0], AI) or isinstance(field.rival_obj[1], AI)) and
                        Rival.HUMAN in rival and
                        field.high_scores is not None):
                    stat = Start.make_stat(game, field.high_scores, rival)
                    _records = RecordsWin(stat)
                while ((field.name_win is None or
                        field.name_win['size'] is None) and
                        not field.exit):
                    QtCore.QCoreApplication.processEvents()
            if field.name_win and field.name_win['size']:
                game, field, rival, is_first = (
                    self.start_new_game(game, field, rival))
            if Rival.HUMAN not in rival and Rival.ONLINE not in rival:
                QtTest.QTest.qWait(100)
        if (rival == (Rival.ONLINE, Rival.ONLINE) and
                self.socket.conn is not None):
            with contextlib.suppress(OSError):
                self.socket.send('EXIT')
                print("send exit")
            with contextlib.suppress(AttributeError):
                self.socket.sock.close()
            with contextlib.suppress(AttributeError):
                self.socket.conn.close()

    def start_connection(self, field):
        if self.socket.conn is None:
            while (self.socket.accept() is None and
                    not field.exit and
                    (field.name_win is None or
                     field.name_win['size'] is None) and
                    not field.results):
                QtCore.QCoreApplication.processEvents()
            if (not field.exit and
                (field.name_win is None or field.name_win['size'] is None) and
                    not field.results):
                self.socket.send_color_and_size(
                    field.saving_for_online['color'],
                    field.saving_for_online['size'])
                QtWidgets.QMessageBox.information(
                    field, 'Start', 'Enemy connected')
                print("START")

    def start_new_game(self, game, field, rival):
        is_first = False
        if field.name_win.get('first', None) is None:
            try:
                with contextlib.suppress(AttributeError):
                    self.socket.sock.close()
                with contextlib.suppress(AttributeError):
                    self.socket.conn.close()
                self.socket = Socket((field.saving_for_online["ip"], 14900))
                print("socket")
            except (TimeoutError, ConnectionRefusedError):
                field.name_win = None
                QtWidgets.QMessageBox.critical(field, 'IP', 'Недопустимый ip!')
        if field.name_win:
            game, field, rival = Start.change_rival_field_game(
                game, field)
            if rival == (Rival.ONLINE, Rival.ONLINE):
                if self.socket.conn is not None:
                    color_size = self.socket.recv_color_and_size()
                    while color_size is None:
                        color_size = self.socket.recv_color_and_size()
                    color, size = color_size
                    field.name_win = {}
                    field.name_win['size'] = size
                    field.saving_for_online = {
                        "ip": self.socket.adress[0],
                        "size": size
                        }
                    if color == Cell.RED:
                        field.saving_for_online["color"] = Cell.BLUE
                    else:
                        field.saving_for_online["color"] = Cell.RED
                    game, field, rival = Start.change_rival_field_game(
                        game, field)
            is_first = True
        return game, field, rival, is_first

    def check_finish_game_of_enemy(self, field, game, value):
        if value == 'EXIT' or value == 'CHANGING_RIVAL' or value == 'RESULTS':
            with contextlib.suppress(AttributeError):
                self.socket.sock.close()
            with contextlib.suppress(AttributeError):
                self.socket.conn.close()
            print(value)
            field.winner = game.get_winner()
            field.update()
            while ((field.name_win is None or field.name_win['size'] is None)
                    and not field.exit):
                QtCore.QCoreApplication.processEvents()

    @staticmethod
    def change_rival_field_game(game, field):
        size = tuple(map(int, field.name_win['size'].split('x')))
        game = Game(size[0], size[1])
        rival = (field.name_win.get('first', None),
                 field.name_win.get('second', None))
        if rival == (None, None):
            color = field.saving_for_online["color"]
            ip = field.saving_for_online["ip"]
            size = field.saving_for_online["size"]
            rival = (Rival.ONLINE, Rival.ONLINE)
        high_scores = Start.get_high_scores(game)

        field = Field(game, high_scores, rival)
        if rival == (Rival.ONLINE, Rival.ONLINE):
            field.saving_for_online = {
                "color": color,
                "ip": ip,
                "size": size}
        game.possible_steps = game.get_possible_step()
        return game, field, rival

    @staticmethod
    def get_high_scores(game):
        name_file = name_file = f'{game.width}x{game.height}.txt'
        high_scores = []
        try:
            if os.path.exists(name_file) and os.stat(name_file).st_size != 0:
                with open(name_file, 'rb') as f:
                    high_scores = pickle.load(f)
            with open(name_file, 'wb') as f:
                pickle.dump(high_scores, f)
        except (Exception, pickle.UnpicklingError):
            return None
        return high_scores

    @staticmethod
    def make_stat(game, high_scores, rival):
        name_file = name_file = f'{game.width}x{game.height}.txt'
        records = RecordsWin(high_scores)
        records.showDialog()
        if records.name is not None:
            if rival[0] == Rival.HUMAN:
                high_scores.append((records.name, game.score_blue))
            elif rival[1] == Rival.HUMAN:
                high_scores.append((records.name, game.score_red))
            high_scores = sorted(high_scores, key=operator.itemgetter(1),
                                 reverse=True)[:7]
            with open(name_file, 'wb') as f:
                pickle.dump(high_scores, f)
        return high_scores


def main():
    start = Start()
    start.start_game()


if __name__ == '__main__':
    main()
