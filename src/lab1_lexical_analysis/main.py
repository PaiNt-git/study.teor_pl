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

        self._file_data = ''
        with open(self.program_filename, 'rt', encoding='utf-8') as f:
            self._file_data = f.read()

        self._ALL_registry = []

    @property
    def ALL_registry(self):
        return self._ALL_registry

    @ALL_registry.setter
    def ALL_registry(self, value):
        self._ALL_registry = value

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

    def run_analysis(self):
        pass


if __name__ == "__main__":

    anal = LexicalAnalyzerC(r'M:\home\magistry2022\study.teor_pl\src\test_gtk\lab_1\data\input_code.c')

    anal.add_lexem(Lexem("W", 1))

    anal.add_lexem(Lexem("W", 1))

    anal.add_lexem(Lexem("W", 1))

    anal.add_lexem(Lexem("C", 1))

    sss = CharStack([1, 2, 3])

    sss.add(4)

    qqq = CharQueue([1, 2, 3])

    qqq.add(4)

    print(sss)

    print(sss.pop())
    print(sss.pop())
    print(sss.pop())

    print(qqq)

    print(qqq.pop())
    print(qqq.pop())
    print(qqq.pop())

    print("")

    pass
