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

    def __eq__(self, other):
        return type(other) is type(self) \
               and self.left_symbol == other.left_symbol \
               and self.right_symbols == other.right_symbols

    def __hash__(self):
        return len(self.left_symbol.name) + len(self.right_symbols)

    def remove_disappearing_from_rule(self, disappearing: Sequence[NonTerminal]) :

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

        def no_epsilon_rules(rule: GrammarRule) -> bool:
            return len(rule.right_symbols) > 0

        if not self.right_symbols:
            return list()
        else:
            return list(
                filter(
                    no_epsilon_rules,
                    list(
                        map(
                            list_to_rule,
                            remove_disappearing_from_list(self.right_symbols),
                        )
                    )
                )
            )


if __name__ == "__main__":
    rule = GrammarRule(
        NonTerminal("A"),
        [NonTerminal("B"),
         NonTerminal("C"),
         ]
    )

    #new_rules = rule.remove_disappearing_from_rule([NonTerminal("C"), NonTerminal("B")])

    d= [12,2,2,2,2,2]
    print(d[1:])
    #print(new_rules)
