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

        '?': 'Другие лексемы',
    }

    def __init__(self, class_code: str, lex_id: int=-1, text: str='', order: int=-1, linen: int=0, charn: int=0, slinen: int=0, scharn: int=0):
        if class_code not in Lexem.LEXEM_CLASSES.keys():
            raise ValueError('Неподходящий код класса лексемы')

        self.class_code = class_code
        self.lex_id = lex_id
        self.text = text
        self.order = order
        self.linen = linen
        self.charn = charn
        self.slinen = slinen
        self.scharn = scharn

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

        'OLC',      # OLC - One-Line Comment state - Статус однострочного комментария
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

    IMPLICIT_SEPARATORS = list(set(list(TABLE_SEPARATORS.keys()) + list(map(lambda x: x[0], TABLE_OPERATIONS.keys())) + list(EXCEPT_CHARS)))

    def __init__(self, program_filename: str):
        self.program_filename = program_filename
        self._current_state = 'S'
        self.current_state_verbose = ''

        self._lex_count = 0

        self._start_linen = 0
        self._current_linen = 0
        self._current_line = CharQueue()

        self._start_сharn = 0
        self._current_сharn = 0
        self._current_char = ''

        self._buffer = CharStack()
        self.__ALL_registry = []

        self._analysed_lines = CharQueue()
        with open(self.program_filename, 'rt', encoding='utf-8') as f:
            for line in f:
                self._analysed_lines.add(line)

    @property
    def current_state(self):
        return self._current_state

    @current_state.setter
    def current_state(self, value):
        state_verbose = ''
        if isinstance(value, (tuple, list)):
            state_verbose = value[1]
            value = value[0]

        if value not in self.STATES:
            raise ValueError('Статус не из списка допустимых')

        self.current_state_verbose = state_verbose
        self._current_state = value

    @property
    def current_char(self):
        return self._current_char

    @current_char.setter
    def current_char(self, value):
        self._current_char = value
        self._current_сharn += 1

    def add_buff(self, state=None, item=None, preclean=False):
        if not item:
            item = self._current_char
        if self._buffer.is_empty and item in self.EXCEPT_CHARS:
            return
        if preclean:
            self.clear_buff(state)
        if state:
            self.current_state = state
        if item:
            self._buffer.add(item)

    def clear_buff(self, state=None):
        if state:
            self.current_state = state

        self._start_linen = self._current_linen
        self._start_сharn = self._current_сharn

        self._buffer.clear()

    def read_buff(self, top=False):
        if top:
            return self._buffer.top()
        return self._buffer.read()

    @property
    def is_buff_empty(self):
        return self._buffer.is_empty

    @property
    def ALL_registry(self):
        return self.__ALL_registry

    @ALL_registry.setter
    def ALL_registry(self, value):
        self.__ALL_registry = value

    W_registry = property(lambda s: [x for x in s.ALL_registry if x.class_code == 'W'])
    N_registry = property(lambda s: [x for x in s.ALL_registry if x.class_code == 'N'])
    C_registry = property(lambda s: [x for x in s.ALL_registry if x.class_code == 'C'])

    def add_lexem(self, lexem: Lexem):
        self._lex_count += 1

        if not lexem.text:
            lexem.text = self.current_char

        if lexem.linen == 0:
            lexem.linen = self._current_linen

        if lexem.charn == 0:
            lexem.charn = self._current_сharn

        if lexem.slinen == 0:
            lexem.slinen = self._start_linen

        if lexem.scharn == 0:
            lexem.scharn = self._start_сharn

        if lexem.order == -1:
            lexem.order = self._lex_count

        if lexem.lex_id <= 0 and lexem.text:
            lex_id = ''

            if lexem.class_code == "W":
                lex_id = self.TABLE_SPEC_WORDS.get(lexem.text, 0)

            elif lexem.class_code == "O":
                lex_id = self.TABLE_OPERATIONS.get(lexem.text, 0)

            elif lexem.class_code == "R":
                lex_id = self.TABLE_SEPARATORS.get(lexem.text, 0)

            lexem.lex_id = lex_id

        self.ALL_registry.append(lexem)

    def get_table_rows_cols(self) -> list:
        th = '''| №     |             Текст лексемы            |  Код  |       Описание лексемы      |  Строка:Символ |'''
        twidth = len(th)
        thds = th.split('|')
        thds = list(filter(lambda x: x != '', thds))

        n_charbuf = len(thds[0]) - 1
        text_charbuf = len(thds[1]) - 1
        code_charbuf = len(thds[2]) - 1
        desc_charbuf = len(thds[3]) - 1
        linechar_charbuf = len(thds[4]) - 1

        def get_row(n='', text='', code='', desc='', linechar=''):
            n_ = f"{n:>{n_charbuf}} "

            if text.count('-') != text_charbuf:
                text = text[:(text_charbuf - 5)].replace('\n', '\\n')

            text_ = f"{text:>{text_charbuf}} "
            code_ = f"{code:>{code_charbuf}} "
            desc_ = f"{desc:>{desc_charbuf}} "
            linechar_ = f"{linechar:>{linechar_charbuf}} "

            return '|' + '|'.join([n_, text_, code_, desc_, linechar_]) + '|'

        ret_list = ['=' * twidth,
                    th,
                    '=' * twidth,
                    ]
        for x in self.ALL_registry:
            lenes = f'{x.linen}:{x.charn}'
            if (x.slinen or x.scharn) and not (x.linen == x.slinen and x.charn == x.scharn):
                lenes = f'{x.slinen}:{x.scharn}' + '-' + lenes

            ret_list.append(get_row(x.order, x.text, x.fcode, x.fdesc, lenes))
            ret_list.append(get_row('-' * n_charbuf, '-' * text_charbuf, '-' * code_charbuf, '-' * desc_charbuf, '-' * linechar_charbuf))

        return ret_list

    def __str__(self):

        if not self.current_state == 'F':
            return '\n'.join(self.get_table_rows_cols())

        return f'Ошибка парсера (строка {self._current_linen}, символ {self._current_сharn}): {self.current_state_verbose}'

    def run_analysis(self):
        """
        Начать анализ. Заполнить таблицы лексем.
        """

        # Цикл парсинга строк программы
        while not self._analysed_lines.is_empty or not self._current_line.is_empty:

            # Парсер вернул ошибку
            if self.current_state == 'F':
                break

            # Парсер чистит буфер за строку если не парсим многострочный комментарий
            if self.current_state != 'MLC':
                self.clear_buff()

            self._current_line = CharQueue(self._analysed_lines.pop())
            self._current_linen += 1

            self._current_сharn = 0
            self.current_char = self._current_line.pop()
            self.add_buff()

            # Цикл парсинга символов в строке
            full_loop_iter = True  # Произошла ли полная итерация
            ret_or_add_chars_to_buff = False  # Вернуть в буфер считанные дополнительные символы или взять новый символ
            next_chars = []  # Дополнительные символы считанные из строки но пока не добавленные в буфер
            while (self.current_char or not self.is_buff_empty) and not self._current_line.is_empty:

                # Заполним буфер если был continue переход
                if ret_or_add_chars_to_buff:
                    if not len(next_chars):  # Берем следующий символ из буфера
                        self.current_char = self._current_line.pop()
                        self.add_buff()
                    else:  # Возвращаем в буфер прочитанные в итерации символы если они есть
                        for nc in next_chars:
                            self.current_char = nc
                            self.add_buff()

                elif not full_loop_iter:  # Если оптимизационный continue случился - берем следующий символ в начале петли, иначе он берется в конце петли
                    self.current_char = self._current_line.pop()
                    self.add_buff()

                ret_or_add_chars_to_buff = False
                next_chars = []
                full_loop_iter = False
                # / Заполним буфер если был continue переход

                #-----------------------------------------
                #-----------------------------------------
                #-----------------------------------------

                # print(self.read_buff())
                # print("=======")

                # Не анализируем символы
                if self.current_char in self.EXCEPT_CHARS and self.current_state not in ('LETT', 'IDENT', 'INT', 'REAL', 'MCOP', ):
                    continue

                # Состояние когда окончены предыдущие парсинги лексем
                elif self.current_state == 'S':

                    # Установка стартовой позиции между успешными лексемами
                    self._start_linen = self._current_linen
                    self._start_сharn = self._current_сharn or 1

                    # Инклюд
                    if self.current_char == '#':
                        next_chars.extend(x for x in self._current_line if x != '\n')
                        self._current_сharn += len(next_chars)
                        self.add_lexem(Lexem('?', text=self.current_char + ''.join(next_chars)))
                        self.clear_buff('S')
                        continue  # Однозначаное определение лексемы

                    # Многострочный комментарий, Однострочный комментарий, иное (операция деления)
                    elif self.current_char == '/':

                        next_chars.append(self._current_line.pop())
                        self._current_сharn += len(next_chars)

                        if next_chars[-1] == '*':  # Многострочный комментарий
                            self.add_buff('MLC', next_chars[-1])
                            continue

                        elif next_chars[-1] == '/':  # Однострочный комментарий
                            self.add_buff('OLC', next_chars[-1])
                            full_loop_iter = True
                            continue

                        else:  # Операция деления
                            self.add_lexem(Lexem('O', text='/'))
                            self.add_buff('S', next_chars[-1], preclean=True)
                            continue  # Однозначаное определение лексемы

                    elif self.current_char == "'" or self.current_char == '"':
                        next_chars.append(self._current_line.pop())
                        self._current_сharn += len(next_chars)

                        if self.current_char == next_chars[-1]:
                            self.add_lexem(Lexem('C', text=self.current_char + next_chars[-1]))
                            self.clear_buff('S')
                            continue  # Однозначаное определение лексемы
                        else:
                            self.add_buff('CHAR', next_chars[-1])
                            continue

                    elif self.current_char in map(lambda x: x[0], self.MULTY_CHAR_OPERATIONS.keys()):
                        self.current_state = 'MCOP'
                        continue

                    elif self.current_char in self.SINGLE_CHAR_OPERATIONS:
                        self.add_lexem(Lexem('O'))
                        self.clear_buff('S')
                        continue  # Однозначаное определение лексемы

                    elif self.current_char in self.TABLE_SEPARATORS:
                        self.add_lexem(Lexem('R'))
                        self.clear_buff('S')
                        continue  # Однозначаное определение лексемы

                    elif self.current_char.isalpha():
                        self.current_state = 'LETT'
                        continue

                    elif self.current_char.isdigit():
                        self.clear_buff('INT')
                        self.add_buff()
                        continue

                    elif self.current_char == '.':
                        self.clear_buff('REAL')
                        self.add_buff()
                        continue

                    elif self.current_char == '_':
                        self.clear_buff('IDENT')
                        self.add_buff()
                        continue

                    else:
                        self.current_state = 'F'
                        break  # Переход на следующую строку и выход

                # Состояние когда идет анализ какойто лексемы
                else:

                    if self.current_state == 'MLC':

                        if self.current_char == '*':  # Многострочный комментарий, Закрывающая звездочка
                            next_chars.append(self._current_line.pop())
                            self._current_сharn += len(next_chars)

                            if next_chars[-1] == '/':  # Многострочный комментарий, Закрывающий слеш
                                self.add_buff(item=next_chars[-1])
                                self.add_lexem(Lexem('?', text=self.read_buff()))
                                self.clear_buff('S')
                                continue   # Однозначаное определение лексемы

                    if self.current_state == 'OLC':

                        next_chars.append(self._current_line.pop())

                        if not next_chars[-1] or next_chars[-1] == '\n':  # строчный комментарий
                            self.add_lexem(Lexem('?', text=self.read_buff()))
                            self.clear_buff('S')
                            continue

                        ret_or_add_chars_to_buff = True
                        continue

                    elif self.current_state == 'LETT' or self.current_state == 'IDENT':

                        if self.current_char.isdigit() or self.current_char == '_':
                            self.current_state = 'IDENT'
                            continue

                        elif self.current_char != ' ' and self.current_char.isalpha():
                            continue

                        elif self.current_char in self.IMPLICIT_SEPARATORS:

                            stripchars = ''.join(self.IMPLICIT_SEPARATORS)
                            scharn = self._start_сharn
                            buff = self.read_buff()
                            bunocu = buff.lstrip(stripchars)
                            bunocu_ = bunocu.rstrip(stripchars)
                            charn = scharn + len(bunocu_) - 1
                            bunocu = bunocu_

                            if self.current_state == 'LETT':
                                if bunocu in self.TABLE_SPEC_WORDS:
                                    self.add_lexem(Lexem('W', text=bunocu, charn=charn, scharn=scharn))
                                    self.add_buff('S', self.current_char, preclean=True)
                                    full_loop_iter = True
                                    continue  # Однозначаное определение лексемы

                                else:
                                    self.add_lexem(Lexem('I', text=bunocu, charn=charn, scharn=scharn))
                                    self.add_buff('S', self.current_char, preclean=True)
                                    full_loop_iter = True
                                    continue  # Однозначаное определение лексемы

                            self.add_buff('S', self.current_char, preclean=True)
                            full_loop_iter = True
                            continue

                    elif self.current_state == 'INT' or self.current_state == 'REAL':

                        if self.current_char.isdigit():
                            continue

                        elif self.current_char == '.' and self.current_state == 'INT':
                            self.current_state = 'REAL'
                            continue

                        elif self.current_char in self.IMPLICIT_SEPARATORS:

                            stripchars = ''.join(self.IMPLICIT_SEPARATORS)
                            scharn = self._start_сharn
                            buff = self.read_buff()
                            bunocu = buff.lstrip(stripchars)
                            bunocu_ = bunocu.rstrip(stripchars)
                            charn = scharn + len(bunocu_) - 1
                            bunocu = bunocu_

                            self.add_lexem(Lexem('N', text=bunocu, charn=charn, scharn=scharn))
                            self.add_buff('S', self.current_char, preclean=True)
                            full_loop_iter = True
                            continue  # Однозначаное определение лексемы

                        else:
                            self.clear_buff(('F', f"Символ {self.current_char} не может быть "
                                                  f"лексемой в данном контексте "
                                                  f"({self.current_state})"))
                            break  # Переход на следующую строку и выход

                    elif self.current_state == 'CHAR':
                        buff = self.read_buff()
                        firstchar = buff.lstrip()[0]

                        if self.current_char == '\\':
                            next_chars.append(self._current_line.pop())
                            self._current_сharn += len(next_chars)

                            if next_chars[-1] == '\n':
                                self.clear_buff('S')
                                break  # Переход на следующую строку

                            ret_or_add_chars_to_buff = True
                            continue

                        elif (self._analysed_lines.is_empty and self._current_line.is_empty and \
                              not self.current_char) or self.current_char == '\n':
                            self.clear_buff(('F', f"Обрыв строки посередине строковой константы: {self.read_buff()}"))
                            break  # Переход на следующую строку и выход

                        elif self.current_char == firstchar:
                            self.add_lexem(Lexem('C', text=self.read_buff()))
                            self.clear_buff('S')
                            continue  # Однозначаное определение лексемы

                    elif self.current_state == 'MCOP':

                        if self.current_char == ' ' or self.current_char in self.IMPLICIT_SEPARATORS:

                            stripchars = ' ' + ''.join(self.TABLE_SEPARATORS.keys()) + ''.join(self.EXCEPT_CHARS)
                            scharn = self._start_сharn
                            buff = self.read_buff()
                            full_op = buff.lstrip(stripchars)
                            bunocu_ = full_op.rstrip(stripchars)
                            charn = scharn + len(bunocu_) - 1

                            full_op = bunocu_
                            oneop = full_op[0]

                            if full_op in self.MULTY_CHAR_OPERATIONS:
                                self.add_lexem(Lexem('O', text=full_op, scharn=scharn, charn=charn))
                                self.clear_buff('S')
                                continue  # Однозначаное определение лексемы

                            elif oneop in self.SINGLE_CHAR_OPERATIONS and self.current_char not in self.SINGLE_CHAR_OPERATIONS:
                                self.add_lexem(Lexem('O', text=oneop, charn=scharn, scharn=scharn))
                                self.add_buff('S', self.current_char, preclean=True)
                                full_loop_iter = True
                                continue  # Однозначаное определение лексемы

                            else:  # Не многолитерная не однолитерная
                                self.clear_buff(('F', f"оператор {full_op} не является оператором!"))
                                break  # Переход на следующую строку

                        else:  # Не многолитерная не однолитерная
                            self.clear_buff(('F', f"{self.read_buff()} не является оператором!"))
                            break  # Переход на следующую строку

                    pass

                #-----------------------------------------
                #-----------------------------------------
                #-----------------------------------------

                # Заполним буфер поумолчанию
                if ret_or_add_chars_to_buff:
                    if not len(next_chars):  # Берем следующий символ из буфера
                        self.current_char = self._current_line.pop()
                        self.add_buff()
                    else:  # Возвращаем в буфер прочитанные в итерации символы если они есть
                        for nc in next_chars:
                            self.current_char = nc
                            self.add_buff()
                else:  # Берем следующий символ из буфера
                    self.current_char = self._current_line.pop()
                    self.add_buff()

                ret_or_add_chars_to_buff = False
                next_chars = []
                # / Заполним буфер поумолчанию

                full_loop_iter = True

        pass


if __name__ == "__main__":

    anali = LexicalAnalyzerC(r'input_code.c')

    anali.run_analysis()

    print(anali)

    pass
