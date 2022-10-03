r"""
Описание
"""

# теневая (т.е. объекты внутри объекта - ссылки; сам объект - другой)
# глубокая (объект и подобъекты - новые значения)
from copy import copy, deepcopy


class handler_of_syntax_of_analyzer:
    def __init__(self, support_for_two_character_operations=True):

        self.abbreviations = {
            'functional_words': ('W', 'Служебные слова'),
            'operations': ('O', 'Операции'),
            'separators': ('R', 'Разделители'),
            'identifiers': ('I', 'Идентификаторы'),
            'character_constants': ('C', 'Символьные константы'),
            'numeric_constants': ('N', 'Числовые константы')
        }

        self.mutable_tables_of_lex = {
            'identifiers': [],
            'character_constants': [],
            'numeric_constants': []
        }

        self.const_tables_of_lex = {
            'functional_words': ('char', 'double', 'float', 'int', 'string',
                                 'const', 'long', 'short', 'signed', 'unsigned',
                                 'void', 'auto',
                                 'if', 'else', 'case', 'switch',
                                 'for', 'while', 'do', 'break', 'continue',
                                 'return', 'goto', 'using', 'namespace'),
            # по идеи не хватает, допустим, операторов --> или .
            # но задача учебная и не преследует цель написания полноценного
            # лексического анализатора
            'operations': ('+', '++', '-', '--', '*', '**', '^', '/', '%',
                           '==', '!=', '<', '>', '<=', '>=', '&',
                           '&&', '||', '!', '<<', '>>', ':', '='),


            'separators': ('(', ')', ';', '[', ']', '{', '}', ',')
        }

        self.is_letters = lambda x: x.isalpha()  # в строке только буквы?!
        self.is_digits = lambda x: str(x).isdigit()  # в строке только цифры?!
        self.is_separators = lambda x: x in self.const_tables_of_lex['separators']
        self.is_skip_separators = lambda x: x in (' ', '\n', '\t', '')
        self.is_operations = lambda x: x in self.const_tables_of_lex['operations']

        if support_for_two_character_operations:
            table_two_litters_operations = []
            for x in self.const_tables_of_lex['operations']:
                if len(x) == 2:
                    table_two_litters_operations.append(x)
            table_of_start_two_litters_operations = list(map(lambda x: x[0], table_two_litters_operations))

            # уникальные однолитерки
            table_only_one_litters_operations = \
                (
                    set(self.const_tables_of_lex['operations']) -
                    set(table_two_litters_operations)
                ) - set(table_of_start_two_litters_operations)

            self.const_tables_of_lex['only_one_litters_operations'] = list(table_only_one_litters_operations)
            self.const_tables_of_lex['two_litters_operations'] = table_two_litters_operations
            self.const_tables_of_lex['start_two_litters_operations'] = table_of_start_two_litters_operations

            self.is_only_one_litters_operations = lambda x: x in self.const_tables_of_lex[
                'only_one_litters_operations']
            self.is_in_two_litters_operations = lambda x: x in self.const_tables_of_lex[
                'start_two_litters_operations']
            self.is_two_litters_operations = lambda x: x in self.const_tables_of_lex['two_litters_operations']


class lex:
    def __init__(self, full_lex: str, PL_code: str, class_of_lex: str):
        self.full_lex = full_lex

        self.code_name = self.full_lex[0]
        self.id = self.full_lex[1:]

        self.PL_code = PL_code  # if, int, etc...
        self.class_of_lex = class_of_lex  # Разделители, Идентификатора, etc...

    def return_as_list(self):
        return self.code_name, self.id


class keeper_of_analysis_result:
    def __init__(self):
        self.result_of_analysis = []
        self.table_with_formatted_result = []
        # self.current_status

    def add(self, new_lex, PL_code: str, class_of_lex: str):  # W51
        if not isinstance(new_lex, lex):  # если это не класс, а строка
            new_lex = lex(new_lex, PL_code, class_of_lex)  # создать класс
        self.result_of_analysis.append(new_lex)

    def return_all_lex_as_list(self):
        return list(map(lambda x: x.full_lex, self.result_of_analysis))

    def return_all_lex_as_str(self, separator=' '):
        return separator.join(self.return_all_lex_as_list())

    def show_last_lex(self):
        if self.result_of_analysis:
            return self.result_of_analysis[-1:]
        else:
            return None

    def get_result_as_formatted_list(self):
        self.table_with_formatted_result = []
        num = -1
        for lex in self.result_of_analysis:
            num += 1
            self.table_with_formatted_result.append([str(num), lex.PL_code, lex.full_lex, lex.class_of_lex])
        return self.table_with_formatted_result


class status:
    def __init__(self, ID=str(), with_message=str()):
        self.ID = ID
        self.message = with_message


class extended_stack_or_queue:
    def __init__(self, list_to_put_in_stack_or_queue=None, is_stack=False):
        self.items = []

        self.is_stack = is_stack

        if self.is_stack:
            self.add = lambda x: self.items.append(x)
            self.show_all_as_str = lambda: ''.join(self.items)
        else:  # queue
            self.add = lambda x: self.items.insert(0, x)
            self.show_all_as_str = lambda: ''.join(reversed(self.items))

        if list_to_put_in_stack_or_queue is None:
            list_to_put_in_stack_or_queue = []
        else:
            for value in list_to_put_in_stack_or_queue:
                self.add(value)

    def is_empty(self):
        if self.items:
            return False
        return True

    def pop(self):
        if self.is_empty():
            return ''
        else:
            return self.items.pop()

    def clear(self):
        self.items = []

    def len(self):
        return len(self.items)


class lexical_analyzer:
    def __init__(self, data_for_analysis: "list of str"):
        self.raw_code = extended_stack_or_queue(data_for_analysis, is_stack=False)
        self.__syntax = handler_of_syntax_of_analyzer()
        self.__buffer = extended_stack_or_queue(is_stack=True)
        self.result_of_analysis = keeper_of_analysis_result()

        self.__current_status = status(ID='start')
        self.__current_line = extended_stack_or_queue(is_stack=False)
        self.__current_line_num = 0
        self.__current_amount_of_lines_remaining = int()
        self.__current_chapter = str()

        # что является начальным символом при обработке символьных констант (' или ")
        self.__stop_litter_for_character_constants = None

        # print(f"На вход поступили строки: {data_for_analysis}")

    def change_status_and_add_symbol_to_buffer(self, new_status: str):
        self.override_status_and_or_message(new_status)
        self.__buffer.add(self.__current_chapter)

    def override_status_and_or_message(self, status=None, line_in_message=True, message=None, clear_message=True):
        if status:
            self.__current_status.ID = status
            if clear_message:
                self.__current_status.message = str()

        if line_in_message:
            line_in_message = f"[{self.__current_line_num}] "

        if message:
            self.__current_status.message = line_in_message + message

    def decide_what_to_do_with_lex(self, name_of_table: str, item=None):
        switch_to_dynamic_table = False
        code_of_lex = ''  # чтоб PyCharm не ругался, потом - удали

        if not item:  # не знаем точно, с какой лексемой работаем
            item = self.__buffer.show_all_as_str()

        if name_of_table in self.__syntax.const_tables_of_lex:
            if item in self.__syntax.const_tables_of_lex[name_of_table]:
                code_of_lex = self.__syntax.abbreviations[name_of_table][0] + \
                    str(self.__syntax.const_tables_of_lex[name_of_table].index(item))
            else:
                if name_of_table == 'functional_words':
                    name_of_table = 'identifiers'
                    switch_to_dynamic_table = True
                elif name_of_table == 'operations':  # двулитерки не обнаружено (однолитерка)
                    return 'is_not_two_litters_operations'
        else:
            switch_to_dynamic_table = True

        if switch_to_dynamic_table:
            if item in self.__syntax.mutable_tables_of_lex[name_of_table] and name_of_table == 'identifiers':
                code_of_lex = self.__syntax.abbreviations[name_of_table][0] + \
                    str(self.__syntax.mutable_tables_of_lex[name_of_table].index(item))
            else:
                code_of_lex = self.__syntax.abbreviations[name_of_table][0] + \
                    str(len(self.__syntax.mutable_tables_of_lex[name_of_table]))
                self.__syntax.mutable_tables_of_lex[name_of_table].append(item)

        self.result_of_analysis.add(code_of_lex, PL_code=item,
                                    class_of_lex=self.__syntax.abbreviations[name_of_table][1])
        self.__buffer.clear()
        self.override_status_and_or_message('start')
        return

    def run_analysis(self):

        while not self.raw_code.is_empty() or not self.__current_line.is_empty():

            if self.__current_status.ID == 'error':
                break

            self.__current_line = extended_stack_or_queue(self.raw_code.pop(), is_stack=False)
            self.__current_chapter = self.__current_line.pop()
            self.__current_line_num += 1

            while self.__current_chapter or not self.__buffer.is_empty():
                if self.__current_status.ID == 'start':

                    if self.__syntax.is_skip_separators(self.__current_chapter):
                        pass

                    elif self.__current_chapter == '#':
                        break

                    elif self.__current_chapter == '/':
                        next_chapter = self.__current_line.pop()
                        if next_chapter == '*':
                            # self.__current_status.ID = 'multiline_comment'
                            # заранее определяемся с возможной ошибкой
                            self.override_status_and_or_message('multiline_comment', True, 'unterminated comment')
                        elif next_chapter == '/':
                            break
                        else:
                            # добавить /
                            self.decide_what_to_do_with_lex('operations', '/')
                            self.__current_chapter = next_chapter
                            continue

                    elif self.__syntax.is_letters(self.__current_chapter):
                        self.change_status_and_add_symbol_to_buffer('letters')

                    elif self.__current_chapter == '_':
                        self.change_status_and_add_symbol_to_buffer('identifiers')

                    elif self.__syntax.is_digits(self.__current_chapter):
                        self.change_status_and_add_symbol_to_buffer('integer_numbers')

                    elif self.__current_chapter == '.':
                        self.change_status_and_add_symbol_to_buffer('real_numbers')

                    elif self.__current_chapter == "'" or self.__current_chapter == '"':
                        self.__stop_litter_for_character_constants = self.__current_chapter
                        self.override_status_and_or_message('character_constants',
                                                            True,
                                                            'Символьная константа не имеет закрывающей кавычки!')

                    elif self.__syntax.is_in_two_litters_operations(self.__current_chapter):
                        self.change_status_and_add_symbol_to_buffer('two_litters_operations')

                    elif self.__syntax.is_only_one_litters_operations(self.__current_chapter):  # ['/', '^', ':', '%']
                        self.decide_what_to_do_with_lex('operations', self.__current_chapter)

                    elif self.__syntax.is_separators(self.__current_chapter):
                        self.decide_what_to_do_with_lex('separators', self.__current_chapter)

                    else:
                        self.override_status_and_or_message('error', True,
                                                            f"Символ {repr(self.__current_chapter)} не может быть "
                                                            f"лексемой в данном контексте ({self.__current_status.ID})")
                        break

                else:

                    if self.__current_status.ID == 'multiline_comment':
                        if self.__current_chapter == '*':
                            next_chapter = self.__current_line.pop()
                            if next_chapter == '/':
                                self.override_status_and_or_message('start')

                    elif self.__current_status.ID == 'letters' or self.__current_status.ID == 'identifiers':
                        if self.__syntax.is_digits(self.__current_chapter) or self.__current_chapter == '_':
                            self.change_status_and_add_symbol_to_buffer('identifiers')
                        elif self.__syntax.is_letters(self.__current_chapter):
                            self.__buffer.add(self.__current_chapter)
                        elif self.__syntax.is_skip_separators(self.__current_chapter) or \
                                self.__syntax.is_separators(self.__current_chapter) or \
                                self.__syntax.is_in_two_litters_operations(self.__current_chapter) or \
                                self.__syntax.is_only_one_litters_operations(self.__current_chapter):
                            if self.__current_status.ID == 'letters':
                                self.decide_what_to_do_with_lex('functional_words')
                            else:
                                self.decide_what_to_do_with_lex('identifiers')
                            continue
                        else:
                            self.override_status_and_or_message('error', True,
                                                                f"Символ {repr(self.__current_chapter)} не может быть "
                                                                f"лексемой в данном контексте "
                                                                f"({self.__current_status.ID})")
                            break

                    elif self.__current_status.ID == 'integer_numbers' or self.__current_status.ID == 'real_numbers':
                        if self.__syntax.is_digits(self.__current_chapter):
                            self.__buffer.add(self.__current_chapter)
                        elif self.__current_chapter == '.' and self.__current_status.ID == 'integer_numbers':
                            self.change_status_and_add_symbol_to_buffer('real_numbers')
                        elif self.__syntax.is_skip_separators(self.__current_chapter) or \
                                self.__syntax.is_separators(self.__current_chapter) or \
                                self.__syntax.is_in_two_litters_operations(self.__current_chapter) or \
                                self.__syntax.is_only_one_litters_operations(self.__current_chapter):
                            self.decide_what_to_do_with_lex('numeric_constants')
                            continue
                        else:
                            self.override_status_and_or_message('error', True,
                                                                f"Символ {repr(self.__current_chapter)} не может быть "
                                                                f"лексемой в данном контексте "
                                                                f"({self.__current_status.ID})")
                            break

                    elif self.__current_status.ID == 'character_constants':

                        if self.__current_chapter == '\\':
                            next_chapter = self.__current_line.pop()
                            if next_chapter == '\n':
                                break
                            elif next_chapter == 'n':
                                self.__buffer.add('\n')
                            elif next_chapter == 't':
                                self.__buffer.add('\t')
                            else:  # любой другой
                                self.__buffer.add(next_chapter)
                        elif (self.raw_code.is_empty() and self.__current_line.is_empty() and \
                              not self.__current_chapter) or self.__current_chapter == '\n':
                            self.override_status_and_or_message('error', clear_message=False)
                            self.__buffer.clear()
                            break
                        elif self.__current_chapter == self.__stop_litter_for_character_constants:
                            if self.__stop_litter_for_character_constants == '"':
                                self.decide_what_to_do_with_lex('character_constants')
                            else:  # "'"
                                item = self.__buffer.show_all_as_str()
                                if len(item) <= 1:
                                    self.decide_what_to_do_with_lex('character_constants', item)
                                else:
                                    self.decide_what_to_do_with_lex('character_constants', item[-1:])
                                    print('warning: character constant too long for its type')
                        else:
                            self.__buffer.add(self.__current_chapter)

                    elif self.__current_status.ID == 'two_litters_operations':
                        join_buffer = self.__buffer.items[0] + self.__current_chapter
                        if self.decide_what_to_do_with_lex('operations', join_buffer) == \
                                'is_not_two_litters_operations':
                            if self.__buffer.items[0] in self.__syntax.const_tables_of_lex['operations']:  # |
                                self.decide_what_to_do_with_lex('operations')
                                continue
                            else:  # не это однолитерная операция
                                self.override_status_and_or_message('error', True,
                                                                    f"{repr(self.__buffer.items[0])} или "
                                                                    f"{repr(join_buffer)} не является оператором!")
                                break

                self.__current_chapter = self.__current_line.pop()

        # print('-------------------------------')

        self.result_of_analysis.get_result_as_formatted_list()

        return self.__current_status.message

    def return_copy_of_join_tables_of_handler(self):
        join = {
            'const_tables_of_lex': self.__syntax.const_tables_of_lex,
            'mutable_tables_of_lex': self.__syntax.mutable_tables_of_lex
        }
        return deepcopy(join)
