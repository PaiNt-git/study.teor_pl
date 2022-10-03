#!/usr/bin/env python3

# conda activate python3.9

# pip3 install PyGObject
# pip3 install pycairo

# https://adior.ru/index.php/robototekhnika/67-glade-gtk-python-signals
# https://python--gtk--3--tutorial-readthedocs-io.translate.goog/en/latest/builder.html?_x_tr_sl=auto&_x_tr_tl=ru&_x_tr_hl=ru
# https://eax.me/python-gtk/

# ctrl + shift + * + num(1)

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gio
from urllib.parse import urlparse
# from queue import Queue
import json
import os

# Мои классы
from lexical_analyzer import lexical_analyzer


class control_ui:
    def __init__(self, ui_objects):
        self.ui = ui_objects

    @staticmethod
    def read_file(gfcb_button, gtb_target):
        gfcb_file_path = universal_func.get_path_from_GFCB_url_or_none(gfcb_button)
        try:
            with open(file=gfcb_file_path, encoding='utf-8') as file:
                gtb_target.set_text(''.join(file.readlines()))
        except:
            print('Не удалось загрузить %s!' % gfcb_file_path)
            return None

    @staticmethod
    def return_json_data(config_file: str):
        try:
            with open(config_file) as file:
                return json.load(file)
        except:
            print('Не удалось загрузить %s!' % config_file)
            return None

    @staticmethod
    def save_json_data(config_file: str, update_variable_from_ui):
        if hasattr(update_variable_from_ui, '__call__'):
            dump_data = update_variable_from_ui()  # dict
        else:
            dump_data = update_variable_from_ui
        try:
            with open(config_file, 'w+') as file:
                json.dump(dump_data, file, sort_keys=False, indent=4, ensure_ascii=False)
        except:
            print("Невозможно сохранить настройки!")  # PermissionError

    @staticmethod
    def test_connection(*args):
        print('Соединение установлено! Получены аргументы:')
        for num_arg in range(len(args)):
            print('arg[', num_arg, '] = ', args[num_arg], sep='')

    @staticmethod
    def return_text_from_GTextV_as_list(buffer):
        start_iter = buffer.get_start_iter()
        end_iter = buffer.get_end_iter()

        return list(
            map(
                lambda x: x + '\n',
                buffer.get_text(start_iter, end_iter, True).split('\n')
            )
        )


class universal_func:
    correct_path = staticmethod(lambda x: os.path.abspath(os.path.expanduser(x)))

    @staticmethod
    def get_path_from_GFCB_url_or_none(gfcb_button):
        bp = gfcb_button.get_uri()
        bp1 = urlparse(bp)
        bp2 = bp1.path
        bp3 = bp2.strip('/')

        received_path = os.path.normpath(bp3)
        if str(received_path) != "b''":
            return received_path
        return None


class error_dialog(Gtk.Dialog):
    def __init__(self, parent):
        super().__init__(title='Error', transient_for=parent, flags=0)
        self.head = str()
        self.h1_bold_text = str()
        self.message = str()

    def remember_message_fields(self, head=None, h1_bold_text=None, message=None):
        if head:
            self.head = head
        if h1_bold_text:
            self.h1_bold_text = h1_bold_text
        if message:
            self.message = message

    def show_dialog(self):
        dialog = Gtk.MessageDialog(
            title=self.head,
            transient_for=self,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,  # Gtk.ButtonsType.CANCEL,
            text=self.h1_bold_text,
        )
        dialog.format_secondary_text(
            self.message
        )

        dialog.connect("response", lambda x, y: dialog.destroy())
        dialog.show()


class ui(Gtk.Builder):
    def __init__(self, ui_path: str, id_of_ui_main_window: str, GFCB_json_file='GFCB_configs.json'):
        super().__init__()
        self.add_from_file(universal_func.correct_path(ui_path))

        # переменные
        self.id_of_ui_main_window = id_of_ui_main_window  # главное окно (str)
        self.main_window = self.get_object(self.id_of_ui_main_window)  # главное окно (объект)
        self.GFCB_json_file = universal_func.correct_path(GFCB_json_file)  # файл с настройками путей по умолчанию
        self.GFCB_json_dict = control_ui.return_json_data(self.GFCB_json_file)  # словарь с настройками GFCB

        self.connect_main_signals()
        self.run_when_app_starting()
        self.main_window.show_all()
        Gtk.main()

    def connect_main_signals(self):
        # --------------------------------------------------- Общее ----------------------------------------------------
        self.handler_destroy = self.main_window.connect("destroy", Gtk.main_quit)

        # Файл--> Сохранить пути (неидеальный event)
        self.handler_save_paths = self.get_object('GMenu_save_paths').connect(
            "button-press-event",  # плохое действие
            lambda x, y: control_ui.save_json_data(
                self.GFCB_json_file,
                self.update_dict_of_GFCB_json_data
            )
        )
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------- 1 лаба ---------------------------------------------------
        self.handler_lex_read_file = self.get_object('GButton_lex_read_file').connect(  # Прочитать
            "clicked",
            lambda x: control_ui.read_file(
                self.get_object('GFCB_lex_select_file'),
                self.get_object('GTB_content_of_lex_file')
            )
        )

        self.handler_lex_analysis = self.get_object('GButton_lex_analysis').connect(  # Анализ
            "clicked",
            self.instantiate_the_lexical_analyzer
        )

        self.handler_table_of_lex_save_in_file = self.get_object('GButton_table_of_lex_save_in_file').connect(  # Save
            "clicked",
            lambda x: self.save_result_of_lexical_analyzer_to_files(
                universal_func.get_path_from_GFCB_url_or_none(self.get_object('GFCB_out_lex_select_file_1')),
                universal_func.get_path_from_GFCB_url_or_none(self.get_object('GFCB_table_of_lex_select_file'))
            )
        )

        # --------------------------------------------------------------------------------------------------------------

        # ------------------------------------------------- 2 и 3 лаба -------------------------------------------------
        self.handler_out_lex_read_file = self.get_object('GButton_out_lex_read_file').connect(
            "clicked",
            lambda x: control_ui.read_file(
                self.get_object('GFCB_out_lex_select_file_2'),
                self.get_object('GTB_content_of_out_codes_file')
            )
        )
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------- 4 лаба ---------------------------------------------------

        # --------------------------------------------------------------------------------------------------------------

    def run_when_app_starting(self):
        self.update_GFCB_setted_files()
        self.clear_GTreeV_table_of_lex(self.get_object('GLS_list_for_table_of_lex'), add_empty_line=True)

    # ----------------------------------------------------- 1 лаба -----------------------------------------------------
    def instantiate_the_lexical_analyzer(self, *args):  # лексический анализ
        # print(control_ui.return_text_from_GTextV_as_list(self.get_object('GTB_content_of_lex_file')))
        self.lexical_analyzer = lexical_analyzer(
            data_for_analysis=control_ui.return_text_from_GTextV_as_list(self.get_object('GTB_content_of_lex_file'))
        )

        current_status_message = self.lexical_analyzer.run_analysis()

        GLS = self.get_object('GLS_list_for_table_of_lex')
        GLS.clear()

        for line in self.lexical_analyzer.result_of_analysis.table_with_formatted_result:
            GLS.append(line)

        if not current_status_message:
            print('\nУспешный разбор!')
        else:
            error = error_dialog(self.main_window)
            error.remember_message_fields('Лексический анализатор', 'Ошибка разбора!', current_status_message)
            error.show_dialog()

    def save_result_of_lexical_analyzer_to_files(self, file_sequence: str, file_handler: str):
        if not hasattr(self, 'lexical_analyzer'):
            error = error_dialog(self.main_window)
            error.remember_message_fields('Лексический анализатор',
                                          'Ошибка сохранения результата анализа!',
                                          'Сначала проведите анализ!')
            error.show_dialog()
        elif not file_sequence or not file_handler:
            error = error_dialog(self.main_window)
            error.remember_message_fields('Лексический анализатор',
                                          'Ошибка сохранения результата анализа!',
                                          'Указаны не все файлы, куда сохранять полученные данные!')
            error.show_dialog()
        else:
            if hasattr(self.lexical_analyzer.result_of_analysis, 'table_with_formatted_result'):
                control_ui.save_json_data(
                    file_sequence,
                    self.lexical_analyzer.result_of_analysis.return_all_lex_as_str()
                )

                # как список
                # control_ui.save_json_data(
                #     file_sequence,
                #     list(
                #         map(
                #             lambda x: x[2], self.lexical_analyzer.result_of_analysis.table_with_formatted_result
                #         )
                #     )
                # )

                control_ui.save_json_data(
                    file_handler,
                    self.lexical_analyzer.return_copy_of_join_tables_of_handler()
                )

    # ------------------------------------------------------------------------------------------------------------------

    # -----------------------------------------------------GFCB_JSON----------------------------------------------------
    def update_GFCB_setted_files(self):  # ui
        if self.GFCB_json_dict and 'paths' in self.GFCB_json_dict:
            for key in self.GFCB_json_dict['paths']:
                current_path = self.GFCB_json_dict['paths'][key]
                if current_path:
                    self.get_object(key).set_file(
                        Gio.File.new_for_path(
                            universal_func.correct_path(
                                current_path
                            )
                        )
                    )

    # не хватает "относительных" путей для последующего сохранения в конфиг
    def update_dict_of_GFCB_json_data(self):
        self.GFCB_json_dict = dict()
        self.GFCB_json_dict['paths'] = {
            'GFCB_lex_select_file': universal_func.get_path_from_GFCB_url_or_none(
                self.get_object('GFCB_lex_select_file')
            ),

            'GFCB_out_lex_select_file_1': universal_func.get_path_from_GFCB_url_or_none(
                self.get_object('GFCB_out_lex_select_file_1')
            ),

            'GFCB_table_of_lex_select_file': universal_func.get_path_from_GFCB_url_or_none(
                self.get_object('GFCB_table_of_lex_select_file')
            ),

            'GFCB_out_lex_select_file_2': universal_func.get_path_from_GFCB_url_or_none(
                self.get_object('GFCB_out_lex_select_file_2')
            )
        }
        # print(self.GFCB_json_dict)
        return self.GFCB_json_dict

    # ------------------------------------------------------------------------------------------------------------------

    # ------------------------------------------------------GTreeV------------------------------------------------------
    # https://python--gtk--3--tutorial-readthedocs-io.translate.goog/en/latest/treeview.html?_x_tr_sl=auto&_x_tr_tl=ru&_x_tr_hl=ru
    # self.clear_GTreeV_table_of_lex(self.get_object('GLS_list_for_table_of_lex'))
    def clear_GTreeV_table_of_lex(self, GLS, add_empty_line=False):
        GLS.clear()
        if add_empty_line:
            GLS.append(['', '', '', ''])
    # ------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    ui_from_file = ui('ui.glade', 'Main_Window', GFCB_json_file='data/GFCB_configs.json')
