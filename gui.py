import sys
from PyQt5 import QtWidgets, QtCore, QtGui, QtTest
import os
from enum import Enum
from logic import Game
from cell import Cell
import contextlib
from rivals import Rival


class StartGameWindowNotOnline(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Setting')
        self._sel_layout = QtWidgets.QVBoxLayout()

        items = ['15x15', '20x20', '30x30']

        for i in items:
            self._sel_layout.addWidget(QtWidgets.QRadioButton(i))

        self._other = QtWidgets.QRadioButton('Another size')
        self._other.toggled.connect(self._click_other)
        self._sel_layout.addWidget(self._other)

        self._sel_layout.itemAt(0).widget().setChecked(True)

        self._selector = QtWidgets.QGroupBox()
        self._selector.setTitle('Size')
        self._selector.setLayout(self._sel_layout)

        self._inputs = QtWidgets.QHBoxLayout()
        inp = QtWidgets.QLineEdit()
        self._inputs.addWidget(inp)
        self._inputs.itemAt(0).widget().setPlaceholderText('15x15')
        self._hide_inputs()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._selector)
        layout.addLayout(self._inputs)

        players = ['Blue player', 'Red player']

        self.player_states = {
            'human': Rival.HUMAN,
            'random': Rival.AIrandom,
            'easy': Rival.AIeasy, 
            'normal': Rival.AInormal
        }

        self._player_layouts = []
        for player in players:
            self._sel_layout_new = QtWidgets.QVBoxLayout()

            for state in self.player_states.keys():
                self._sel_layout_new.addWidget(QtWidgets.QRadioButton(state))

            self._sel_layout_new.itemAt(0).widget().setChecked(True)
            self._player_layouts.append(self._sel_layout_new)

            self._selector_new = QtWidgets.QGroupBox()
            self._selector_new.setTitle(player)
            self._selector_new.setLayout(self._sel_layout_new)

            layout.addWidget(self._selector_new)

        self._buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        layout.addWidget(self._buttons)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setLayout(layout)
        self.show()

    def _click_other(self, show):
        self._hide_inputs(not show)
        if show:
            inp = self._inputs.itemAt(0).widget()
            QtCore.QTimer.singleShot(
                0, lambda: inp.setFocus(QtCore.Qt.OtherFocusReason))

    def _hide_inputs(self, value=True):
        for idx in range(self._inputs.count()):
            self._inputs.itemAt(idx).widget().setVisible(not value)

        self.resize(self.width(), self.minimumSizeHint().height())

    def set_size(self):
        def check(params):
            try:
                size = tuple(map(int, params.split('x')))                
                if (size[0] <= 5 or size[1] <= 5 or size[0] * 20 >
                          QtWidgets.QDesktopWidget()
                            .availableGeometry().height() - 200 or
                          size[1] * 20 >
                          QtWidgets.QDesktopWidget()
                            .availableGeometry().height() - 200):
                    QtWidgets.QMessageBox.critical(self, 'Size',
                                         'Недопустимый размер поля!')
                else:
                    return params
            except (IndexError, ValueError):
                QtWidgets.QMessageBox.critical(self, 'Size', 'Wrong format!')

        if self._other.isChecked():
            return check(self._inputs.itemAt(0).widget().text())

        for i in range(self._sel_layout.count() - 1):
            if self._sel_layout.itemAt(i).widget().isChecked():
                return self._sel_layout.itemAt(i).widget().text()

    def set_players(self):
        players = []
        for layout in self._player_layouts:
            for i in range(layout.count()):
                if layout.itemAt(i).widget().isChecked():
                    players.append(
                        self.player_states[layout.itemAt(i).widget().text()])
        return players


class StartGameWindowOnline(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Setting')
        self._sel_layout = QtWidgets.QVBoxLayout()

        items = ['15x15', '20x20', '30x30']

        for i in items:
            self._sel_layout.addWidget(QtWidgets.QRadioButton(i))

        self._other = QtWidgets.QRadioButton('Another size')
        self._other.toggled.connect(self._click_other)
        self._sel_layout.addWidget(self._other)

        self._sel_layout.itemAt(0).widget().setChecked(True)

        self._selector = QtWidgets.QGroupBox()
        self._selector.setTitle('Size')
        self._selector.setLayout(self._sel_layout)

        self._inputs = QtWidgets.QHBoxLayout()
        inp = QtWidgets.QLineEdit()
        self._inputs.addWidget(inp)
        self._inputs.itemAt(0).widget().setPlaceholderText('15x15')
        self._hide_inputs()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._selector)
        layout.addLayout(self._inputs)

        color_str = 'Color'

        self.color_states = {
            'red': Cell.RED,
            'blue': Cell.BLUE
        }

        self._color_layout = None
        self._sel_layout_new = QtWidgets.QVBoxLayout()
        for state in self.color_states.keys():
            self._sel_layout_new.addWidget(QtWidgets.QRadioButton(state))
        self._sel_layout_new.itemAt(0).widget().setChecked(True)
        self._color_layout = self._sel_layout_new

        self._selector_new = QtWidgets.QGroupBox()
        self._selector_new.setTitle(color_str)
        self._selector_new.setLayout(self._sel_layout_new)

        layout.addWidget(self._selector_new)
        self._buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        layout.addWidget(self._buttons)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setLayout(layout)
        self.show()

    def _click_other(self, show):
        self._hide_inputs(not show)
        if show:
            inp = self._inputs.itemAt(0).widget()
            QtCore.QTimer.singleShot(
                0, lambda: inp.setFocus(QtCore.Qt.OtherFocusReason))

    def _hide_inputs(self, value=True):
        for idx in range(self._inputs.count()):
            self._inputs.itemAt(idx).widget().setVisible(not value)

        self.resize(self.width(), self.minimumSizeHint().height())

    def set_size(self):
        def check(params):
            try:
                size = tuple(map(int, params.split('x')))                
                if (size[0] <= 5 or size[1] <= 5 or size[0] * 20 >
                            QtWidgets.QDesktopWidget()
                            .availableGeometry().height() - 200 or
                            size[1] * 20 >
                            QtWidgets.QDesktopWidget()
                            .availableGeometry().height() - 200):
                    QtWidgets.QMessageBox.critical(self, 'Size',
                                            'Недопустимый размер поля!')
                else:
                    return params
            except (IndexError, ValueError):
                QtWidgets.QMessageBox.critical(self, 'Size', 'Wrong format!')

        if self._other.isChecked():
            return check(self._inputs.itemAt(0).widget().text())

        for i in range(self._sel_layout.count() - 1):
            if self._sel_layout.itemAt(i).widget().isChecked():
                return self._sel_layout.itemAt(i).widget().text()

    def set_color(self):
        for i in range(self._sel_layout_new.count()):
            if self._sel_layout_new.itemAt(i).widget().isChecked():
                return self.color_states[self._sel_layout_new.itemAt(i).widget().text()]
    

class OnlineOrNotWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Setting')
        self._sel_layout = QtWidgets.QVBoxLayout()

        items = ['not online']

        for i in items:
            self._sel_layout.addWidget(QtWidgets.QRadioButton(i))

        self._online = QtWidgets.QRadioButton('online')
        self._online.toggled.connect(self._click_online)
        self._sel_layout.addWidget(self._online)

        self._sel_layout.itemAt(0).widget().setChecked(True)

        self._selector = QtWidgets.QGroupBox()
        self._selector.setTitle('Online or not')
        self._selector.setLayout(self._sel_layout)

        self._inputs = QtWidgets.QHBoxLayout()
        inp = QtWidgets.QLineEdit()
        self._inputs.addWidget(inp)
        self._inputs.itemAt(0).widget().setPlaceholderText('000.000.000.000')
        self._hide_inputs()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self._selector)
        layout.addLayout(self._inputs)

        
        self._buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        layout.addWidget(self._buttons)
        layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setLayout(layout)
        self.show()

    def _click_online(self, show):
        self._hide_inputs(not show)
        if show:
            inp = self._inputs.itemAt(0).widget()
            QtCore.QTimer.singleShot(
                0, lambda: inp.setFocus(QtCore.Qt.OtherFocusReason))
    
    def _hide_inputs(self, value=True):
        for idx in range(self._inputs.count()):
            self._inputs.itemAt(idx).widget().setVisible(not value)

        self.resize(self.width(), self.minimumSizeHint().height())

    def set_online(self):
        def check(params):
            parts = params.split('.')
            if len(parts) != 4:
                QtWidgets.QMessageBox.critical(self, 'IP', 'Недопустимый ip!')
                return
            for part in parts:
                if len(part) == 0 or not 0 <= int(part) <= 255:
                    QtWidgets.QMessageBox.critical(self, 'IP', 'Недопустимый ip!')
                    return
            return params
            

        if self._online.isChecked():
            return check(self._inputs.itemAt(0).widget().text())

        for i in range(self._sel_layout.count() - 1):
            if self._sel_layout.itemAt(i).widget().isChecked():
                return self._sel_layout.itemAt(i).widget().text()


class Field(QtWidgets.QMainWindow):
    CELL_BRUSHES = {
        Cell.EMPTY: QtGui.QBrush(QtCore.Qt.white, QtCore.Qt.SolidPattern),
        Cell.RED: QtGui.QBrush(QtCore.Qt.red, QtCore.Qt.SolidPattern),
        Cell.BLUE: QtGui.QBrush(QtCore.Qt.blue, QtCore.Qt.SolidPattern),
        Cell.BLACK: QtGui.QBrush(QtCore.Qt.black, QtCore.Qt.SolidPattern)
    }

    def __init__(self, game, high_scores, rival):
        super().__init__()
        self.rival = rival
        self.high_scores = high_scores
        self.game = game
        self.width = game.width
        self.height = game.height
        self.x = 0
        self.y = 0
        self.pause = True
        self.exit = False
        self.winner = None
        self.name_win = None
        self.record_win = None
        self.results = False

        self.initUI()

    def initUI(self):
        self.resize(
            QtWidgets.QDesktopWidget().availableGeometry().height() - 200,
            QtWidgets.QDesktopWidget().availableGeometry().height() - 50)
        self.center()

        self.setWindowTitle('Points')

        menubar = self.menuBar()
        setting = menubar.addMenu('&Settings')
        
        get_setting = QtWidgets.QAction('Set settings', self)
        get_setting.triggered.connect(self.setting_game)
        setting.addAction(get_setting)


        if self.rival != (Rival.HUMAN, Rival.HUMAN) and Rival.HUMAN in self.rival:
            if self.high_scores is not None:
                records = menubar.addMenu('&Records')
                open_r = QtWidgets.QAction('Open records', self)
                open_r.triggered.connect(self.open_records)
                records.addAction(open_r)

            undo_and_redo = menubar.addMenu('&Undo/Redo')          
            
            undo = QtWidgets.QAction('Undo', self)
            undo.triggered.connect(self.undo)
            undo_and_redo.addAction(undo)

            redo = QtWidgets.QAction('Redo', self)
            redo.triggered.connect(self.redo)
            undo_and_redo.addAction(redo)

        self.show()
    
    def undo(self):
        if self.rival == (Rival.AIrandom, Rival.HUMAN) or self.rival == (Rival.HUMAN, Rival.AIrandom):    
            enemy = Rival.AIrandom
        elif self.rival == (Rival.AIeasy, Rival.HUMAN) or self.rival == (Rival.HUMAN, Rival.AIeasy):    
            enemy = Rival.AIeasy
        elif self.rival == (Rival.AInormal, Rival.HUMAN) or self.rival == (Rival.HUMAN, Rival.AInormal):   
            enemy = Rival.AInormal
        with contextlib.suppress(IndexError):
            self.game.undo(enemy)
            try:
                self.game.undo(enemy)
            except IndexError:
                self.game.redo(enemy)
            self.update()
    
    def redo(self):
        if self.rival == (Rival.AIrandom, Rival.HUMAN) or self.rival == (Rival.HUMAN, Rival.AIrandom):
            enemy = Rival.AIrandom
        elif self.rival == (Rival.AIeasy, Rival.HUMAN) or self.rival == (Rival.HUMAN, Rival.AIeasy):   
            enemy = Rival.AIeasy
        elif self.rival == (Rival.AInormal, Rival.HUMAN) or self.rival == (Rival.HUMAN, Rival.AInormal):    
            enemy = Rival.AInormal
        with contextlib.suppress(IndexError):
            self.game.redo(enemy)
            self.game.redo(enemy)
            self.update()

    def set_params_not_online(self):
        self.name_win = {}
        self.name_win["size"] = self.second_game_dialog.set_size()
        self.name_win["first"] = self.second_game_dialog.set_players()[0]
        self.name_win["second"] = self.second_game_dialog.set_players()[1]
    
    def set_params_online(self):
        self.name_win = {}
        size = self.second_game_dialog.set_size()
        self.name_win["size"] = size
        
        self.saving_for_online = {}
        self.saving_for_online["color"] = self.second_game_dialog.set_color()
        self.saving_for_online["ip"] = self.ip
        self.saving_for_online["size"] = size

    def set_onl(self):
        setting = self.new_game_dialog.set_online()
        if setting == "not online":
            self.second_game_dialog = StartGameWindowNotOnline(self) 
            self.second_game_dialog.setModal(True) 
            self.second_game_dialog.accepted.connect(self.set_params_not_online) 
            self.second_game_dialog.rejected.connect(self.second_game_dialog.close)
        elif setting is not None:
            self.second_game_dialog = StartGameWindowOnline(self)
            self.second_game_dialog.setModal(True) 
            self.second_game_dialog.accepted.connect(self.set_params_online) 
            self.second_game_dialog.rejected.connect(self.second_game_dialog.close)
            self.ip = setting
            
    def setting_game(self):
        self.new_game_dialog = OnlineOrNotWindow(self)
        self.new_game_dialog.setModal(True) 
        self.new_game_dialog.accepted.connect(self.set_onl) ####set_onl переименовать (типо онлайность)
        self.new_game_dialog.rejected.connect(self.new_game_dialog.close) 
    
    def open_records(self):
        if not self.record_win:
            scores = self.high_scores
            self.record_win = RecordsWin(scores)
        self.record_win.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(
            self, 'Message', "Are you sure to quit?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()         
            self.exit = True
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == QtCore.Qt.Key_Escape:
            self.results = True
            
    def mousePressEvent(self, event):
        if event.button() & QtCore.Qt.LeftButton:
            self.pause = False
            self.x = event.x()
            self.y = event.y()            
            self.update()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        try:
            self.draw_grid(qp)
            self.draw_points(qp)
            self.draw_lines(qp)
            self.draw_text(e, qp)
        finally:
            qp.end()

    def draw_points(self, qp):
        dist_x = self.size().width() / self.width
        dist_y = (self.size().height() - 150) / self.height
        for i in range(self.width):
            for j in range(self.height):
                qp.setBrush(Field.CELL_BRUSHES[self.game.field[i][j]])
                point = QtCore.QPoint(
                    dist_x * (i + 1/2), dist_y * (j + 1/2) + 25)
                qp.drawEllipse(point, 7, 7)

    def draw_grid(self, qp):
        pen = QtGui.QPen(QtCore.Qt.black, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
        dist_x = self.size().width() / self.width
        dist_y = (self.size().height() - 150) / self.height

        for i in range(self.width):
            qp.drawLine(dist_x * (i + 1/2), 25,
                        dist_x * (i + 1/2), dist_y * self.height + 25)
        for i in range(self.height):
            qp.drawLine(0, dist_y * (i + 1/2) + 25,
                        dist_x * self.width, dist_y * (i + 1/2) + 25)
        qp.drawLine(0, dist_y * self.height + 25,
                    dist_x * self.width, dist_y * self.height + 25)

    def draw_text(self, event, qp):
        if self.winner is not None:
            if self.winner == Cell.RED:
                text = "Red is winner"
            elif self.winner == Cell.BLUE:
                text = "Blue is winner"
            else:
                text = "It is draw"
            qp.setPen(QtGui.QColor(0, 0, 0))
            qp.setFont(QtGui.QFont('Decorative', min(
                self.size().width() / 10, (self.size().height() - 150) / 5)))
            qp.drawText(event.rect(), QtCore.Qt.AlignCenter, text)

        if self.game.turn == Cell.RED:
            turn = "Red"
            color = QtGui.QColor(255, 0, 0)
        else:
            turn = "Blue"
            color = QtGui.QColor(0, 0, 255)
        if Rival.AIeasy in self.rival or Rival.AIrandom in self.rival or Rival.AInormal in self.rival:
            if self.high_scores:
                name_and_score = '{} {}'.format(*self.high_scores[0])
            else:
                name_and_score = "No records"
            text = (f"Best score: {name_and_score}; \nRed score: "
                    f"{self.game.score_red}; \n"
                    f"Blue score: {self.game.score_blue}:\n")
            qp.setPen(QtGui.QColor(0, 0, 0))
        elif self.rival == (Rival.ONLINE, Rival.ONLINE):
            color_player = self.saving_for_online['color']
            if color_player == self.game.turn:
                player = 'Your'
            else:
                player = "Enemy's"
            text = (f"{player} step; \nRed score: "
                    f"{self.game.score_red}; \n"
                    f"Blue score: {self.game.score_blue};\n")
            qp.setPen(color)
        else:
            text = (f"{turn} step; \nRed score: "
                    f"{self.game.score_red}; \n"
                    f"Blue score: {self.game.score_blue};\n")
            qp.setPen(color)
        qp.setFont(QtGui.QFont('Decorative', 15))

        qp.drawText(event.rect(), QtCore.Qt.AlignBottom, text)

    def draw_lines(self, qp):
        dist_x = self.size().width() / self.width
        dist_y = (self.size().height() - 150) / self.height

        def draw_d_v(qp, point1, point2, coef1):
            qp.drawLine(point1, QtCore.QPoint(point1.x() + coef1*dist_x/2,
                        self.height * dist_y + 25))
            qp.drawLine(point2, QtCore.QPoint(point2.x() - coef1*dist_x/2, 25))

        def draw_d_h(qp, point1, point2, coef1):
            qp.drawLine(point1, QtCore.QPoint(0, point1.y() + coef1*dist_y/2))
            qp.drawLine(point2, QtCore.QPoint(self.width * dist_x,
                        point2.y() - coef1*dist_y/2))

        def draw_ver(qp, previos_x, previos_y, current_y):
            qp.drawLine(QtCore.QPoint(previos_x,
                                    max(previos_y, current_y)),
                                    QtCore.QPoint(previos_x,
                                    self.height * dist_y + 25))
            qp.drawLine(QtCore.QPoint(previos_x,
                        min(previos_y, current_y)),
                        QtCore.QPoint(previos_x, 25))

        def draw_horiz(qp, previos_x, previos_y, current_x):
            qp.drawLine(QtCore.QPoint(
                                    max(previos_x, current_x),
                                    previos_y),
                                    QtCore.QPoint(self.width * dist_x,
                                    previos_y))
            qp.drawLine(QtCore.QPoint(
                            min(previos_x, current_x),
                            previos_y),
                        QtCore.QPoint(0, previos_y))

        def set_qt_color(color):
            if color == Cell.RED:
                return QtCore.Qt.red
            return QtCore.Qt.blue

        def set_qp():
            qt_color = set_qt_color(color)
            pen = QtGui.QPen(qt_color, 4, QtCore.Qt.SolidLine)
            brush = QtGui.QBrush(qt_color, QtCore.Qt.SolidPattern)
            qp.setPen(pen)
            brush.setStyle(QtCore.Qt.DiagCrossPattern)
            qp.setBrush(brush)

        def add_elements_to_path(point1, point2):
            nonlocal path
            nonlocal was_jump_border
            nonlocal path_part
            path.lineTo(point1)
            if not was_jump_border:
                was_jump_border = True
                path_part = path
                path = QtGui.QPainterPath()
            path.moveTo(point2)
            
        for (jump_list, color, _black_points, _square) in self.game.lines:
            if (jump_list[0][0] == 0 or
                (jump_list[0][1] == self.height - 1 or jump_list[0][1] == 0) and
               (abs(jump_list[1][1] - jump_list[0][1]) <= 1)):
                jump_list = jump_list[::-1]
            path = QtGui.QPainterPath()
            path_part = QtGui.QPainterPath()
            was_jump_border = False
            previos = jump_list[0]            
            previos_point = QtCore.QPoint(
                dist_x * (1/2 + previos[0]), dist_y * (1/2 + previos[1]) + 25)
            path.moveTo(previos_point)
            set_qp()

            for (x, y) in jump_list[1:]:
                point = QtCore.QPoint(
                    dist_x * (1/2 + x), dist_y * (1/2 + y) + 25)
                if (abs(previos[0] - x) <= 1 and
                        abs(previos[1] - y) <= 1):
                    qp.drawLine(previos_point, point)
                else:
                    previos_x = previos_point.x()
                    previos_y = previos_point.y()
                    current_x = point.x()
                    current_y = point.y()
                    max_x = max(current_x, previos_x)
                    min_x = min(current_x, previos_x)
                    max_y = max(current_y, previos_y)
                    min_y = min(current_y, previos_y)
                    if previos[0] == x:
                        draw_ver(qp, previos_x, previos_y, current_y)
                        first = QtCore.QPoint(previos_x, self.height * dist_y + 25)
                        second = QtCore.QPoint(previos_x, 25)
                        if previos[1] > y:
                            add_elements_to_path(first, second)
                        else:
                            add_elements_to_path(second, first)
                    elif previos[1] == y:
                        draw_horiz(qp, previos_x, previos_y, current_x)
                        first = QtCore.QPoint(self.width * dist_x, previos_y)
                        second = QtCore.QPoint(0, previos_y)
                        if previos[0] > x:
                            add_elements_to_path(first, second)
                        else:
                            add_elements_to_path(second, first)                      
                    elif abs(previos[0] - x) == 1:
                        if (previos[0] - x) * (previos[1] - y) < 0:
                            draw_d_v(qp, QtCore.QPoint(min_x, max_y),
                                QtCore.QPoint(max_x, min_y), 1)                            
                            if previos[0] > x:
                                add_elements_to_path(QtCore.QPoint(previos_x - dist_x/2, 25), QtCore.QPoint(current_x + dist_x/2, self.height * dist_y + 25))
                            else:
                                add_elements_to_path(QtCore.QPoint(previos_x + dist_x/2, self.height * dist_y + 25), QtCore.QPoint(current_x - dist_x/2, 25))
                        else:
                            draw_d_v(qp, QtCore.QPoint(max_x, max_y),
                                QtCore.QPoint(min_x, min_y), -1)
                            if previos[0] > x:
                                add_elements_to_path(QtCore.QPoint(previos_x - dist_x/2, self.height * dist_y + 25), QtCore.QPoint(current_x + dist_x/2, 25))
                            else:
                                add_elements_to_path(QtCore.QPoint(previos_x + dist_x/2, 25), QtCore.QPoint(current_x - dist_x/2, self.height * dist_y + 25))
                    elif abs(previos[1] - y) == 1:
                        if (previos[0] - x) * (previos[1] - y) < 0:
                            draw_d_h(qp, QtCore.QPoint(min_x, max_y),
                                QtCore.QPoint(max_x, min_y), -1)
                            if previos[0] > x:
                                add_elements_to_path(QtCore.QPoint(self.width * dist_x, previos_y + dist_y/2), QtCore.QPoint(0, current_y - dist_y/2))
                            else:
                                add_elements_to_path(QtCore.QPoint(0, previos_y - dist_y/2), QtCore.QPoint(self.width * dist_x, current_y + dist_y/2))
                        else:
                            draw_d_h(qp, QtCore.QPoint(min_x, min_y),
                                QtCore.QPoint(max_x, max_y), 1)
                            if previos[0] > x:
                                add_elements_to_path(QtCore.QPoint(self.width * dist_x, previos_y - dist_y/2), QtCore.QPoint(0, current_y + dist_y/2))
                            else:
                                add_elements_to_path(QtCore.QPoint(0, previos_y + dist_y/2), QtCore.QPoint(self.width * dist_x, current_y - dist_y/2))

                path.lineTo(point)
                previos_point = point
                previos = (x, y)
            path.connectPath(path_part)
            qp.setPen(set_qt_color(color))
            qp.setRenderHint(QtGui.QPainter.Antialiasing)
            qp.drawPath(path)

    def get_coordinats(self):
        dist_x = self.size().width() / self.width
        dist_y = (self.size().height() - 150) / self.height
        x = round((self.x - dist_x/2) / dist_x)
        y = round((self.y - dist_y/2 - 25) / dist_y)
        return x, y


class RecordsWin(QtWidgets.QWidget):
    def __init__(self, records):
        super().__init__()
        self.records = RecordsWin.get_records(records)
        self.name = None

        self.initUI()

    @staticmethod
    def get_records(records):
        return '\n'.join(f'{name} {value}' for (name, value) in records)

    def initUI(self):
        self.resize(400, 300)
        self.center()
        self.setWindowTitle('Records')
        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.drawText(event, qp)
        qp.end()

    def drawText(self, event, qp):
        qp.setPen(QtGui.QColor(0, 128, 0))
        qp.setFont(QtGui.QFont('Decorative', 15))
        if self.records == "":
            self.records = "No records"
        qp.drawText(event.rect(), QtCore.Qt.AlignCenter, self.records)

    def showDialog(self):
        text, ok = QtWidgets.QInputDialog.getText(
            self, 'Input Dialog', 'Enter your name:')
        if ok:
            self.name = text
