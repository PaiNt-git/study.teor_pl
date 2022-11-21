'''
Created on 15 сент. 2022 г.

@author: ASZabavin
'''

from collections import OrderedDict
from itertools import groupby

from shared_classes import VarStack, VarQueue

from lab1_lexical_analysis.main import LexicalAnalyzerC


class DijkstratorC():

    TABLE_PRIORITY = {}

    @property
    def TABLE_PRIORITY_ITEMS(self):
        itms = sorted(self.TABLE_PRIORITY.items(), key=lambda x: x[1])
        self.TABLE_PRIORITY = dict(itms)
        return itms

    def get_by_priority_iterator(self):
        for prio, lexems in groupby(self.TABLE_PRIORITY_ITEMS, lambda x: x[1]):
            for lxorder in lexems:
                yield prio, self.la_instance.get_reg_lexem_by_order(lxorder[0])

    def get_priority_by_lexemid(self, class_code: str, lex_id, lex_text=None):
        """
        Таблица приоритетов Дисктры для языка

        :param class_code: - код лексемы из методички
        :param lex_id: - идентификатор лексемы из таблицы 1 лаюораторной
        :param lex_text: - текст лексемы
        """

        # TODO: Доделать приоритеты
        if class_code.startswith('W'):
            return 1
        elif class_code.startswith('O'):
            return 2

        return 0

    def get_priority_by_reg_lex_order(self, order: int):
        lx = self.la_instance.get_reg_lexem_by_order(order)
        return self.get_priority_by_lexemid(lx.class_code, lx.lex_id, lx.text)

    def __init__(self, la_instance: LexicalAnalyzerC):
        self.la_instance = la_instance

        if not len(la_instance.ALL_registry):
            la_instance.run_analysis()
        self.TABLE_PRIORITY = {lx.order: self.get_priority_by_lexemid(lx.class_code, lx.lex_id, lx.text) for lx in la_instance.ALL_registry}

        self._lexem_queue = VarQueue(la_instance.ALL_registry)
        self._postfix_stack = VarStack()
        self._output_list = []
        self._cur_op_state = 'S'
        pass

    STATES = [
        'S',
        'BLOCK_BODY',  # { BLOCK_BODY }
        'FUNC_BODY',  # ( FUNC_BODY )
    ]

    def stack_top(self):
        return self._postfix_stack.top()

    def stack_pop_and_state(self, state=''):
        if state:
            self._cur_op_state = state
        return self._postfix_stack.pop()

    def stack_add_and_state(self, lex, state=''):
        self._postfix_stack.add(lex)
        if state:
            self._cur_op_state = state

    def output_add_and_state(self, lex, state=''):
        self._output_list.append(lex)
        if state:
            self._cur_op_state = state

    @property
    def cur_op_state(self):
        return self._cur_op_state

    def run_postfix_notatization(self):

        while not self._lexem_queue.is_empty:
            cl = self._lexem_queue.pop()

            # Если лексема является числом, строкой, добавляем ее в ПОЛИЗ-массив
            if cl.class_code in ('N', 'C', ):
                self.output_add_and_state(cl)

            # Если лексема идентификатор
            elif cl.class_code in ('I'):
                nexto = cl.order + 1
                nextlex = self.la_instance.get_reg_lexem_by_order(nexto)

                # Если лексема идентификатор переменной, добавляем ее в ПОЛИЗ-массив
                if not nextlex or nextlex.text != '(':
                    self.output_add_and_state(cl)

                # Если лексема является символом функции, помещаем ее в стек
                elif nextlex and nextlex == '(':
                    self.stack_add_and_state(cl, 'FUNC_BODY')

            # Если лексема является разделителем аргументов функции (например, запятая)
            elif self.cur_op_state == 'FUNC_BODY' and cl.class_code in ('R') and cl.text == ',':

                #===============================================================================
                # до тех пор, пока верхним элементом стека не станет
                # открывающаяся скобка, выталкиваем элементы из стека в
                # ПОЛИЗ-массив. Если открывающаяся скобка не встретилась,
                # это означает, что в выражении либо неверно поставлен
                # разделитель, либо несогласованы скобки
                #===============================================================================
                while self.stack_top().text != '(':
                    cl = self.stack_pop_and_state()
                    self.output_add_and_state(cl, 'FUNC_BODY')

            # Если лексема является операцией θ, тогда
            elif cl.class_code in ('O'):
                op_priority = self.get_priority_by_reg_lex_order(cl.order)

                is_left_op_ = self.la_instance.is_left_op(cl.text)
                is_right_op_ = self.la_instance.is_right_op(cl.text)

                #===============================================================================
                # 1) пока приоритет θ меньше либо равен приоритету операции,
                # находящейся на вершине стека (для лево-ассоциативных
                # операций), или приоритет θ строго меньше приоритета
                # операции, находящейся на вершине стека (для право-
                # ассоциативных операций) выталкиваем верхние элементы
                # стека в ПОЛИЗ-массив;
                # 2) помещаем операцию θ в стек.
                #===============================================================================
                if is_left_op_:
                    while op_priority <= self.get_priority_by_reg_lex_order(self.stack_top().order):
                        cl = self.stack_pop_and_state()
                        self.output_add_and_state(cl)

                elif is_right_op_:
                    while op_priority < self.get_priority_by_reg_lex_order(self.stack_top().order):
                        cl = self.stack_pop_and_state()
                        self.output_add_and_state(cl)

            # Открывающую скобку всегда вносим в стек
            elif cl.class_code in ('R') and cl.text == '(':
                self.stack_add_and_state(cl)

            #===============================================================================
            # Если лексема является закрывающей скобкой, выталкиваем
            # элементы из стека в ПОЛИЗ-массив до тех пор, пока на вершине
            # стека не окажется открывающая скобка. При этом открывающая
            # скобка удаляется из стека, но в ПОЛИЗ-массив не добавляется.
            # Если после этого шага на вершине стека оказывается символ
            # функции, выталкиваем его в ПОЛИЗ-массив. Если в процессе
            # выталкивания открывающей скобки не нашлось и стек пуст, это
            # означает, что в выражении не согласованы скобки
            #===============================================================================
            elif cl.class_code in ('R') and cl.text == ')':

                while self.stack_top().text != '(':
                    cl = self.stack_pop_and_state()
                    self.output_add_and_state(cl)

                if self.stack_top().text == '(':
                    cl = self.stack_pop_and_state()

                    topl = self.stack_top()
                    if topl:
                        nexto = topl.order + 1
                        nextlex = self.la_instance.get_reg_lexem_by_order(nexto)
                        if self.cur_op_state == 'FUNC_BODY' and topl.class_code == 'I' and nextlex.text == '(':
                            topl = self.stack_pop_and_state()
                            self.output_add_and_state(topl, 'BLOCK_BODY')

            # Открывающую {
            elif cl.class_code in ('R') and cl.text == '{':
                self.stack_add_and_state(cl)

            #===============================================================================
            # Если лексема является } скобкой, выталкиваем
            # элементы из стека в ПОЛИЗ-массив до тех пор, пока на вершине
            # стека не окажется { скобка. При этом {
            # скобка удаляется из стека, но в ПОЛИЗ-массив не добавляется.
            # Если в процессе выталкивания { скобки не нашлось и стек пуст, это
            # означает, что в выражении не согласованы скобки
            #===============================================================================
            elif cl.class_code in ('R') and cl.text == '}':

                while self.stack_top().text != '{':
                    cl = self.stack_pop_and_state()
                    self.output_add_and_state(cl)

                if self.stack_top().text == '{':
                    cl = self.stack_pop_and_state()

                    topl = self.stack_top()
                    if topl:
                        nexto = topl.order + 1
                        nextlex = self.la_instance.get_reg_lexem_by_order(nexto)
                        if self.cur_op_state == 'BLOCK_BODY' and topl.class_code == 'I' and nextlex.text == '{':
                            topl = self.stack_pop_and_state()
                            self.output_add_and_state(topl, 'S')

            pass

        pass

    def __str__(self):
        return ' '.join([x.text for x in self._output_list])


if __name__ == "__main__":

    opz = DijkstratorC(LexicalAnalyzerC(r'input_code.cpp'))

    opz.run_postfix_notatization()

    for lexem in opz.la_instance.ALL_registry:
        print((lexem.order, str(lexem)))

    print(opz)

    pass
