import sys
import os
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QPushButton, QGridLayout, QVBoxLayout, QRadioButton,
                             QButtonGroup, QMessageBox, QHBoxLayout, QDialog, QSizePolicy, QGroupBox, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap
import time
import sqlite3
from datetime import datetime

class Lobby(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("крестики-нолики")
        self.resize(400, 500)

        self.layout = QVBoxLayout()
        self.title_label = QLabel("КРЕСТИКИ-НОЛИКИ", alignment=Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(QFont("Arial", 12))
        self.layout.addWidget(self.title_label)

        self.image_label = QLabel()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = 'cat.png'
        print(image_path)
        if os.path.exists(image_path):
            self.pixmap = QPixmap(image_path)
            self.image_label.setPixmap(self.pixmap)
        else:
            print("Изображение не найдено:", image_path)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.image_label)

        self.layout.addWidget(QLabel("ВЫБЕРИТЕ РЕЖИМ ИГРЫ", alignment=Qt.AlignmentFlag.AlignCenter))

        self.button_two_players = QPushButton("игра вдвоём")
        self.button_two_players.setFont(QFont("Arial", 14))
        self.button_two_players.clicked.connect(self.start_two_player_game)
        self.layout.addWidget(self.button_two_players)
        self.button_two_players.clicked.connect(self.start_two_player_game)
        button_layout1 = QHBoxLayout()
        self.layout.addLayout(button_layout1)

        self.button_vs_computer = QPushButton("игра с компьютером")
        self.button_vs_computer.setFont(QFont("Arial", 14))
        self.button_vs_computer.clicked.connect(self.start_vs_computer_game)
        self.layout.addWidget(self.button_vs_computer)
        button_layout2 = QHBoxLayout()
        self.layout.addLayout(button_layout2)
        
        self.setLayout(self.layout)
        self.resize_timer = QTimer()
        self.resize_timer.timeout.connect(self.resize_event_handler)
        self.resize_timer.start(50)
        
        self.button_statistics = QPushButton("статистика игр")
        self.button_statistics.setFont(QFont("Arial", 14))
        self.button_statistics.clicked.connect(self.show_statistics)
        self.layout.addWidget(self.button_statistics)
        button_layout3 = QHBoxLayout()
        self.layout.addLayout(button_layout3)


    def show_statistics(self):
        self.statistics = StatisticsWindow()
        self.statistics.show()
        self.close()

    def start_two_player_game(self):
        self.two_player_choice = TwoPlayerGameChoice()
        self.two_player_choice.show()
        self.close()

    def start_vs_computer_game(self):
        self.vs_computer_game = GameChoice()
        self.vs_computer_game.show()
        self.close()

    def resize_event_handler(self):
        font_size = min(self.width() // 25, 30)
        self.title_label.setFont(QFont("Arial", font_size))

        font_size = min(self.height() // 40, 24)
        self.layout.itemAt(2).widget().setFont(QFont("Arial", font_size))

        font_size = min(self.height() // 30, 24)
        self.button_two_players.setFont(QFont("Arial", font_size))
        self.button_vs_computer.setFont(QFont("Arial", font_size))
        self.button_statistics.setFont(QFont("Arial", font_size))

        if hasattr(self, 'pixmap'):
            scaled_width = int(self.width() * 0.65)
            scaled_height = int(self.height() * 0.4)
            scaled_pixmap = self.pixmap.scaled(scaled_width, scaled_height, 
                                Qt.AspectRatioMode.KeepAspectRatio, 
                                Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

class TwoPlayerGameChoice(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выбор режима игры вдвоем")
        self.layout = QVBoxLayout()

        self.return_to_menu_button = QPushButton("Вернуться в меню")
        self.button_3x3 = QPushButton("Игра 3x3")
        self.button_5x5 = QPushButton("Игра 5x5")
        self.button_rules = QPushButton("Правила игры")

        for button in [self.return_to_menu_button, self.button_3x3, self.button_5x5, self.button_rules]:
            button.setFont(QFont("Arial", 14))
            self.layout.addWidget(button)

        self.setLayout(self.layout)
        self.return_to_menu_button.clicked.connect(self.return_to_lobby)
        self.button_3x3.clicked.connect(self.start_3x3_game)
        self.button_5x5.clicked.connect(self.start_5x5_game)
        self.button_rules.clicked.connect(self.show_rules)
        self.setFixedSize(400, 400)

    def return_to_lobby(self):
        self.lobby = Lobby()
        self.lobby.show()
        self.close()

    def start_3x3_game(self):
        self.game = TwoPlayerGame(3)
        self.game.show()
        self.close()

    def start_5x5_game(self):
        self.game = TwoPlayerGame(5)
        self.game.show()
        self.close()

    def show_rules(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        rules_path = 'rules.txt'
        try:
            with open(rules_path, 'r', encoding='utf-8') as file:
                rules_text = file.read()
            QMessageBox.information(self, "Правила игры", rules_text)
        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", "Файл с правилами не найден")


class TwoPlayerGame(QWidget):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.start_time = None
        self.db = DatabaseHelper()
        self.setWindowTitle(f"Игра вдвоем {size}x{size}")
        self.current_player = 'X'
        self.setup_ui()
        self.setMinimumSize(300, 400)

    def setup_ui(self):
        self.start_time = datetime.now()
        self.layout = QVBoxLayout()
        self.top_buttons_layout = QHBoxLayout()
        self.new_game_button = QPushButton("Новая игра")
        self.new_game_button.clicked.connect(self.start_new_game)
        self.return_to_menu_button = QPushButton("Вернуться в меню")
        self.return_to_menu_button.clicked.connect(self.return_to_menu)
        self.top_buttons_layout.addWidget(self.new_game_button)
        self.top_buttons_layout.addWidget(self.return_to_menu_button)
        self.layout.addLayout(self.top_buttons_layout)

        self.grid_layout = QGridLayout()
        self.buttons = []

        for i in range(self.size):
            for j in range(self.size):
                button = QPushButton()
                button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
                button.clicked.connect(self.process_click)
                self.grid_layout.addWidget(button, i, j)
                self.buttons.append(button)

        self.layout.addLayout(self.grid_layout)

        self.status_label = QLabel("Ход игрока X")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont("Arial", 8))
        self.layout.addWidget(self.status_label)

        radio_container = QWidget()
        self.player_layout = QHBoxLayout(radio_container)
        self.player_x_radio = QRadioButton("Игрок X")
        self.player_o_radio = QRadioButton("Игрок O")
        self.player_x_radio.setChecked(True)
        self.player_layout.addStretch()
        self.player_layout.addWidget(self.player_x_radio)
        self.player_layout.addWidget(self.player_o_radio)
        self.player_layout.addSpacing(20)
        self.player_layout.addStretch()

        radio_container.setLayout(self.player_layout)
        self.layout.addWidget(radio_container, alignment=Qt.AlignCenter)
        
        self.setLayout(self.layout)

    def process_click(self):
        button = self.sender()
        if button.text() == "":
            button.setText(self.current_player)
            if self.check_winner(self.current_player):
                self.finish(self.current_player)
            elif self.is_draw():
                self.finish(None)
            else:
                self.switch_player()

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.status_label.setText(f"Ход игрока {self.current_player}")
        if self.current_player == 'X':
            self.player_x_radio.setChecked(True)
        else:
            self.player_o_radio.setChecked(True)

    def check_winner(self, player):
        for i in range(self.size):
            if all(self.buttons[i * self.size + j].text() == player for j in range(self.size)) or \
                    all(self.buttons[i + j * self.size].text() == player for j in range(self.size)):
                return True

        if all(self.buttons[i * (self.size + 1)].text() == player for i in range(self.size)) or \
                all(self.buttons[(i + 1) * (self.size - 1)].text() == player for i in range(self.size)):
            return True

        return False

    def is_draw(self):
        return all(button.text() != "" for button in self.buttons)
    
    def get_winning_line(self, player):
        for i in range(self.size):
            row = [i*self.size + j for j in range(self.size)]
            if all(self.buttons[pos].text() == player for pos in row):
                return row
        
        for i in range(self.size):
            col = [i + j*self.size for j in range(self.size)]
            if all(self.buttons[pos].text() == player for pos in col):
                return col
        
        diag1 = [i*(self.size+1) for i in range(self.size)]
        if all(self.buttons[pos].text() == player for pos in diag1):
            return diag1
        
        diag2 = [(i+1)*(self.size-1) for i in range(self.size)]
        if all(self.buttons[pos].text() == player for pos in diag2):
            return diag2
        
        return []

    def finish(self, winner=None):
        game_time = datetime.now() - self.start_time
        minutes = game_time.seconds // 60
        seconds = game_time.seconds % 60
        time_str = f"{minutes}:{seconds:02d}"
        
        if winner:
            self.db.add_two_player_game(f"Игрок {winner}", time_str, self.size)
        else:
            self.db.add_two_player_game("Ничья", time_str, self.size)

        for button in self.buttons:
            button.setEnabled(False)
        
        if winner:
            win_line = self.get_winning_line(winner)
            for pos in win_line:
                button = self.buttons[pos]
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #90EE90;
                        color: #006400;
                        font-weight: bold;
                        border: 2px solid #006400;
                    }
                """)
            message = f"Игрок {winner} победил!"
        else:
            message = "Ничья!"
            for button in self.buttons:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFD700;
                        color: #8B4513;
                        font-weight: bold;
                        border: 2px solid #8B4513;
                    }
                """)
    
        QMessageBox.information(self, "Игра окончена", message)


    def start_new_game(self):
        self.current_player = 'X'
        self.status_label.setText("Ход игрока X")
        self.player_x_radio.setChecked(True)
        self.start_time = datetime.now()
        
        for button in self.buttons:
            button.setText("")
            button.setEnabled(True)
            button.setStyleSheet("")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.adjust_button_sizes()

    def adjust_button_sizes(self):
        available_width = self.width() - self.layout.contentsMargins().left() - self.layout.contentsMargins().right()
        available_height = self.height() - self.top_buttons_layout.sizeHint().height() - self.status_label.sizeHint().height() - self.player_layout.sizeHint().height() - self.layout.contentsMargins().top() - self.layout.contentsMargins().bottom()
        button_size = min(available_width // self.size, available_height // self.size)

        for button in self.buttons:
            button.setFixedSize(button_size, button_size)

        margin = (available_width - button_size * self.size) // 2
        self.grid_layout.setContentsMargins(margin, 0, margin, 0)

    def resizeEvent(self, event):
        super().resizeEvent(event)

        button_size = min(self.width() // self.size, self.height() // (self.size + 2))

        for button in self.buttons:
            button.setFixedSize(button_size, button_size)
            font = button.font()
            font.setPointSize(button_size // 3)
            button.setFont(font)

        self.grid_layout.invalidate()
        self.grid_layout.update()

        font_size = min(self.height() // 40, 20)
        self.status_label.setFont(QFont("Arial", font_size))

    def return_to_lobby(self):
        self.close()
        self.lobby = TwoPlayerGameChoice()
        self.lobby.show()

    def return_to_menu(self):
        self.close()
        self.game_choice = GameChoice()
        self.game_choice.show()


class GameChoice(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выбор режима игры")
        self.layout = QVBoxLayout()

        self.button_menu = QPushButton("Вернуться в меню")
        self.button_3x3 = QPushButton("Игра 3x3")
        self.button_5x5 = QPushButton("Игра 5x5")
        self.button_rules = QPushButton("Правила игры")

        for button in [self.button_menu, self.button_3x3, self.button_5x5, self.button_rules]:
            button.setFont(QFont("Arial", 14))
            self.layout.addWidget(button)

        self.setLayout(self.layout)

        self.button_menu.clicked.connect(self.return_to_lobby)
        self.button_3x3.clicked.connect(lambda: self.start_game(3))
        self.button_5x5.clicked.connect(lambda: self.start_game(5))
        self.button_rules.clicked.connect(self.show_rules)

        self.setFixedSize(300, 400)

    def start_game(self, size):
        self.game = ComputerGame(size)
        self.game.show()
        self.close()

    def show_rules(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        rules_path = 'rules1.txt'
        try:
            with open(rules_path, 'r', encoding='utf-8') as file:
                rules_text = file.read()
            QMessageBox.information(self, "Правила игры", rules_text)
        except FileNotFoundError:
            QMessageBox.warning(self, "Ошибка", "Файл с правилами не найден")

    def return_to_lobby(self):
        self.lobby = Lobby()
        self.lobby.show()
        self.close()


class ComputerGame(QWidget):
    def __init__(self, size):
        super().__init__()
        self.size = size
        self.start_time = None
        self.db = DatabaseHelper()
        self.setWindowTitle(f"Крестики-нолики: Игра с компьютером {size}x{size}")
        self.difficulty = "easy"
        self.reset_game()
        self.buttons = []
        self.layoutB = QGridLayout()
        self.layoutB.setSpacing(0)
        self.create_game_field()

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.button)
        self.layout.addWidget(self.difficulty_button)
        self.layout.addWidget(self.return_to_menu_button)

        self.layout.addLayout(self.layoutB)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.resize(300, 400)

        self.return_to_menu_button.clicked.connect(self.return_to_menu)
        self.difficulty_button.clicked.connect(self.show_difficulty_dialog)

    def reset_game(self):
        self.button = QPushButton("Начать новую игру")
        self.button.clicked.connect(self.start_game)
        self.difficulty_button = QPushButton("Выбрать уровень сложности")
        self.label = QLabel("Начинайте игру")
        self.label.setFont(QFont("Arial", 8))
        self.label.setAlignment(Qt.AlignCenter)
        self.return_to_menu_button = QPushButton("Вернуться в меню")
        self.playerXSymbol = "X"
        self.player0Symbol = "0"

    def create_game_field(self):
        self.start_time = datetime.now()
        self.buttons = []
        for i in range(self.size * self.size):
            button = QPushButton()
            self.buttons.append(button)
            button.setObjectName(str(i))
            button.clicked.connect(self.process_click)
            button.setFixedSize(100, 100)
            button.setFont(QFont("Arial", 18))
            self.layoutB.addWidget(button, i // self.size, i % self.size)

    def start_game(self):
        for i in range(self.size * self.size):
            self.buttons[i].setEnabled(True)
            self.buttons[i].setText("")
        self.label.setText("Ваш ход")
        
        self.start_time = datetime.now()
        for button in self.buttons:
            button.setText("")
            button.setEnabled(True)
            button.setStyleSheet("")

    def process_click(self):
        button = self.sender()
        button.setStyleSheet("color: black;")
        button.setText(self.playerXSymbol)
        button.setEnabled(False)

        winner = self.check_winner()
        if winner:
            self.finish(winner)
        elif not self.check_enabled():
            self.finish()
        else:
            self.computer_turn()

    def computer_turn(self):
        available_buttons = [i for i, button in enumerate(self.buttons) if button.isEnabled()]
        if available_buttons:
            if self.difficulty == "easy":
                computer_choice = self.easy_ai(available_buttons)
            elif self.difficulty == "medium":
                computer_choice = self.medium_ai(available_buttons)
            else:
                computer_choice = self.hard_ai(available_buttons)

            self.buttons[computer_choice].setText(self.player0Symbol)
            self.buttons[computer_choice].setStyleSheet("color: black;")
            self.buttons[computer_choice].setEnabled(False)

            winner = self.check_winner()
            if winner:
                self.finish(winner)
            elif not self.check_enabled():
                self.finish()
            else:
                self.label.setText("Ваш ход")

    def easy_ai(self, available_buttons):
        index = int(time.time() * 1000) % len(available_buttons)
        return available_buttons[index]

    def medium_ai(self, available_buttons):
        for i in available_buttons:
            self.buttons[i].setText(self.player0Symbol)
            if self.check_winner() == self.player0Symbol:
                self.buttons[i].setText("")
                return i
            self.buttons[i].setText("")

        for i in available_buttons:
            self.buttons[i].setText(self.playerXSymbol)
            if self.check_winner() == self.playerXSymbol:
                self.buttons[i].setText("")
                return i
            self.buttons[i].setText("")

        return self.easy_ai(available_buttons)

    def hard_ai(self, available_buttons):
        for i in available_buttons:
            self.buttons[i].setText(self.player0Symbol)
            if self.check_winner() == self.player0Symbol:
                self.buttons[i].setText("")
                return i
            self.buttons[i].setText("")

        for i in available_buttons:
            self.buttons[i].setText(self.playerXSymbol)
            if self.check_winner() == self.playerXSymbol:
                self.buttons[i].setText("")
                return i
            self.buttons[i].setText("")

        if self.size == 3:
            priority_moves = [0, 2, 4, 6, 8]
        else:
            priority_moves = [0, 4, 12, 20, 24]
            priority_moves += [6, 8, 16, 18]

        available_priority = [move for move in priority_moves if move in available_buttons]
        if available_priority:
            return self.easy_ai(available_priority)

        return self.easy_ai(available_buttons)

    def check_winner(self):
        win_positions = self.get_win_positions()
        for pos in win_positions:
            if all(self.buttons[p].text() == self.player0Symbol for p in pos):
                return self.player0Symbol
            elif all(self.buttons[p].text() == self.playerXSymbol for p in pos):
                return self.playerXSymbol
        return None

    def get_win_positions(self):
        if self.size == 3:
            return ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8), (0, 4, 8), (2, 4, 6))
        else:
            return (
                (0, 1, 2, 3, 4), (5, 6, 7, 8, 9), (10, 11, 12, 13, 14), (15, 16, 17, 18, 19), (20, 21, 22, 23, 24),
                (0, 5, 10, 15, 20), (1, 6, 11, 16, 21), (2, 7, 12, 17, 22), (3, 8, 13, 18, 23), (4, 9, 14, 19, 24),
                (0, 6, 12, 18, 24), (4, 8, 12, 16, 20)
            )

    def check_enabled(self):
        return any(button.isEnabled() for button in self.buttons)

    def get_winning_line(self, player):
        for i in range(self.size):
            row = [i*self.size + j for j in range(self.size)]
            if all(self.buttons[pos].text() == player for pos in row):
                return row
        
        for i in range(self.size):
            col = [i + j*self.size for j in range(self.size)]
            if all(self.buttons[pos].text() == player for pos in col):
                return col
        
        diag1 = [i*(self.size+1) for i in range(self.size)]
        if all(self.buttons[pos].text() == player for pos in diag1):
            return diag1
        
        diag2 = [(i+1)*(self.size-1) for i in range(self.size)]
        if all(self.buttons[pos].text() == player for pos in diag2):
            return diag2
        
        return []
    
    def finish(self, winner=None):
        game_time = datetime.now() - self.start_time
        minutes = game_time.seconds // 60
        seconds = game_time.seconds % 60
        time_str = f"{minutes}:{seconds:02d}"
        
        if winner == self.playerXSymbol:
            self.db.add_computer_game("Человек", self.difficulty, time_str, self.size)
        elif winner:
            self.db.add_computer_game("Компьютер", self.difficulty, time_str, self.size)
        else:
            self.db.add_computer_game("Ничья", self.difficulty, time_str, self.size)

        for button in self.buttons:
            button.setEnabled(False)
        
        if winner:
            win_line = self.get_winning_line(winner)
            if winner == self.playerXSymbol:
                message = "Вы выиграли!"
                for pos in win_line:
                    self.buttons[pos].setStyleSheet("""
                        QPushButton {
                            background-color: #98FB98;
                            color: #006400;
                            font-weight: bold;
                            border: 2px solid #006400;
                        }
                    """)
            else:
                message = "Компьютер выиграл!"
                for pos in win_line:
                    self.buttons[pos].setStyleSheet("""
                        QPushButton {
                            background-color: #FF4500;
                            color: #FFFFFF;
                            font-weight: bold;
                            border: 2px solid #8B0000;
                        }
                    """)
        else:
            message = "Ничья!"
            for button in self.buttons:
                button.setStyleSheet("""
                    QPushButton {
                        background-color: #FFD700;
                        color: #8B4513;
                        font-weight: bold;
                        border: 2px solid #8B4513;
                    }
                """)
        
        QMessageBox.information(self, "Игра окончена", message)

    def show_difficulty_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Выбор сложности игры")
        dialog.setMinimumWidth(250)
        layout = QVBoxLayout()

        group = QButtonGroup(dialog)
        easy_button = QRadioButton("Легкий")
        medium_button = QRadioButton("Средний")
        hard_button = QRadioButton("Сложный")
        group.addButton(easy_button)
        group.addButton(medium_button)
        group.addButton(hard_button)

        if self.difficulty == "easy":
            easy_button.setChecked(True)
        elif self.difficulty == "medium":
            medium_button.setChecked(True)
        else:
            hard_button.setChecked(True)

        layout.addWidget(easy_button)
        layout.addWidget(medium_button)
        layout.addWidget(hard_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)

        dialog.setLayout(layout)

        if dialog.exec_():
            if easy_button.isChecked():
                self.difficulty = "easy"
            elif medium_button.isChecked():
                self.difficulty = "medium"
            else:
                self.difficulty = "hard"

    def return_to_menu(self):
        self.close()
        game_choice = GameChoice()
        game_choice.show()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        button_size = min(self.width() // self.size, self.height() // (self.size + 2))
        for button in self.buttons:
            button.setFixedSize(button_size, button_size)
            font = button.font()
            font.setPointSize(button_size // 3)
            button.setFont(font)
        self.layoutB.invalidate()
        self.layoutB.update()

        font_size = min(self.height() // 20, 24)
        self.label.setFont(QFont("Arial", font_size))

    def return_to_lobby(self):
        self.close()
        self.game_choice = GameChoice()
        self.game_choice.show()

class DatabaseHelper:
    def __init__(self):    
        self.conn = sqlite3.connect('game_stats.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS two_player_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            winner TEXT NOT NULL,                 
            game_time TEXT NOT NULL,              
            board_size INTEGER NOT NULL,          
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        cursor.execute('''CREATE TABLE IF NOT EXISTS computer_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            winner TEXT NOT NULL, 
            difficulty TEXT NOT NULL,            
            game_time TEXT NOT NULL,           
            board_size INTEGER NOT NULL,
            date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        self.conn.commit()

    def add_two_player_game(self, winner, game_time, board_size):
        cursor = self.conn.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute('''INSERT INTO two_player_stats (winner, game_time, board_size, date_time)
                      VALUES (?, ?, ?, ?)''', (winner, game_time, board_size, current_time))
        self.conn.commit()

    def add_computer_game(self, winner, difficulty, game_time, board_size):
        cursor = self.conn.cursor()
        cursor.execute('''INSERT INTO computer_stats (winner, difficulty, game_time, board_size)
                          VALUES (?, ?, ?, ?)''', (winner, difficulty, game_time, board_size))
        self.conn.commit()

    def get_two_player_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM two_player_stats ORDER BY date_time DESC LIMIT 10')
        return cursor.fetchall()

    def get_computer_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM computer_stats ORDER BY date_time DESC LIMIT 10')
        return cursor.fetchall()

    def get_all_two_player_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM two_player_stats ORDER BY date_time DESC')
        return cursor.fetchall()

    def get_all_computer_stats(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM computer_stats ORDER BY date_time DESC')
        return cursor.fetchall()

class StatisticsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("статистика игр")
        self.resize(800, 600)
        self.db = DatabaseHelper()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        return_button = QPushButton("Вернуться в меню")
        return_button.clicked.connect(self.return_to_menu)
        layout.addWidget(return_button)

        stats_layout = QHBoxLayout()

        two_player_group = QGroupBox("СТАТИСТИКА ИГРЫ ВДВОЁМ")
        two_player_layout = QVBoxLayout()
        self.two_player_text = QTextEdit()
        self.two_player_text.setReadOnly(True)
        two_player_layout.addWidget(self.two_player_text)
        
        all_games_button = QPushButton("все игры")
        all_games_button.clicked.connect(self.show_all_two_player_games)
        two_player_layout.addWidget(all_games_button)
        two_player_group.setLayout(two_player_layout)
        stats_layout.addWidget(two_player_group)
    

        computer_group = QGroupBox("СТАТИСТИКА ИГРЫ С КОМЬЮТЕРОМ")
        computer_layout = QVBoxLayout()
        self.computer_text = QTextEdit()
        self.computer_text.setReadOnly(True)
        computer_layout.addWidget(self.computer_text)
        
        all_computer_games_button = QPushButton("все игры")
        all_computer_games_button.clicked.connect(self.show_all_computer_games)
        computer_layout.addWidget(all_computer_games_button)
        computer_group.setLayout(computer_layout)
        stats_layout.addWidget(computer_group)

        layout.addLayout(stats_layout)
        self.setLayout(layout)
        
        self.update_statistics()

    def update_statistics(self):
        two_player_stats = self.db.get_two_player_stats()
        two_player_text = "Последние 10 игр:\n\n"
        for stat in two_player_stats:
            two_player_text += f"Победитель: {stat[1]}\n"
            two_player_text += f"Время игры: {stat[2]}\n"
            two_player_text += f"Размер поля: {stat[3]}x{stat[3]}\n"
            two_player_text += f"Дата: {stat[4]}\n\n"
        self.two_player_text.setText(two_player_text)

        computer_stats = self.db.get_computer_stats()
        computer_text = "Последние 10 игр:\n\n"
        for stat in computer_stats:
            computer_text += f"Победитель: {stat[1]}\n"
            computer_text += f"Сложность: {stat[2]}\n"
            computer_text += f"Время игры: {stat[3]}\n"
            computer_text += f"Размер поля: {stat[4]}x{stat[4]}\n"
            computer_text += f"Дата: {stat[5]}\n\n"
        self.computer_text.setText(computer_text)

    def show_all_two_player_games(self):
        all_games_window = AllGamesWindow("Игра вдвоём", self.db.get_all_two_player_stats())
        all_games_window.exec_()

    def show_all_computer_games(self):
        all_games_window = AllGamesWindow("Игра с компьютером", self.db.get_all_computer_stats())
        all_games_window.exec_()

    def return_to_menu(self):
        self.close()
        self.lobby = Lobby()
        self.lobby.show()


class AllGamesWindow(QDialog):
    def __init__(self, title, games):
        super().__init__()        
        self.setWindowTitle(f"Все игры - {title}")
        self.resize(600, 400)
        self.setModal(True)
        layout = QVBoxLayout()
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        if not games:
            no_games_label = QLabel("Пока нет сохраненных игр")
            no_games_label.setAlignment(Qt.AlignCenter)
            text_layout.addWidget(no_games_label)
        
        for stat in games:
            game_info = QLabel()
            game_info.setWordWrap(True)
            if len(stat) == 5:
                date_time = datetime.strptime(stat[4], '%Y-%m-%d %H:%M:%S')
                info_text = f"""
                <p style='margin:10px;'>
                <b>Победитель:</b> {stat[1]}<br>
                <b>Время игры:</b> {stat[2]}<br>
                <b>Размер поля:</b> {stat[3]}x{stat[3]}<br>
                <b>Дата и время:</b> {date_time.strftime('%d.%m.%Y %H:%M:%S')}
                </p>
                """
            else: 
                date_time = datetime.strptime(stat[5], '%Y-%m-%d %H:%M:%S')
                info_text = f"""
                <p style='margin:10px;'>
                <b>Победитель:</b> {stat[1]}<br>
                <b>Сложность:</b> {stat[2]}<br>
                <b>Время игры:</b> {stat[3]}<br>
                <b>Размер поля:</b> {stat[4]}x{stat[4]}<br>
                <b>Дата и время:</b> {date_time.strftime('%d.%m.%Y %H:%M:%S')}
                </p>
                """
            game_info.setText(info_text)
            text_layout.addWidget(game_info)
            
        text_layout.addStretch()
        scroll.setWidget(text_widget)
        layout.addWidget(scroll)
        
        close_button = QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)
        
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Lobby()
    window.show()
    sys.exit(app.exec())