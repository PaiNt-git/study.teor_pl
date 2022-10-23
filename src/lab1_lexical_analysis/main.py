'''
Created on 15 сент. 2022 г.

@author: ASZabavin
'''

from shared_classes import CharStack, CharQueue


class Lexem:
    LEXEM_CLASSES = {
        'W': 'Служебные слова',
        'I': 'Идентификаторы',
        'O': 'Операции',
        'R': 'Разделители',
        'N': 'Константы числовые',
        'C': 'Константы символьные',
    }

    def __init__(self, class_code: str, lex_id: int, text: str='', order: int=-1):
        if class_code not in Lexem.LEXEM_CLASSES.keys():
            raise ValueError('Неподходящий код класса лексемы')

        self.class_code = class_code
        self.lex_id = lex_id
        self.text = text
        self.order = order

    @property
    def fcode(self):
        return f'{self.class_code}{self.lex_id}'

    @property
    def fdesc(self):
        return f'{Lexem.LEXEM_CLASSES[self.class_code]}'

    def __repr__(self):
        clsname = self.__class__.__name__
        return f'<{clsname}: {self.fcode}>'

    def __str__(self):
        return f'"{self.text}" ({self.fcode}: {self.fdesc})'


class LexicalAnalyzerC:

    STATES = [
        'S',    # S - Start state - Начальный статус по умолчанию
        'Z',    # Z - sucsess end state - Статус успешного завершения
        'F',    # F - Fail (error) state - Статус ошибки

        'MLC',      # MLC - Multi-Line Comment state - Статус многострочного комментария

        'MCOP',     # MCOP - Multi-Char OPerators - Статус многосимвольного оператора
        'LETT',     # LETT - LETTers state - Статус букв, которые могут быть как идентификаторами переменных так и служебными словами
        'IDENT',    # IDENT - IDENTifiers state - Статус идентификаторов переменных
        'INT',      # INT - INTeger state - Статус целых чисел
        'REAL',     # REAL - REAL (float) state - Статус вещественных чисел
        'CHAR',     # CHAR - CHAR constants state - Статус строковых констант
    ]

    EXCEPT_CHARS = (' ', '\n', '\t', '')

    TABLE_SPEC_WORDS = {
        'char': 0,
        'double': 1,
        'float': 2,
        'int': 3,
        'string': 4,
        'const': 5,
        'long': 6,
        'short': 7,
        'signed': 8,
        'unsigned': 9,
        'void': 10,
        'auto': 11,
        'if': 12,
        'else': 13,
        'case': 14,
        'switch': 15,
        'for': 16,
        'while': 17,
        'do': 18,
        'break': 19,
        'continue': 20,
        'return': 21,
        'goto': 22,
        'using': 23,
        'namespace': 24,
    }

    TABLE_SEPARATORS = {

        '(': 0,
        ')': 1,
        ';': 2,
        '[': 3,
        ']': 4,
        '{': 5,
        '}': 6,
        ',': 7,

    }

    TABLE_OPERATIONS = {

        '+': 0,
        '++': 1,
        '-': 2,
        '--': 3,
        '*': 4,
        '**': 5,
        '^': 6,
        '/': 7,
        '%': 8,
        '==': 9,
        '!=': 10,
        '<': 11,
        '>': 12,
        '<=': 13,
        '>=': 14,
        '&': 15,
        '&&': 16,
        '||': 17,
        '!': 18,
        '<<': 19,
        '>>': 20,
        ':': 21,
        '=': 22,

    }
    SINGLE_CHAR_OPERATIONS = {k: v for k, v in TABLE_OPERATIONS.items() if len(k) == 1}
    MULTY_CHAR_OPERATIONS = {k: v for k, v in TABLE_OPERATIONS.items() if len(k) > 1}

    def __init__(self, program_filename: str):
        self.program_filename = program_filename
        self._current_state = 'S'
        self._current_char = ''
        self._current_linen = 0
        self._current_сharn = 0

        self.__buffer = CharStack()
        self.__ALL_registry = []

        self._analysed_lines = CharQueue()
        with open(self.program_filename, 'rt', encoding='utf-8') as f:
            for line in f:
                self._analysed_lines.add(line)

        self._current_line = CharQueue()

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def _current_state(self, value):
        if value not in self.STATES:
            raise ValueError('Статус не из списка допустимых')
        self._current_state = value

    @property
    def ALL_registry(self):
        return self.__ALL_registry

    @ALL_registry.setter
    def _ALL_registry(self, value):
        self.__ALL_registry = value

    W_registry = property(lambda s: [x for x in s.ALL_registry if x.class_code == 'W'])
    N_registry = property(lambda s: [x for x in s.ALL_registry if x.class_code == 'N'])
    C_registry = property(lambda s: [x for x in s.ALL_registry if x.class_code == 'C'])

    def add_lexem(self, lexem: Lexem):
        self.ALL_registry.append(lexem)

    def clear_lexems(self):
        self.ALL_registry = []

    def get_table_rows_cols(self) -> list:
        th = '''| №       |           Текст лексемы              |   Код Лексемы   |         Описание лексемы         |'''
        twidth = len(th)
        thds = th.split('|')
        thds = list(filter(lambda x: x != '', thds))

        n_charbuf = len(thds[0]) - 1
        text_charbuf = len(thds[1]) - 1
        code_charbuf = len(thds[2]) - 1
        desc_charbuf = len(thds[3]) - 1

        def get_row(n='', text='', code='', desc=''):
            n_ = f"{n:>{n_charbuf}} "
            text_ = f"{text:>{text_charbuf}} "
            code_ = f"{code:>{code_charbuf}} "
            desc_ = f"{desc:>{desc_charbuf}} "

            return '|' + '|'.join([n_, text_, code_, desc_]) + '|'

        ret_list = ['=' * twidth,
                    th,
                    '=' * twidth,
                    ]
        for x in self.ALL_registry:
            ret_list.append(get_row(x.order, x.text, x.fcode, x.fdesc))
            ret_list.append(get_row('-' * n_charbuf, '-' * text_charbuf, '-' * code_charbuf, '-' * desc_charbuf))

        return ret_list

    def __str__(self):
        return '\n'.join(self.get_table_rows_cols())

    def add_buff(self, item, state=None):
        if state:
            self.current_state = state

        self.__buffer.add(item)

    def clear_buff(self, state=None):
        if state:
            self.current_state = state

        self.__buffer.clear()

    def read_buff(self, top=False, bottom=False):
        if top:
            return self.__buffer.top()
        if bottom:
            return self.__buffer.bottom()

        self.__buffer.read()

    @property
    def is_buff_empty(self):
        return self.__buffer.is_empty

    def run_analysis(self):
        """
        Начать анализ. Заполнить таблицы лексем.
        """

        while not self._analysed_lines.is_empty() or not self._current_line.is_empty():

            if self.current_state == 'F':
                break

            self._current_line = CharQueue(self._analysed_lines.pop())
            self._current_linen += 1

            self._current_сharn = 0
            self._current_char = self._current_line.pop()
            self._current_сharn += 1

            while self._current_char or not self.is_buff_empty:
                if self.current_state == 'S':

                    if self._current_char in self.EXCEPT_CHARS:
                        pass

                    elif self._current_char == '#':
                        break

                    elif self._current_char == '/':
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

                    elif self._current_char.isalpha():
                        self.change_status_and_add_symbol_to_buffer('letters')

                    elif self._current_char == '_':
                        self.change_status_and_add_symbol_to_buffer('identifiers')

                    elif self._current_char.isdigit():
                        self.change_status_and_add_symbol_to_buffer('integer_numbers')

                    elif self._current_char == '.':
                        self.change_status_and_add_symbol_to_buffer('real_numbers')

                    elif self._current_char == "'" or self._current_char == '"':
                        self.__stop_litter_for_character_constants = self.__current_chapter
                        self.override_status_and_or_message('character_constants',
                                                            True,
                                                            'Символьная константа не имеет закрывающей кавычки!')

                    elif self._current_char in self.MULTY_CHAR_OPERATIONS:
                        self.change_status_and_add_symbol_to_buffer('two_litters_operations')

                    elif self._current_char in self.SINGLE_CHAR_OPERATIONS:  # ['/', '^', ':', '%']
                        self.decide_what_to_do_with_lex('operations', self.__current_chapter)

                    elif self._current_char in self.TABLE_SEPARATORS:
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

        pass


if __name__ == "__main__":

    anal = LexicalAnalyzerC(r'M:\home\git\\magistry2022\study.teor_pl\src\test_gtk_artem\lab_1\data\input_code.c')

    sss = CharStack([1, 2, 3])

    sss.add(10)
    sss.add(20)
    sss.add(30)
    sss.add(40)

    for elem in sss:
        print(elem)

    print("====")

    qqq = CharQueue([1, 2, 3])

    qqq.add(100)
    qqq.add(200)
    qqq.add(300)
    qqq.add(400)

    for elem in qqq:
        print(elem)

    pass
