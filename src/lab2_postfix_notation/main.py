'''
Created on 15 сент. 2022 г.

@author: ASZabavin
'''

from shared_classes import CharStack, CharQueue

from lab1_lexical_analysis.main import LexicalAnalyzerC
from itertools import groupby
from collections import OrderedDict


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

    def get_priority_by_id(self, class_code: str, lex_id, lex_text=None):
        """
        Таблица приоритетов Дисктры для языка

        :param class_code: - код лексемы из методички
        :param lex_id: - идентификатор лексемы из таблицы 1 лаюораторной
        :param lex_text: - текст лексемы
        """
        if class_code.startswith('W'):
            return 1
        elif class_code.startswith('O'):
            return 2

        return 0

    def __init__(self, la_instance: LexicalAnalyzerC):
        self.la_instance = la_instance

        if not len(la_instance.ALL_registry):
            la_instance.run_analysis()
        self.TABLE_PRIORITY = {lx.order: self.get_priority_by_id(lx.class_code, lx.lex_id, lx.text) for lx in la_instance.ALL_registry}
        pass


if __name__ == "__main__":

    opz = DijkstratorC(LexicalAnalyzerC(r'input_code.cpp'))

    for prio, lexem in opz.get_by_priority_iterator():
        print((prio, lexem))

    pass
