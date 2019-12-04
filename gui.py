from PyQt5 import QtWidgets, QtCore, QtGui, QtTest
from logic import Game
from cell import Cell
import contextlib
from rivals import Rival
from players import AIrandom, AIeasy, AInormal, HUMAN, ONLINE, AI
import players

class StartGameWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.distance_between_points = 25
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

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self._selector)
        self.layout.addLayout(self._inputs)

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
                if (size[0] <= 5 or size[1] <= 5 or
                    size[0] * self.distance_between_points >
                        QtWidgets.QDesktopWidget()
                        .availableGeometry().height() - 200 or
                    size[1] * self.distance_between_points >
                        QtWidgets.QDesktopWidget()
                        .availableGeometry().height() - 200):
                    QtWidgets.QMessageBox.critical(
                        self, 'Size', 'Недопустимый размер поля!')
                else:
                    return params
            except (IndexError, ValueError):
                QtWidgets.QMessageBox.critical(self, 'Size', 'Wrong format!')

        if self._other.isChecked():
            return check(self._inputs.itemAt(0).widget().text())

        for i in range(self._sel_layout.count() - 1):
            if self._sel_layout.itemAt(i).widget().isChecked():
                return self._sel_layout.itemAt(i).widget().text()


class StartGameWindowNotOnline(StartGameWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

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

            self.layout.addWidget(self._selector_new)

        self._buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        self.layout.addWidget(self._buttons)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setLayout(self.layout)
        self.show()

    def set_players(self):
        players = []
        for layout in self._player_layouts:
            for i in range(layout.count()):
                if layout.itemAt(i).widget().isChecked():
                    players.append(
                        self.player_states[layout.itemAt(i).widget().text()])
        return players


class StartGameWindowOnline(StartGameWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
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

        self.layout.addWidget(self._selector_new)
        self._buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

        self.layout.addWidget(self._buttons)
        self.layout.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)

        self.setLayout(self.layout)
        self.show()

    def set_color(self):
        for i in range(self._sel_layout_new.count()):
            if self._sel_layout_new.itemAt(i).widget().isChecked():
                return self.color_states[
                    self._sel_layout_new.itemAt(i).widget().text()]


class OnlineOrNotWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Setting')
        self._sel_layout = QtWidgets.QVBoxLayout()

        items = ['not online', 'create server']

        for i in items:
            self._sel_layout.addWidget(QtWidgets.QRadioButton(i))

        self._online = QtWidgets.QRadioButton('connect to server')
        self._online.toggled.connect(self._click_online)
        self._sel_layout.addWidget(self._online)

        self._sel_layout.itemAt(0).widget().setChecked(True)

        self._selector = QtWidgets.QGroupBox()
        self._selector.setTitle('Online or not')
        self._selector.setLayout(self._sel_layout)

        self._inputs = QtWidgets.QHBoxLayout()
        inp = QtWidgets.QLineEdit()
        self._inputs.addWidget(inp)
        self._inputs.itemAt(0).widget().setPlaceholderText('192.168.xxx.xxx')
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
                QtWidgets.QMessageBox.critical(
                    self, 'IP', 'Недопустимый ip!')
                return
            for part in parts:
                if len(part) == 0 or not 0 <= int(part) <= 255:
                    QtWidgets.QMessageBox.critical(
                        self, 'IP', 'Недопустимый ip!')
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

        self.RIVALOBJECT = {
            Rival.HUMAN: HUMAN(),
            Rival.ONLINE: ONLINE(),
            Rival.AIeasy: AIeasy(),
            Rival.AInormal: AInormal(),
            Rival.AIrandom: AIrandom()
        }

        self.waiting = ""
        self.rival_obj = self.create_rival_obj()

        self.initUI()

    def create_rival_obj(self):
        temp = []
        for i in range(2):
            temp.append(self.RIVALOBJECT[self.rival[i]])
        return tuple(temp)

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

        if (self.rival != (Rival.HUMAN, Rival.HUMAN) and
                Rival.HUMAN in self.rival):
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
        sort_rival_obj = players.sort(*self.rival_obj)
        sort_rival = Rival.sort_tuple(*self.rival)
        if (isinstance(sort_rival_obj[0], AI)
                and type(sort_rival_obj[1]) is HUMAN):
            enemy = sort_rival[0]
            with contextlib.suppress(IndexError):
                self.game.undo(enemy)
                try:
                    self.game.undo(enemy)
                    self.x, self.y = -1, -1
                except IndexError:
                    self.game.redo(enemy)
                self.update()

    def redo(self):
        sort_rival_obj = players.sort(*self.rival_obj)
        sort_rival = Rival.sort_tuple(*self.rival)
        if (isinstance(sort_rival_obj[0], AI)
                and type(sort_rival_obj[1]) is HUMAN):
            enemy = sort_rival[0]
        with contextlib.suppress(IndexError):
            self.game.redo(enemy)
            self.game.redo(enemy)
            self.update()

    def set_params_not_online(self):
        self.name_win = {
            "size": self.second_game_dialog.set_size(),
            "first": self.second_game_dialog.set_players()[0],
            "second": self.second_game_dialog.set_players()[1]}

    def set_params_create_server(self):
        size = self.second_game_dialog.set_size()
        self.name_win = {"size": size}
        self.saving_for_online = {
            "color": self.second_game_dialog.set_color(),
            "ip": self.ip,
            "size": size}

    def set_params_set_params_connect_to_server(self):
        self.saving_for_online = {"ip": self.ip,
                                  "color": Cell.RED,
                                  "size": "15x15"
                                  }
        self.name_win = {"size": "15x15"}

    def set_online_or_not_online(self):
        setting = self.new_game_dialog.set_online()
        if setting == "not online":
            self.second_game_dialog = StartGameWindowNotOnline(self)
            self.second_game_dialog.setModal(True)
            self.second_game_dialog.accepted.connect(
                self.set_params_not_online)
            self.second_game_dialog.rejected.connect(
                self.second_game_dialog.close)
        elif setting == "create server":
            self.second_game_dialog = StartGameWindowOnline(self)
            self.second_game_dialog.setModal(True)
            self.second_game_dialog.accepted.connect(
                self.set_params_create_server)
            self.second_game_dialog.rejected.connect(
                self.second_game_dialog.close)
            self.ip = ""
        elif setting is not None:
            self.ip = setting
            self.set_params_set_params_connect_to_server()

    def setting_game(self):
        self.new_game_dialog = OnlineOrNotWindow(self)
        self.new_game_dialog.setModal(True)
        self.new_game_dialog.accepted.connect(self.set_online_or_not_online)
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
        self.exit = True

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
                if (i, j) in [self.game.last_blue, self.game.last_red]:
                    qp.setPen(QtGui.QPen(QtCore.Qt.black, 4,
                                         QtCore.Qt.SolidLine))
                else:
                    qp.setPen(QtGui.QPen(QtCore.Qt.black, 2,
                                         QtCore.Qt.SolidLine))
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

        if ((isinstance(self.rival_obj[0], AI) or isinstance(self.rival_obj[1], AI)) and
                Rival.HUMAN in self.rival):
            if self.high_scores:
                name_and_score = '{} {}'.format(*self.high_scores[0])
            else:
                name_and_score = "No records"
            text = (f"{self.waiting}Best score: {name_and_score}; \n"
                    f"Red score: {self.game.score_red}; \n"
                    f"Blue score: {self.game.score_blue}:\n")
            qp.setPen(QtGui.QColor(0, 0, 0))
        elif self.rival == (Rival.ONLINE, Rival.ONLINE):
            color_player = self.saving_for_online['color']
            if color_player == self.game.turn:
                player = 'Your'
            else:
                player = "Enemy's"
            text = (f"{self.waiting}{player} step; \nRed score: "
                    f"{self.game.score_red}; \n"
                    f"Blue score: {self.game.score_blue};\n")
            qp.setPen(color)
        elif self.rival == (Rival.HUMAN, Rival.HUMAN):
            text = (f"{self.waiting}{turn} step; \nRed score: "
                    f"{self.game.score_red}; \n"
                    f"Blue score: {self.game.score_blue};\n")
            qp.setPen(color)
        else:
            text = (f"{self.waiting}Red score: "
                    f"{self.game.score_red}; \n"
                    f"Blue score: {self.game.score_blue};\n")
            qp.setPen(QtGui.QColor(0, 0, 0))
        qp.setFont(QtGui.QFont('Decorative', 15))

        qp.drawText(event.rect(), QtCore.Qt.AlignBottom, text)

    @staticmethod
    def draw_d_v(qp, point1, point2, coef1, dist_x, dist_y, height):
        qp.drawLine(point1, QtCore.QPoint(point1.x() + coef1*dist_x/2,
                    height * dist_y + 25))
        qp.drawLine(point2, QtCore.QPoint(point2.x() - coef1*dist_x/2, 25))
    
    @staticmethod
    def draw_d_h(qp, point1, point2, coef1, dist_x, dist_y, width):
        qp.drawLine(point1, QtCore.QPoint(0, point1.y() + coef1*dist_y/2))
        qp.drawLine(point2, QtCore.QPoint(width * dist_x,
                    point2.y() - coef1*dist_y/2))

    @staticmethod
    def draw_ver(qp, previos_x, previos_y, current_y, dist_y, height):
        qp.drawLine(QtCore.QPoint(previos_x,
                                    max(previos_y, current_y)),
                    QtCore.QPoint(previos_x,
                                    height * dist_y + 25))
        qp.drawLine(QtCore.QPoint(previos_x,
                    min(previos_y, current_y)),
                    QtCore.QPoint(previos_x, 25))
    
    @staticmethod
    def draw_horiz(qp, previos_x, previos_y, current_x, dist_x, width):
        qp.drawLine(QtCore.QPoint(
                                max(previos_x, current_x),
                                previos_y),
                    QtCore.QPoint(width * dist_x,
                                    previos_y))
        qp.drawLine(QtCore.QPoint(
                        min(previos_x, current_x),
                        previos_y),
                    QtCore.QPoint(0, previos_y))

    @staticmethod
    def draw_diagonal_right(qp, previos_x, previos_y,
                            current_x, current_y, dist_x, dist_y, height, width):
        qp.drawLine(QtCore.QPoint(min(previos_x, current_x),
                                    min(previos_y, current_y)),
                    QtCore.QPoint(0, 25))
        qp.drawLine(QtCore.QPoint(max(previos_x, current_x),
                                    max(previos_y, current_y)),
                    QtCore.QPoint(width * dist_x,
                                    height * dist_y + 25))

    @staticmethod
    def draw_diagonal_left(qp, previos_x, previos_y, current_x, current_y, dist_x, dist_y, height, width):
        qp.drawLine(QtCore.QPoint(min(previos_x, current_x),
                                    max(previos_y, current_y)),
                    QtCore.QPoint(0, height * dist_y + 25))
        qp.drawLine(QtCore.QPoint(max(previos_x, current_x),
                                    min(previos_y, current_y)),
                    QtCore.QPoint(width * dist_x, 25))
    
    @staticmethod
    def set_qt_color(color):
        if color == Cell.RED:
            return QtCore.Qt.red
        return QtCore.Qt.blue

    @staticmethod
    def set_qp(qp, color):
        qt_color = Field.set_qt_color(color)
        pen = QtGui.QPen(qt_color, 4, QtCore.Qt.SolidLine)
        brush = QtGui.QBrush(qt_color, QtCore.Qt.SolidPattern)
        qp.setPen(pen)
        brush.setStyle(QtCore.Qt.DiagCrossPattern)
        qp.setBrush(brush)

    @staticmethod
    def add_elements_for_drawing_path(list_lines, point1, point2, i, width, height, x, y):
        flag = False
        list_lines[i].append(point1)
        for index in range(len(list_lines)):
            last_element = list_lines[index][-1]
            if ((abs(last_element[0] + 1 - x) <= width / 2 and
                (abs(last_element[1] + 1 - y) <= height / 2 or
                    abs(last_element[1] - y) <= height / 2 or
                    abs(last_element[1] - 1 - y) <= height / 2)) or
                (abs(last_element[0] - x) <= width / 2 and
                    (abs(last_element[1] + 1 - y) <= height / 2 or
                    abs(last_element[1] - 1 - y) <= height / 2)) or
                (abs(last_element[0] - 1 - x) <= width / 2 and
                    (abs(last_element[1] + 1 - y) <= height / 2 or
                    abs(last_element[1] - y) <= height / 2 or
                    abs(last_element[1] - 1 - y) <= height / 2))):
                flag = True
                i = index
                break
        if not flag:
            list_lines.append([])
            i = len(list_lines) - 1
        list_lines[i].append(point2)
        return i

    @staticmethod
    def draw_path(qp, list_line, dist_x, dist_y, height, width):
            path = QtGui.QPainterPath()
            list_line.append(list_line[0])
            path.moveTo(QtCore.QPoint(
                dist_x * (1/2 + list_line[0][0]),
                dist_y * (1/2 + list_line[0][1]) + 25))
            for i in range(len(list_line[1:])):
                if (list_line[i][0] == -0.5 and
                        list_line[i + 1][1] == -0.5 or
                        list_line[i][1] == -0.5 and
                        list_line[i + 1][0] == -0.5):
                    path.lineTo(QtCore.QPoint(0, 0))
                elif (list_line[i][0] == -0.5 and
                        list_line[i + 1][1] == height - 0.5 or
                        list_line[i][1] == height - 0.5 and
                        list_line[i + 1][0] == -0.5):
                    path.lineTo(QtCore.QPoint(
                        0, dist_y * height + 25))
                elif (list_line[i][0] == width - 0.5 and
                        list_line[i + 1][1] == -0.5 or
                        list_line[i][1] == - 0.5 and
                        list_line[i + 1][0] == width - 0.5):
                    path.lineTo(QtCore.QPoint(dist_x * width, 0))
                elif (list_line[i][0] == width - 0.5 and
                        list_line[i + 1][1] == height - 0.5 or
                        list_line[i][1] == height - 0.5 and
                        list_line[i + 1][0] == width - 0.5):
                    path.lineTo(QtCore.QPoint(
                        dist_x * width, dist_y * height + 25))
                path.lineTo(QtCore.QPoint(
                    dist_x * (1/2 + list_line[i + 1][0]),
                    dist_y * (1/2 + list_line[i + 1][1]) + 25))
            qp.drawPath(path)

    @staticmethod
    def draw_borders(qp, x, y, list_lines, height, width, previos_point, point, previos, dist_y, dist_x, i):
        previos_x = previos_point.x()
        previos_y = previos_point.y()
        current_x = point.x()
        current_y = point.y()
        max_x = max(current_x, previos_x)
        min_x = min(current_x, previos_x)
        max_y = max(current_y, previos_y)
        min_y = min(current_y, previos_y)

        if previos[0] == x:
            Field.draw_ver(qp, previos_x, previos_y, current_y, dist_y, height)
            if previos[1] > y:
                i = Field.add_elements_for_drawing_path(
                    list_lines,
                    (previos[0], height - 1 + 0.5),
                    (previos[0], -0.5), i, width, height, x, y)
            else:
                i = Field.add_elements_for_drawing_path(
                    list_lines,
                    (previos[0], -0.5),
                    (previos[0], height - 1 + 0.5), i, width, height, x, y)
        elif previos[1] == y:
            Field.draw_horiz(qp, previos_x, previos_y, current_x, dist_x, width)
            if previos[0] > x:
                i = Field.add_elements_for_drawing_path(
                    list_lines,
                    (width - 1 + 0.5, previos[1]),
                    (- 0.5, previos[1]), i, width, height, x, y)
            else:
                i = Field.add_elements_for_drawing_path(
                    list_lines, (- 0.5, previos[1]),
                    (width - 1 + 0.5, previos[1]), i, width, height, x, y)
        elif abs(previos[0] - x) == 1:
            if (previos[0] - x) * (previos[1] - y) < 0:
                Field.draw_d_v(qp, QtCore.QPoint(min_x, max_y),
                            QtCore.QPoint(max_x, min_y), 1, dist_x, dist_y, height)
                if previos[0] > x:
                    i = Field.add_elements_for_drawing_path(
                        list_lines, (previos[0] - 0.5, -0.5),
                        (x + 0.5, height - 1 + 0.5), i, width, height, x, y)
                else:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (previos[0] + 0.5, height - 1 + 0.5),
                        (x - 0.5, -0.5), i, width, height, x, y)
            else:
                Field.draw_d_v(qp, QtCore.QPoint(max_x, max_y),
                            QtCore.QPoint(min_x, min_y), -1, dist_x, dist_y, height)
                if previos[0] > x:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (previos[0] - 0.5, height - 1 + 0.5),
                        (x + 0.5, -0.5), i, width, height, x, y)
                else:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (previos[0] + 0.5, -0.5),
                        (x - 0.5, height - 1 + 0.5), i, width, height, x, y)
        elif abs(previos[1] - y) == 1:
            if (previos[0] - x) * (previos[1] - y) < 0:
                Field.draw_d_h(qp, QtCore.QPoint(min_x, max_y),
                            QtCore.QPoint(max_x, min_y), -1, dist_x, dist_y, width)
                if previos[0] > x:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (width - 1 + 0.5, previos[1] + 0.5),
                        (- 0.5, y - 0.5), i, width, height, x, y)
                else:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (-0.5, previos[1] - 0.5),
                        (width - 1 + 0.5, y + 0.5), i, width, height, x, y)
            else:
                Field.draw_d_h(qp, QtCore.QPoint(min_x, min_y),
                            QtCore.QPoint(max_x, max_y), 1, dist_x, dist_y, width)
                if previos[0] > x:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (width - 1 + 0.5, previos[1] - 0.5),
                        (-0.5, y + 0.5), i, width, height, x, y)
                else:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (-0.5, previos[1] + 0.5),
                        (width - 1 + 0.5, y - 0.5), i, width, height, x, y)
        else:
            if (previos[0] - x) * (previos[1] - y) > 0:
                Field.draw_diagonal_right(
                    qp, previos_x, previos_y, current_x, current_y,
                    dist_x, dist_y, height, width)
                if (previos[0] - x) < 0:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (-0.5, -0.5),
                        (width - 1 + 0.5,
                            height - 1 + 0.5), i, width, height, x, y)
                else:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (width - 1 + 0.5,
                            height - 1 + 0.5),
                        (-0.5, -0.5), i, width, height, x, y)
            else:
                Field.draw_diagonal_left(
                    qp, previos_x, previos_y, current_x, current_y,
                    dist_x, dist_y, height, width)
                if (previos[0] - x) < 0:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (-0.5, height - 1 + 0.5),
                        (width - 1 + 0.5, - 0.5), i, width, height, x, y)
                else:
                    i = Field.add_elements_for_drawing_path(
                        list_lines,
                        (width - 1 + 0.5, - 0.5),
                        (-0.5, height - 1 + 0.5), i, width, height, x, y)
        return i

    def draw_lines(self, qp):
        dist_x = self.size().width() / self.width
        dist_y = (self.size().height() - 150) / self.height

        for (jump_list, color, _black_points, _square) in self.game.lines:
            if (jump_list[0][0] == 0 or
                (jump_list[0][1] == self.height - 1
                 or jump_list[0][1] == 0) and
               (abs(jump_list[1][1] - jump_list[0][1]) <= 1)):
                jump_list = jump_list[::-1]
            previos = jump_list[0]
            previos_point = QtCore.QPoint(
                dist_x * (1/2 + previos[0]), dist_y * (1/2 + previos[1]) + 25)
            Field.set_qp(qp, color)

            list_lines = []
            list_lines.append([])
            list_lines[0].append(previos)
            i = 0
            for (x, y) in jump_list[1:]:
                point = QtCore.QPoint(
                    dist_x * (1/2 + x), dist_y * (1/2 + y) + 25)
                if (abs(previos[0] - x) <= 1 and
                        abs(previos[1] - y) <= 1):
                    qp.drawLine(previos_point, point)
                    list_lines[i].append((x, y))
                else:
                    i = Field.draw_borders(qp, x, y, list_lines, self.height, self.width, previos_point, point, previos, dist_y, dist_x, i)
                    list_lines[i].append((x, y))

                previos_point = point
                previos = (x, y)
            if len(list_lines) > 1 and list_lines[0][0] == list_lines[-1][-1]:
                list_lines[0] += list_lines[-1]
                del list_lines[-1]
            qp.setPen(Field.set_qt_color(color))
            qp.setRenderHint(QtGui.QPainter.Antialiasing)

            for list_line in list_lines:
                Field.draw_path(qp, list_line, dist_x, dist_y, self.height, self.width)

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
