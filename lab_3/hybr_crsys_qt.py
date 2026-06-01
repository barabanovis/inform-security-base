import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QLabel, QTextEdit,
                             QFileDialog, QMessageBox, QGroupBox, QRadioButton,
                             QTabWidget, QFrame, QProgressBar, QScrollArea,
                             QComboBox)  # Убран QSpinBox
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation
from PyQt5.QtGui import QColor

import modules_folder.key_generation as key_generation
import modules_folder.encryption as encryption
import modules_folder.decryption as decryption


class AnimatedButton(QPushButton):
    """Кнопка с анимацией при наведении"""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.animation = QPropertyAnimation(self, b"color")
        self.animation.setDuration(200)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.animation.stop()
        self.animation.setEndValue(QColor(150, 200, 255))
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.stop()
        self.animation.setEndValue(QColor(220, 220, 255))
        self.animation.start()
        super().leaveEvent(event)


class CryptoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings_file = 'settings.json'
        self.json_data = self.read_json()
        self.init_ui()
        self.setup_styles()

    def read_json(self):
        """Читает настройки из JSON файла"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
                # Устанавливаем значение по умолчанию для длины ключа 3DES, если его нет
                if 'symm_key_length' not in data:
                    data['symm_key_length'] = 24  # 192 бита по умолчанию
                return data
        except FileNotFoundError:
            QMessageBox.warning(
                self, "Ошибка", f"Файл {self.settings_file} не найден!")
            return {'symm_key_length': 24}
        except json.JSONDecodeError:
            QMessageBox.warning(
                self, "Ошибка", "Ошибка в формате settings.json!")
            return {'symm_key_length': 24}

    def save_json(self):
        """Сохраняет настройки в JSON файл"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as json_file:
                json.dump(self.json_data, json_file,
                          indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            QMessageBox.critical(
                self, "Ошибка", f"Не удалось сохранить settings.json:\n{str(e)}")
            return False

    def setup_styles(self):
        """Настройка стилей приложения с яркими цветами"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1e1e2e;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4a4a6a;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                font-size: 14px;
                color: #e0e0ff;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #a0a0ff;
            }
            QRadioButton {
                color: #e0e0ff;
                font-size: 13px;
                padding: 5px;
            }
            QRadioButton::indicator {
                width: 15px;
                height: 15px;
            }
            QRadioButton::indicator::unchecked {
                background-color: #2a2a3a;
                border: 2px solid #6a6a9a;
                border-radius: 8px;
            }
            QRadioButton::indicator::checked {
                background-color: #8a8aff;
                border: 2px solid #aaaaff;
                border-radius: 8px;
            }
            QLabel {
                color: #e0e0ff;
                font-size: 12px;
            }
            QPushButton {
                background-color: #2a2a3a;
                border: 2px solid #5a5a8a;
                border-radius: 8px;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
                color: #e0e0ff;
            }
            QPushButton:hover {
                background-color: #3a3a4a;
                border-color: #8a8aff;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #1a1a2a;
            }
            QTextEdit, QPlainTextEdit {
                background-color: #2a2a3a;
                border: 2px solid #4a4a6a;
                border-radius: 8px;
                color: #e0e0ff;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                padding: 5px;
            }
            QComboBox {
                background-color: #2a2a3a;
                border: 2px solid #4a4a6a;
                border-radius: 8px;
                padding: 5px;
                color: #e0e0ff;
                font-size: 12px;
                min-width: 100px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 2px solid #8a8aff;
                border-bottom: 2px solid #8a8aff;
                width: 8px;
                height: 8px;
            }
            QComboBox QAbstractItemView {
                background-color: #2a2a3a;
                color: #e0e0ff;
                border: 2px solid #4a4a6a;
                selection-background-color: #4a4a6a;
            }
            QTabWidget::pane {
                background-color: #2a2a3a;
                border: 2px solid #4a4a6a;
                border-radius: 10px;
            }
            QTabBar::tab {
                background-color: #1e1e2e;
                color: #c0c0e0;
                padding: 8px 15px;
                margin: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background-color: #2a2a3a;
                color: #aaaaff;
                border-bottom: 2px solid #8a8aff;
            }
            QTabBar::tab:hover {
                background-color: #3a3a4a;
                color: #ffffff;
            }
            QProgressBar {
                border: 2px solid #4a4a6a;
                border-radius: 8px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #8a8aff;
                border-radius: 6px;
            }
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)

    def init_ui(self):
        """Инициализация пользовательского интерфейса"""
        self.setWindowTitle('🔐 Гибридная криптографическая система')
        self.setGeometry(100, 100, 1000, 800)

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Основной вертикальный layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Заголовок с градиентом
        title_widget = QWidget()
        title_layout = QVBoxLayout()

        # Основной заголовок
        main_title = QLabel("🔒 Hybrid Cryptosystem")
        main_title.setStyleSheet("""
            font-size: 28px; 
            font-weight: bold; 
            color: #c0c0ff; 
            padding: 10px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                       stop:0 #4a4a6a, stop:1 #2a2a3a);
            border-radius: 10px;
        """)
        main_title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(main_title)

        # Статус
        status_label = QLabel("✅ Готов к работе")
        status_label.setStyleSheet("""
            color: #aaffaa; 
            font-size: 13px; 
            padding: 5px;
            font-weight: bold;
        """)
        status_label.setAlignment(Qt.AlignRight)
        title_layout.addWidget(status_label)

        title_widget.setLayout(title_layout)
        main_layout.addWidget(title_widget)

        # Создаем вкладки
        tabs = QTabWidget()
        tabs.setStyleSheet("QTabWidget::tab-bar { alignment: center; }")
        main_layout.addWidget(tabs)

        # Вкладка настроек
        settings_tab = QWidget()
        tabs.addTab(settings_tab, "⚙️ Настройки")

        # Вкладка просмотра файлов
        view_tab = QWidget()
        tabs.addTab(view_tab, "📄 Просмотр файлов")

        # Вкладка логов
        log_tab = QWidget()
        tabs.addTab(log_tab, "📝 Лог операций")

        # Вкладка информации (с прокруткой)
        info_tab = QWidget()
        tabs.addTab(info_tab, "ℹ️ О программе")

        # ============ Вкладка настроек ============
        settings_layout = QVBoxLayout()
        settings_tab.setLayout(settings_layout)

        # Группа выбора режима работы
        mode_group = QGroupBox("🎯 Выберите режим работы")
        mode_layout = QHBoxLayout()

        self.radio_gen = QRadioButton("🔑 Генерация ключей")
        self.radio_enc = QRadioButton("🔒 Шифрование")
        self.radio_dec = QRadioButton("🔓 Дешифрование")

        # Устанавливаем стиль для радио-кнопок
        for rb in [self.radio_gen, self.radio_enc, self.radio_dec]:
            rb.setStyleSheet("""
                font-size: 14px; 
                padding: 8px;
                color: #e0e0ff;
            """)

        self.radio_gen.toggled.connect(self.on_mode_changed)
        self.radio_enc.toggled.connect(self.on_mode_changed)
        self.radio_dec.toggled.connect(self.on_mode_changed)

        mode_layout.addWidget(self.radio_gen)
        mode_layout.addWidget(self.radio_enc)
        mode_layout.addWidget(self.radio_dec)
        mode_layout.addStretch()
        mode_group.setLayout(mode_layout)
        settings_layout.addWidget(mode_group)

        # Группа настроек криптографии (только для 3DES)
        crypto_group = QGroupBox("🔐 Криптографические настройки")
        crypto_layout = QVBoxLayout()

        # Настройка длины симметричного ключа для 3DES
        des_layout = QHBoxLayout()
        des_layout.addWidget(QLabel("🔑 Длина ключа 3DES:"))

        self.key_length_combo = QComboBox()
        # 3DES поддерживает длины: 64 бита (8 байт), 128 бит (16 байт), 192 бита (24 байта)
        self.key_length_combo.addItem(
            "64 бита (8 байт) - 1DES (совместимость)", 8)
        self.key_length_combo.addItem("128 бит (16 байт) - 2DES", 16)
        self.key_length_combo.addItem(
            "192 бита (24 байт) - 3DES (рекомендуется)", 24)

        # Устанавливаем текущее значение из настроек
        current_length = self.json_data.get('symm_key_length', 24)
        # Находим соответствующий индекс
        index = self.key_length_combo.findData(current_length)
        if index >= 0:
            self.key_length_combo.setCurrentIndex(index)

        self.key_length_combo.currentIndexChanged.connect(
            self.on_key_length_changed)
        des_layout.addWidget(self.key_length_combo)

        # Добавляем пояснение
        des_info = QLabel("(для шифрования/дешифрования)")
        des_info.setStyleSheet("color: #a0a0ff; font-size: 10px;")
        des_layout.addWidget(des_info)
        des_layout.addStretch()

        crypto_layout.addLayout(des_layout)

        # Добавляем информационную метку
        info_label = QLabel("ℹ️ 3DES: Triple Data Encryption Standard - симметричный блочный шифр\n"
                            "ℹ️ RSA: Асимметричный алгоритм (2048 бит) для шифрования симметричного ключа")
        info_label.setStyleSheet(
            "color: #a0a0ff; font-size: 11px; padding: 5px; margin-top: 5px;")
        info_label.setWordWrap(True)
        crypto_layout.addWidget(info_label)

        crypto_group.setLayout(crypto_layout)
        settings_layout.addWidget(crypto_group)

        # Группа для отображения/изменения путей
        paths_group = QGroupBox("📁 Пути к файлам (settings.json)")
        paths_layout = QVBoxLayout()

        # Создаем строки для каждого пути
        self.path_labels = {}

        # Категория: Ключи
        keys_label = QLabel("🔐 Файлы ключей:")
        keys_label.setStyleSheet("""
            font-weight: bold; 
            color: #aaaaff; 
            font-size: 14px; 
            margin-top: 5px;
            padding: 5px;
        """)
        paths_layout.addWidget(keys_label)

        for key_name, label_text in [('public_key', 'Публичный ключ'),
                                     ('private_key', 'Приватный ключ'),
                                     ('secret_key', 'Секретный ключ')]:
            paths_layout.addLayout(self.create_path_row(label_text, key_name))

        # Разделитель
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("background-color: #5a5a8a; margin: 10px;")
        paths_layout.addWidget(separator)

        # Категория: Данные
        data_label = QLabel("📄 Файлы данных:")
        data_label.setStyleSheet("""
            font-weight: bold; 
            color: #aaaaff; 
            font-size: 14px; 
            margin-top: 5px;
            padding: 5px;
        """)
        paths_layout.addWidget(data_label)

        for key_name, label_text in [('initial_file', 'Исходный файл'),
                                     ('encrypted_file', 'Зашифрованный файл'),
                                     ('decrypted_file', 'Расшифрованный файл'),
                                     ('symmetric_key', 'Симметричный ключ')]:
            paths_layout.addLayout(self.create_path_row(label_text, key_name))

        paths_group.setLayout(paths_layout)
        settings_layout.addWidget(paths_group)

        # Кнопки управления
        buttons_layout = QHBoxLayout()

        self.btn_save = AnimatedButton("💾 Сохранить изменения")
        self.btn_save.clicked.connect(self.save_settings)
        buttons_layout.addWidget(self.btn_save)

        self.btn_execute = AnimatedButton("▶️ Выполнить операцию")
        self.btn_execute.setMinimumHeight(45)
        self.btn_execute.setStyleSheet("""
            QPushButton {
                background-color: #4a4a6a;
                border: 2px solid #8a8aff;
                font-size: 14px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #5a5a7a;
                border-color: #aaaaff;
                color: #ffffff;
            }
        """)
        self.btn_execute.clicked.connect(self.execute_operation)
        buttons_layout.addWidget(self.btn_execute)

        settings_layout.addLayout(buttons_layout)

        # ============ Вкладка просмотра файлов ============
        view_layout = QVBoxLayout()
        view_tab.setLayout(view_layout)

        # Выбор файла для просмотра
        file_selector_layout = QHBoxLayout()
        file_selector_layout.addWidget(QLabel("📂 Выберите файл:"))
        self.view_file_label = QLabel("Не выбран")
        self.view_file_label.setStyleSheet("""
            border: 2px solid #5a5a8a; 
            border-radius: 5px; 
            padding: 5px;
            color: #e0e0ff;
            background-color: #2a2a3a;
        """)
        file_selector_layout.addWidget(self.view_file_label, 1)

        self.btn_view_file = AnimatedButton("🔍 Выбрать файл")
        self.btn_view_file.clicked.connect(self.select_file_to_view)
        file_selector_layout.addWidget(self.btn_view_file)

        self.btn_refresh_view = AnimatedButton("🔄 Обновить")
        self.btn_refresh_view.clicked.connect(self.refresh_file_view)
        file_selector_layout.addWidget(self.btn_refresh_view)

        view_layout.addLayout(file_selector_layout)

        # Текстовое поле для просмотра
        self.view_text = QTextEdit()
        self.view_text.setReadOnly(True)
        self.view_text.setStyleSheet("""
            background-color: #1e1e2e;
            color: #e0e0ff;
            font-size: 12px;
        """)
        view_layout.addWidget(self.view_text)

        # ============ Вкладка логов ============
        log_layout = QVBoxLayout()
        log_tab.setLayout(log_layout)

        # Кнопки управления логами
        log_buttons_layout = QHBoxLayout()
        self.btn_clear_log = AnimatedButton("🗑️ Очистить лог")
        self.btn_clear_log.clicked.connect(self.clear_log)
        log_buttons_layout.addWidget(self.btn_clear_log)

        self.btn_export_log = AnimatedButton("💾 Экспорт лога")
        self.btn_export_log.clicked.connect(self.export_log)
        log_buttons_layout.addWidget(self.btn_export_log)
        log_buttons_layout.addStretch()

        log_layout.addLayout(log_buttons_layout)

        # Текстовое поле для логов
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            background-color: #1e1e2e;
            color: #e0e0ff;
            font-size: 12px;
            font-family: 'Consolas', monospace;
        """)
        log_layout.addWidget(self.log_text)

        # Прогресс бар
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #5a5a8a;
                border-radius: 8px;
                text-align: center;
                color: #ffffff;
                font-weight: bold;
                background-color: #2a2a3a;
            }
            QProgressBar::chunk {
                background-color: #8aff8a;
                border-radius: 6px;
            }
        """)
        log_layout.addWidget(self.progress_bar)

        # ============ Вкладка информации (с прокруткой) ============
        # Создаем scroll area для информации
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #2a2a3a;
                border-radius: 10px;
            }
            QScrollBar:vertical {
                border: none;
                background: #2a2a3a;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #6a6a9a;
                border-radius: 5px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #8a8aff;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)

        # Контейнер для содержимого
        info_container = QWidget()
        info_layout_tab = QVBoxLayout()
        info_container.setLayout(info_layout_tab)

        # Информационный виджет
        info_widget = QFrame()
        info_widget.setStyleSheet("""
            QFrame {
                background-color: #2a2a3a;
                border-radius: 15px;
                padding: 20px;
            }
            QLabel {
                color: #e0e0ff;
                font-size: 13px;
            }
        """)
        info_main_layout = QVBoxLayout()
        info_widget.setLayout(info_main_layout)

        # Заголовок
        title_info = QLabel("📋 Гибридная криптографическая система")
        title_info.setStyleSheet(
            "font-size: 20px; font-weight: bold; color: #c0c0ff; padding: 10px;")
        title_info.setAlignment(Qt.AlignCenter)
        info_main_layout.addWidget(title_info)

        # Описание
        description = QLabel(
            "Данная программа реализует гибридную криптосистему,\n"
            "сочетающую в себе преимущества симметричного и\n"
            "асимметричного шифрования.\n\n"
            "🔑 Возможности программы:\n"
            "• Генерация ключевых пар (RSA 2048 бит)\n"
            "• Шифрование файлов с использованием гибридной схемы\n"
            "• Дешифрование файлов\n"
            "• Просмотр содержимого файлов\n"
            "• Ведение лога операций\n\n"
            "🛡️ Используемые алгоритмы:\n"
            "• RSA (асимметричное шифрование, 2048 бит)\n"
            "• 3DES (симметричное шифрование, 64/128/192 бит)\n"
            "• Гибридная схема шифрования"
        )
        description.setAlignment(Qt.AlignLeft)
        description.setStyleSheet(
            "font-size: 12px; padding: 10px; line-height: 1.5;")
        description.setWordWrap(True)
        info_main_layout.addWidget(description)

        # Разделитель
        sep_line = QLabel("─" * 80)
        sep_line.setAlignment(Qt.AlignCenter)
        sep_line.setStyleSheet("color: #5a5a8a; font-size: 10px;")
        info_main_layout.addWidget(sep_line)

        # Информация о разработчике
        dev_title = QLabel("👨‍💻 Разработчик:")
        dev_title.setStyleSheet(
            "font-weight: bold; color: #aaaaff; font-size: 14px; margin-top: 10px;")
        info_main_layout.addWidget(dev_title)

        dev_info = QLabel(
            "Барабанов Иван Сергеевич\n"
            "Студент Самарского университета имени академика С.П. Королева\n"
            "Группа: 6212-100503D"
        )
        dev_info.setStyleSheet("font-size: 12px; padding: 5px;")
        dev_info.setWordWrap(True)
        info_main_layout.addWidget(dev_info)

        # Руководитель
        teacher_title = QLabel("👩‍🏫 Руководитель:")
        teacher_title.setStyleSheet(
            "font-weight: bold; color: #aaaaff; font-size: 14px; margin-top: 10px;")
        info_main_layout.addWidget(teacher_title)

        teacher_info = QLabel(
            "Позднякова Дарья Сергеевна\n"
            "Преподаватель кафедры геоинформатики и информационной безопасности"
        )
        teacher_info.setStyleSheet("font-size: 12px; padding: 5px;")
        teacher_info.setWordWrap(True)
        info_main_layout.addWidget(teacher_info)

        # Версия
        version_label = QLabel("Версия: 1.0.0 | © 2024")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setStyleSheet(
            "font-size: 10px; color: #8a8aaa; margin-top: 20px;")
        info_main_layout.addWidget(version_label)

        # Добавляем информационный виджет в контейнер
        info_layout_tab.addWidget(info_widget)
        info_layout_tab.addStretch()

        # Устанавливаем контейнер в scroll area
        scroll_area.setWidget(info_container)

        # Добавляем scroll area на вкладку
        info_tab_layout = QVBoxLayout()
        info_tab_layout.addWidget(scroll_area)
        info_tab.setLayout(info_tab_layout)

        # Устанавливаем начальное состояние
        self.radio_gen.setChecked(True)

        # Приветственное сообщение
        self.log("✨ Добро пожаловать в Hybrid Cryptosystem!")
        self.log("🔐 Готов к выполнению криптографических операций")
        self.log(f"🔑 Текущая длина ключа 3DES: {self.key_length_combo.currentData()} байт "
                 f"({self.key_length_combo.currentData() * 8} бит)")

    def on_key_length_changed(self, index):
        """Обработчик изменения длины ключа 3DES"""
        key_length_bytes = self.key_length_combo.currentData()
        key_length_bits = key_length_bytes * 8
        self.json_data['symm_key_length'] = key_length_bytes
        self.log(
            f"🔑 Установлена длина ключа 3DES: {key_length_bits} бит ({key_length_bytes} байт)")

    def create_path_row(self, label_text, key_name):
        """Создает строку с меткой, путем и кнопкой изменения"""
        layout = QHBoxLayout()
        label = QLabel(f"{label_text}:")
        label.setMinimumWidth(150)
        label.setStyleSheet("""
            font-size: 12px;
            color: #e0e0ff;
            font-weight: bold;
        """)
        layout.addWidget(label)

        path_label = QLabel(self.json_data.get(key_name, "❌ Не указан"))
        path_label.setStyleSheet("""
            border: 1px solid #6a6a9a; 
            border-radius: 5px; 
            padding: 5px; 
            background-color: #2a2a3a;
            color: #d0d0ff;
        """)
        path_label.setWordWrap(True)
        layout.addWidget(path_label, 1)

        btn = AnimatedButton("📁 Изменить")
        btn.clicked.connect(lambda: self.change_path(key_name, path_label))
        layout.addWidget(btn)

        # Сохраняем ссылку на label для обновления
        self.path_labels[key_name] = path_label

        return layout

    def change_path(self, key_name, path_label):
        """Изменяет путь в зависимости от типа ключа"""
        current_path = self.json_data.get(key_name, "")

        # Определяем, что нужно выбирать: файл или папку
        if key_name in ['public_key', 'private_key', 'secret_key', 'symmetric_key']:
            file_path, _ = QFileDialog.getSaveFileName(
                self, f"Выберите файл для {key_name}",
                current_path,
                "Все файлы (*.*)"
            )
            if file_path:
                self.json_data[key_name] = file_path
                path_label.setText(file_path)
                self.log(f"📁 Изменен путь {key_name}: {file_path}")
        else:
            file_path, _ = QFileDialog.getOpenFileName(
                self, f"Выберите файл для {key_name}",
                current_path,
                "Все файлы (*.*)"
            )
            if file_path:
                self.json_data[key_name] = file_path
                path_label.setText(file_path)
                self.log(f"📁 Изменен путь {key_name}: {file_path}")

    def select_file_to_view(self):
        """Выбор файла для просмотра"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите файл для просмотра", "", "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if file_path:
            self.view_file_label.setText(file_path)
            self.refresh_file_view()

    def refresh_file_view(self):
        """Обновление содержимого файла в окне просмотра"""
        file_path = self.view_file_label.text()
        if file_path and file_path != "Не выбран" and os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.view_text.setPlainText(content)
                self.log(f"📖 Просмотрен файл: {file_path}")
            except UnicodeDecodeError:
                # Пробуем прочитать как бинарный файл
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read(1000)  # Читаем первые 1000 байт
                    self.view_text.setPlainText(
                        f"⚠️ Файл не является текстовым или имеет другую кодировку.\n\n"
                        f"Первые 1000 байт (в hex):\n{content.hex()}"
                    )
                    self.log(f"⚠️ Файл {file_path} не является текстовым")
                except Exception as e:
                    self.view_text.setPlainText(
                        f"❌ Ошибка при чтении файла:\n{str(e)}")
                    self.log(f"❌ Ошибка просмотра файла {file_path}: {str(e)}")
            except Exception as e:
                self.view_text.setPlainText(
                    f"❌ Ошибка при чтении файла:\n{str(e)}")
                self.log(f"❌ Ошибка просмотра файла {file_path}: {str(e)}")

    def save_settings(self):
        """Сохраняет настройки в JSON файл"""
        if self.save_json():
            self.log("✅ Настройки сохранены в settings.json")
            QMessageBox.information(
                self, "✅ Успех", "Настройки успешно сохранены!")
        else:
            self.log("❌ Ошибка при сохранении настроек")
            QMessageBox.critical(
                self, "❌ Ошибка", "Не удалось сохранить настройки!")

    def clear_log(self):
        """Очистка лога"""
        self.log_text.clear()
        self.log("🗑️ Лог очищен")

    def export_log(self):
        """Экспорт лога в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить лог", "log.txt", "Текстовые файлы (*.txt)"
        )
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                self.log(f"💾 Лог экспортирован в {file_path}")
                QMessageBox.information(
                    self, "✅ Успех", f"Лог сохранен в:\n{file_path}")
            except Exception as e:
                self.log(f"❌ Ошибка экспорта лога: {str(e)}")
                QMessageBox.critical(
                    self, "❌ Ошибка", f"Не удалось экспортировать лог:\n{str(e)}")

    def on_mode_changed(self):
        """Обработчик изменения режима работы"""
        if self.radio_gen.isChecked():
            self.log("🎯 Режим: Генерация ключей")
        elif self.radio_enc.isChecked():
            self.log("🎯 Режим: Шифрование")
        else:
            self.log("🎯 Режим: Дешифрование")

    def log(self, message):
        """Добавление сообщения в лог"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

        # Прокручиваем вниз
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def execute_operation(self):
        """Выполнение выбранной операции"""
        # Сохраняем текущие настройки
        if not self.save_json():
            return

        # Показываем прогресс бар
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        if self.radio_gen.isChecked():
            self.generate_keys()
        elif self.radio_enc.isChecked():
            self.encrypt_data()
        elif self.radio_dec.isChecked():
            self.decrypt_data()

        self.progress_bar.setValue(100)
        QTimer.singleShot(1000, lambda: self.progress_bar.setVisible(False))

    def generate_keys(self):
        """Генерация ключей"""
        try:
            self.log("=" * 50)
            self.log("🔐 НАЧАЛО ГЕНЕРАЦИИ КЛЮЧЕЙ")

            # Проверяем, что все пути для ключей указаны
            required_keys = ['public_key', 'private_key', 'secret_key']
            missing_keys = [
                key for key in required_keys if not self.json_data.get(key)]

            if missing_keys:
                self.log(
                    f"❌ Ошибка: Не указаны пути для: {', '.join(missing_keys)}")
                QMessageBox.warning(self, "⚠️ Ошибка",
                                    f"В settings.json не указаны пути для:\n{', '.join(missing_keys)}")
                return

            self.log(f"📁 Публичный ключ: {self.json_data['public_key']}")
            self.log(f"📁 Приватный ключ: {self.json_data['private_key']}")
            self.log(f"📁 Секретный ключ: {self.json_data['secret_key']}")

            # Создаем директории, если их нет
            for key in required_keys:
                path = self.json_data[key]
                directory = os.path.dirname(path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                    self.log(f"📁 Создана директория: {directory}")

            # Вызываем функцию генерации ключей
            key_generation.key_gen_and_save(self.json_data)

            self.log("✅ КЛЮЧИ УСПЕШНО СГЕНЕРИРОВАНЫ!")
            self.log("=" * 50)
            QMessageBox.information(self, "✅ УСПЕХ!",
                                    "🎉 Ключи успешно сгенерированы!\n\n"
                                    "✅ Публичный ключ\n"
                                    "✅ Приватный ключ\n"
                                    "✅ Секретный ключ\n\n"
                                    "🔑 Длина RSA ключа: 2048 бит")
        except Exception as e:
            self.log(f"❌ ОШИБКА при генерации ключей: {str(e)}")
            QMessageBox.critical(
                self, "❌ Ошибка", f"Ошибка при генерации ключей:\n{str(e)}")

    def encrypt_data(self):
        """Шифрование данных"""
        try:
            self.log("=" * 50)
            self.log("🔒 НАЧАЛО ШИФРОВАНИЯ")

            # Логируем используемую длину ключа
            key_length = self.json_data.get('symm_key_length', 24)
            self.log(
                f"🔑 Используется длина ключа 3DES: {key_length * 8} бит ({key_length} байт)")

            # Проверяем, что все необходимые пути указаны
            required_keys = ['initial_file', 'encrypted_file', 'public_key']
            missing_keys = [
                key for key in required_keys if not self.json_data.get(key)]

            if missing_keys:
                self.log(
                    f"❌ Ошибка: Не указаны пути для: {', '.join(missing_keys)}")
                QMessageBox.warning(self, "⚠️ Ошибка",
                                    f"В settings.json не указаны пути для:\n{', '.join(missing_keys)}")
                return

            # Проверяем существование входного файла
            if not os.path.exists(self.json_data['initial_file']):
                self.log(
                    f"❌ Исходный файл не найден: {self.json_data['initial_file']}")
                QMessageBox.warning(self, "⚠️ Ошибка",
                                    f"Исходный файл не найден:\n{self.json_data['initial_file']}")
                return

            # Проверяем существование публичного ключа
            if not os.path.exists(self.json_data['public_key']):
                self.log(
                    f"❌ Публичный ключ не найден: {self.json_data['public_key']}")
                QMessageBox.warning(self, "⚠️ Ошибка",
                                    f"Файл публичного ключа не найден:\n{self.json_data['public_key']}\n\n"
                                    f"🔑 Сначала сгенерируйте ключи!")
                return

            self.log(f"📁 Исходный файл: {self.json_data['initial_file']}")
            self.log(
                f"📁 Зашифрованный файл: {self.json_data['encrypted_file']}")
            self.log(f"📁 Публичный ключ: {self.json_data['public_key']}")

            # Создаем директорию для выходного файла, если её нет
            output_dir = os.path.dirname(self.json_data['encrypted_file'])
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.log(f"📁 Создана директория: {output_dir}")

            # Вызываем функцию шифрования
            encryption.data_encryption(self.json_data)

            self.log("✅ ДАННЫЕ УСПЕШНО ЗАШИФРОВАНЫ!")
            self.log(
                f"📁 Результат сохранен в: {self.json_data['encrypted_file']}")
            self.log("=" * 50)
            QMessageBox.information(self, "✅ УСПЕХ!",
                                    f"🎉 Шифрование завершено успешно!\n\n"
                                    f"📁 Входной файл: {os.path.basename(self.json_data['initial_file'])}\n"
                                    f"📁 Выходной файл: {os.path.basename(self.json_data['encrypted_file'])}\n"
                                    f"🔑 Длина ключа 3DES: {key_length * 8} бит\n\n"
                                    f"✅ Данные защищены!")
        except Exception as e:
            self.log(f"❌ ОШИБКА при шифровании: {str(e)}")
            QMessageBox.critical(
                self, "❌ Ошибка", f"Ошибка при шифровании:\n{str(e)}")

    def decrypt_data(self):
        """Дешифрование данных"""
        try:
            self.log("=" * 50)
            self.log("🔓 НАЧАЛО ДЕШИФРОВАНИЯ")

            # Логируем используемую длину ключа
            key_length = self.json_data.get('symm_key_length', 24)
            self.log(
                f"🔑 Используется длина ключа 3DES: {key_length * 8} бит ({key_length} байт)")

            # Проверяем, что все необходимые пути указаны
            required_keys = ['encrypted_file', 'decrypted_file', 'private_key']
            missing_keys = [
                key for key in required_keys if not self.json_data.get(key)]

            if missing_keys:
                self.log(
                    f"❌ Ошибка: Не указаны пути для: {', '.join(missing_keys)}")
                QMessageBox.warning(self, "⚠️ Ошибка",
                                    f"В settings.json не указаны пути для:\n{', '.join(missing_keys)}")
                return

            # Проверяем существование зашифрованного файла
            if not os.path.exists(self.json_data['encrypted_file']):
                self.log(
                    f"❌ Зашифрованный файл не найден: {self.json_data['encrypted_file']}")
                QMessageBox.warning(self, "⚠️ Ошибка",
                                    f"Зашифрованный файл не найден:\n{self.json_data['encrypted_file']}")
                return

            # Проверяем существование приватного ключа
            if not os.path.exists(self.json_data['private_key']):
                self.log(
                    f"❌ Приватный ключ не найден: {self.json_data['private_key']}")
                QMessageBox.warning(self, "⚠️ Ошибка",
                                    f"Файл приватного ключа не найден:\n{self.json_data['private_key']}\n\n"
                                    f"🔑 Сначала сгенерируйте ключи!")
                return

            self.log(
                f"📁 Зашифрованный файл: {self.json_data['encrypted_file']}")
            self.log(
                f"📁 Расшифрованный файл: {self.json_data['decrypted_file']}")
            self.log(f"📁 Приватный ключ: {self.json_data['private_key']}")

            # Создаем директорию для выходного файла, если её нет
            output_dir = os.path.dirname(self.json_data['decrypted_file'])
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)
                self.log(f"📁 Создана директория: {output_dir}")

            # Вызываем функцию дешифрования
            decryption.decryption(self.json_data)

            self.log("✅ ДАННЫЕ УСПЕШНО ДЕШИФРОВАНЫ!")
            self.log(
                f"📁 Результат сохранен в: {self.json_data['decrypted_file']}")
            self.log("=" * 50)
            QMessageBox.information(self, "✅ УСПЕХ!",
                                    f"🎉 Дешифрование завершено успешно!\n\n"
                                    f"📁 Входной файл: {os.path.basename(self.json_data['encrypted_file'])}\n"
                                    f"📁 Выходной файл: {os.path.basename(self.json_data['decrypted_file'])}\n"
                                    f"🔑 Длина ключа 3DES: {key_length * 8} бит\n\n"
                                    f"✅ Исходные данные восстановлены!")
        except Exception as e:
            self.log(f"❌ ОШИБКА при дешифровании: {str(e)}")
            QMessageBox.critical(
                self, "❌ Ошибка", f"Ошибка при дешифровании:\n{str(e)}")


def main():
    app = QApplication(sys.argv)

    # Установка глобальной палитры
    app.setStyle('Fusion')

    window = CryptoApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
