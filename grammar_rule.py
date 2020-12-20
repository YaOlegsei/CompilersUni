from typing import Set, Dict, List, Sequence, Optional
from grammar_symbol import GrammarSymbol, NonTerminal, Terminal


class GrammarRule:
    def __init__(self, left_symbol: NonTerminal, right_symbols: List[GrammarSymbol]):
        self.left_symbol = left_symbol
        self.right_symbols = right_symbols

    def __str__(self):
        right_str = ""
        for symb in self.right_symbols:
            right_str += f" {symb}"

        return f"{self.left_symbol} ->{right_str}"
