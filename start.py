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


class Start:
    def __init__(self):
        self.socket = None

    def start_game(self):
        _app = QtWidgets.QApplication(sys.argv)
        game = Game(20, 20)

        high_scores = Start.get_high_scores(game)
        rival = ((Rival.HUMAN, Rival.HUMAN))
        field = Field(game, high_scores, rival)
        
        game.possible_steps = game.get_possible_step()
        isFirst = True
        while isFirst or game.process():
            field.update()
            isFirst = False
            if field.name_win and field.name_win['size']:

                if field.name_win.get('first', None) is None:
                    try:
                        self.socket = Socket((field.saving_for_online["ip"], 14900))
                        print("socket") 
                    except (TimeoutError, ConnectionRefusedError):
                        field.name_win = None
                        QtWidgets.QMessageBox.critical(field, 'IP', 'Недопустимый ip!')
                if field.name_win:
                    if rival == (Rival.ONLINE, Rival.ONLINE):
                        with contextlib.suppress(AttributeError):
                            self.socket.sock.close()
                        with contextlib.suppress(AttributeError):
                            self.socket.conn.close()

                    game, field, rival = Start.change_rival(
                        game, field)# копипаста 1 начало
                    if rival == (Rival.ONLINE, Rival.ONLINE):
                        if self.socket.conn is not None:
                            color_size = self.socket.recv_color_and_size()
                            while color_size is None: # возможно не надо
                                color_size = self.socket.recv_color_and_size()
                            color, size = color_size
                            field.name_win = {}
                            field.name_win['size'] = size
                            field.saving_for_online = {}
                            if color == Cell.RED:
                                field.saving_for_online["color"] = Cell.BLUE
                            else:
                                field.saving_for_online["color"] = Cell.RED
                            field.saving_for_online["ip"] = self.socket.adress[0]
                            field.saving_for_online["size"] = size
                            game, field, rival = Start.change_rival(
                                game, field)    
                    isFirst = True
                    continue # копипаста 1 конец
            if Rival.HUMAN not in rival:
                field.update()
                if field.results:
                    field.winner = game.get_winner()
                    field.update()
                    while not field.exit:
                        QtCore.QCoreApplication.processEvents()  
                    return                    
                if field.exit:
                    return
                QtTest.QTest.qWait(100)

            if (rival[0] == Rival.AIrandom and game.turn == Cell.BLUE or
               rival[1] == Rival.AIrandom and game.turn == Cell.RED):
                coordinats = game.get_random_step()
                game.make_step(*coordinats)
                continue
            if (rival[0] == Rival.AIeasy and game.turn == Cell.BLUE or
               rival[1] == Rival.AIeasy and game.turn == Cell.RED):
                if not game.make_easy_or_normal_step(Rival.AIeasy):
                    coordinats = game.get_random_step()
                    game.make_step(*coordinats)
                continue
            if (rival[0] == Rival.AInormal and game.turn == Cell.BLUE or
               rival[1] == Rival.AInormal and game.turn == Cell.RED):
                if not game.make_easy_or_normal_step(Rival.AInormal):
                    coordinats = game.get_random_step()
                    game.make_step(*coordinats)
                continue

            if rival == (Rival.ONLINE, Rival.ONLINE):
                if game.turn == field.saving_for_online["color"]:
                    field.x, field.y = -1, -1
                    coordinats = field.get_coordinats()
                    while (not game.make_step(*coordinats)) and not field.exit and (field.name_win is None or field.name_win['size'] is None):
                        if self.socket.sock is not None and self.socket.accept() is not None:
                            self.socket.send_color_and_size(field.saving_for_online['color'], field.saving_for_online['size'])
                            QtWidgets.QMessageBox.information(field, 'Start', 'Enemy connected')
                            print("START")
                        if self.socket.conn is not None:
                            data = self.socket.recv()
                            if data == 'EXIT' or data == 'CHANGING_RIVAL': # копипаста 3
                                print(data) # копипаста 3
                                field.winner = game.get_winner() # копипаста 3
                                field.update() # копипаста 3
                                while not field.exit: # копипаста 3
                                    QtCore.QCoreApplication.processEvents() # копипаста 3
                                break
                        QtCore.QCoreApplication.processEvents()
                        coordinats = field.get_coordinats()
                    
                    if field.name_win is None or field.name_win['size'] is None:
                        if self.socket.conn is None:
                            while self.socket.accept() is None and not field.exit: # копипаста 2
                                QtCore.QCoreApplication.processEvents() # копипаста 2
                            if not field.exit and (field.name_win is None or field.name_win['size'] is None):
                                self.socket.send_color_and_size(field.saving_for_online['color'], field.saving_for_online['size']) # копипаста 2 
                                QtWidgets.QMessageBox.information(field, 'Start', 'Enemy connected')
                                print("START") # копипаста 2
                        if not field.exit and (field.name_win is None or field.name_win['size'] is None):
                            self.socket.send(coordinats)
                    elif self.socket.conn is not None:
                        self.socket.send('CHANGING_RIVAL')
                else:
                    if self.socket.conn is None:
                        while self.socket.accept() is None and not field.exit and (field.name_win is None or field.name_win['size'] is None): # копипаста 2
                            QtCore.QCoreApplication.processEvents() # копипаста 2
                        if not field.exit and (field.name_win is None or field.name_win['size'] is None):
                            self.socket.send_color_and_size(field.saving_for_online['color'], field.saving_for_online['size']) # копипаста 2
                            QtWidgets.QMessageBox.information(field, 'Start', 'Enemy connected')
                            print("START") # копипаста 2
                    coordinats = None
                    while coordinats is None and not field.exit and (field.name_win is None or field.name_win['size'] is None):
                        coordinats = self.socket.recv()
                        if coordinats == 'EXIT' or coordinats == 'CHANGING_RIVAL': # копипаста 3
                            print(coordinats) # копипаста 3
                            field.winner = game.get_winner() # копипаста 3
                            field.update() # копипаста 3
                            while not field.exit: # копипаста 3
                                QtCore.QCoreApplication.processEvents() # копипаста 3
                        QtCore.QCoreApplication.processEvents()
                    if not field.exit and (field.name_win is None or field.name_win['size'] is None):
                        game.make_step(*coordinats)
                    elif not (field.name_win is None or field.name_win['size'] is None) and self.socket.conn is not None:
                        self.socket.send('CHANGING_RIVAL')
            else:
                field.x, field.y = -1, -1
                coordinats = field.get_coordinats()
                while (not game.make_step(*coordinats)) and not field.exit and not field.results:
                    QtCore.QCoreApplication.processEvents()
                    coordinats = field.get_coordinats()                    
                    if field.name_win and field.name_win['size']: # копипаста 1 начало
                        if field.name_win.get('first', None) is None:
                            try:
                                self.socket = Socket((field.saving_for_online["ip"], 14900))
                                print("socket")
                            except (TimeoutError, ConnectionRefusedError):
                                field.name_win = None
                                QtWidgets.QMessageBox.critical(field, 'IP', 'Недопустимый ip!')
                        if field.name_win:
                        
                            if rival == (Rival.ONLINE, Rival.ONLINE):
                                with contextlib.suppress(AttributeError):
                                    self.socket.sock.close()
                                with contextlib.suppress(AttributeError):
                                    self.socket.conn.close()
                            game, field, rival = Start.change_rival(
                                game, field)
                            if rival == (Rival.ONLINE, Rival.ONLINE):

                                if self.socket.conn is not None:
                                    color_size = self.socket.recv_color_and_size()
                                    while color_size is None: # возможно не надо
                                        color_size = self.socket.recv_color_and_size()
                                    color, size = color_size
                                    field.name_win = {}
                                    field.name_win['size'] = size
                                    field.saving_for_online = {}
                                    if color == Cell.RED:
                                        field.saving_for_online["color"] = Cell.BLUE
                                    else:
                                        field.saving_for_online["color"] = Cell.RED
                                    field.saving_for_online["ip"] = self.socket.adress[0]
                                    field.saving_for_online["size"] = size
                                    game, field, rival = Start.change_rival(
                                        game, field)    
                            isFirst = True # копипаста 1 конец
                            break
            
            if field.exit:
                if rival == (Rival.ONLINE, Rival.ONLINE) and self.socket.conn is not None:
                    self.socket.send('EXIT')
                    print("send exit")
                return

            if field.results:
                field.winner = game.get_winner()
                field.update()
                if ((Rival.AIeasy in rival or Rival.AIrandom in rival or Rival.AInormal in rival) and
                    field.high_scores is not None):
                    stat = Start.make_stat(game, field.high_scores, rival)
                    _records = RecordsWin(stat)
                while not field.exit:
                    QtCore.QCoreApplication.processEvents()

        if rival == (Rival.ONLINE, Rival.ONLINE):
            with contextlib.suppress(AttributeError):
                self.socket.sock.close()
            with contextlib.suppress(AttributeError):
                self.socket.conn.close()
        field.winner = game.get_winner()
        field.update()
        if (Rival.AIeasy in rival or Rival.AIrandom in rival or Rival.AInormal in rival) and Rival.HUMAN in rival:
            stat = Start.make_stat(game, field.high_scores, rival)
            _records = RecordsWin(stat)
        while not field.exit:
            QtCore.QCoreApplication.processEvents()    

    @staticmethod
    def change_rival(game, field):
        size = tuple(map(int, field.name_win['size'].split('x')))
        game = Game(size[0], size[1])

        rival = ((field.name_win.get('first', None), field.name_win.get('second', None)))
        if rival == (None, None):
            color = field.saving_for_online["color"]
            ip = field.saving_for_online["ip"]
            size = field.saving_for_online["size"]
            rival = (Rival.ONLINE, Rival.ONLINE)
            
        high_scores = Start.get_high_scores(game)
        field = Field(game, high_scores, rival)
        if rival == (Rival.ONLINE, Rival.ONLINE):
            field.saving_for_online = {}
            field.saving_for_online["color"] = color
            field.saving_for_online["ip"] = ip
            field.saving_for_online["size"] = size
        game.possible_steps = game.get_possible_step()
        return game, field, rival

    @staticmethod
    def get_high_scores(game):
        name_file = name_file = f'{game.width}x{game.height}.txt'
        high_scores = []
        if os.path.exists(name_file) and os.stat(name_file).st_size != 0:
            try:
                with open(name_file, 'rb') as f:
                    try:
                        high_scores = pickle.load(f)
                    except (pickle.UnpicklingError):
                        return None
            except PermissionError:
                return None
        try:
            with open(name_file, 'wb') as f:
                pickle.dump(high_scores, f)
        except PermissionError:
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
