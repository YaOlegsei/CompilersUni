from __future__ import annotations
from typing import List, Sequence
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

    def remove_disappearing_from_rule(self, disappearing: Sequence[NonTerminal]) -> List[GrammarRule]:

        def remove_disappearing_from_list(
                right_symbols: List[GrammarSymbol],
        ) -> List[List[GrammarSymbol]]:
            i = 0
            for symbol in right_symbols:
                i += 1
                if symbol in disappearing:
                    last_parts = \
                        remove_disappearing_from_list(right_symbols[i:])

                    if len(last_parts) == 0:
                        return [right_symbols[:i], right_symbols[:i - 1]]

                    with_last_symb = list(
                        map(
                            lambda list: right_symbols[:i] + list,
                            last_parts,
                        )
                    )

                    no_last_symb = list(
                        map(
                            lambda list: right_symbols[:i - 1] + list,
                            last_parts,
                        )
                    )

                    return no_last_symb + with_last_symb

            return [right_symbols]

        def list_to_rule(symb_list) -> GrammarRule:
            return GrammarRule(self.left_symbol, symb_list)

        return list(
            map(
                list_to_rule,
                remove_disappearing_from_list(self.right_symbols),
            )
        )


if __name__ == "__main__":
    rule = GrammarRule(
        NonTerminal("A"),
        [NonTerminal("B"),
         Terminal("ast"),
         NonTerminal("C"),
         NonTerminal("V")]
    )

    new_rules = rule.remove_disappearing_from_rule([NonTerminal("C"), NonTerminal("B")])

    print(new_rules)
