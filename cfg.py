from __future__ import annotations
from typing import Set, Dict, List, Sequence, Optional
from collections import defaultdict
from grammar_symbol import NonTerminal,Terminal
from grammar_rule import GrammarRule


class ContextFreeGrammar:
    def __init__(self,
                 terminals: Sequence[Terminal],
                 non_terminals: Sequence[NonTerminal],
                 rules: Sequence[GrammarRule],
                 start_non_terminal: NonTerminal,
                 ):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.rules = rules

        rules_dict: Dict[NonTerminal, List[GrammarRule]] = defaultdict(list)

        for rule in rules:
            rules_dict[rule.left_symbol].append(rule)

        self.rules_dict = rules_dict
        self.start_non_terminal = start_non_terminal

    def __get_new_alives__(self, alives: Set[NonTerminal]) -> List[NonTerminal]:
        new_alives: List[NonTerminal] = list()

        available_rules = filter(lambda rule:
                                 rule.left_symbol not in alives and rule.right_symbols,
                                 self.rules, )

        for rule in available_rules:
            not_alive_symbols = list(
                filter(lambda symb:
                       isinstance(symb, NonTerminal) and symb not in alives,
                       rule.right_symbols, ))

            if not not_alive_symbols:
                new_alives.append(rule.left_symbol)

        return new_alives

    def __get_alive_only_grammar__(self) -> ContextFreeGrammar:
        alives: Set[NonTerminal] = set()

        while True:
            new_alives = self.__get_new_alives__(alives)

            if not new_alives:
                break

            alives.update(new_alives)

        new_rules = list(filter(lambda rule: rule.left_symbol in alives, self.rules))

        return ContextFreeGrammar(self.terminals,
                                  list(alives),
                                  new_rules,
                                  self.start_non_terminal,
                                  )

    def __get_reachable_only_grammar__(self) -> ContextFreeGrammar:
        reachables: Set[NonTerminal] = {self.start_non_terminal}

        reachable_rules = self.rules_dict[self.start_non_terminal]

        while reachable_rules:
            rule = reachable_rules.pop()

            for symbol in rule.right_symbols:
                if isinstance(symbol, NonTerminal) and symbol not in reachables:
                    reachables.add(symbol)
                    reachable_rules.extend(self.rules_dict[symbol])

        new_rules = list(filter(lambda rule: rule.left_symbol in reachables, self.rules))

        return ContextFreeGrammar(self.terminals,
                                  list(reachables),
                                  new_rules,
                                  self.start_non_terminal,
                                  )

    def __str__(self):
        terminals = "Terminals: "
        for terminal in self.terminals:
            terminals += f" {terminal}"

        non_terminals = "Non-terminals: "
        for non_terminal in self.non_terminals:
            non_terminals += f" {non_terminal}"

        rules = "Rules: "
        for rule in self.rules:
            rules += f"  {rule} \n"

        return f"{terminals}\n{non_terminals}\n{rules}"

    def remove_external_non_terminals(self):
        return ContextFreeGrammar \
            .__get_alive_only_grammar__(self) \
            .__get_reachable_only_grammar__()

    def __get_new_disappearing__(self, disappearing: Set[NonTerminal]) -> List[NonTerminal]:
        new_disappearing: Set[NonTerminal] = set()
        for rule in self.rules:
            if rule.left_symbol in disappearing: continue
            not_disappearing_symbols = list(filter(lambda symbol: symbol not in disappearing, rule.right_symbols))
            if not not_disappearing_symbols: new_disappearing.add(rule.left_symbol)

        return list(new_disappearing)

    def detect_disappearing_non_terminals(self) -> List[NonTerminal]:
        disappearing: Set[NonTerminal] = set()

        while True:
            new_disappearing = self.__get_new_disappearing__(disappearing)

            if not new_disappearing: break

            disappearing.update(new_disappearing)

        return list(disappearing)

    def __detect_if_in_cycle__(self, symb: NonTerminal) -> bool:

        disappearing: List[NonTerminal] = self.detect_disappearing_non_terminals()

        def find_most_left_non_terminals(rule: GrammarRule) -> List[NonTerminal]:
            left_non_terminals: Set[NonTerminal] = set()
            for symb in rule.right_symbols:
                if symb in disappearing:
                    left_non_terminals.add(symb)
                    continue
                if isinstance(symb, NonTerminal):
                    left_non_terminals.add(symb)
                break

            return list(left_non_terminals)

        enter_dict: Dict[NonTerminal, bool] = defaultdict(lambda: False)

        def dfs(cur_symb: NonTerminal) -> Optional[NonTerminal]:

            has_entered = enter_dict[cur_symb]
            if has_entered: return cur_symb

            enter_dict[cur_symb] = True

            for rule in self.rules_dict[cur_symb]:
                for next_symb in find_most_left_non_terminals(rule):
                    if symb == dfs(next_symb):
                        enter_dict[cur_symb] = False
                        return symb

            enter_dict[cur_symb] = False
            return None

        return dfs(symb) == symb

    def detect_left_recursion(self) -> List[NonTerminal]:
        return list(
            filter(
                lambda non_terminal: self.__detect_if_in_cycle__(non_terminal),
                self.non_terminals,
            )
        )


if __name__ == "__main__":
    cfg = ContextFreeGrammar(
        [Terminal("chr"), Terminal("ast")],
        [NonTerminal("A"), NonTerminal("B")],
        [GrammarRule(NonTerminal("A"), [Terminal("chr"), Terminal("ast")])],
        NonTerminal("A"),
    )

    cfg_non_terminals = ContextFreeGrammar(
        [Terminal("chr"), Terminal("ast")],
        [NonTerminal("A"), NonTerminal("B"), NonTerminal("S")],
        [
            GrammarRule(NonTerminal("S"), [NonTerminal("A"), NonTerminal("B")]),
            GrammarRule(NonTerminal("A"), []),
            GrammarRule(NonTerminal("B"), [])
        ],
        NonTerminal("S"),
    )

    cfg_simple_recursion = ContextFreeGrammar(
        [Terminal("chr"), Terminal("ast")],
        [NonTerminal("A"), NonTerminal("B")],
        [
            GrammarRule(NonTerminal("A"), [NonTerminal("A"), ]),
            GrammarRule(NonTerminal("B"), [])
        ],
        NonTerminal("A"),
    )

    cfg_complex_recursion = ContextFreeGrammar(
        [Terminal("chr"), Terminal("ast")],
        [NonTerminal("A"), NonTerminal("B"), NonTerminal("S")],
        [
            GrammarRule(NonTerminal("S"), [NonTerminal("A"), NonTerminal("B")]),
            GrammarRule(NonTerminal("B"), [NonTerminal("S"), ]),
            GrammarRule(NonTerminal("A"), [NonTerminal("B")]),
        ],
        NonTerminal("S"),
    )
    d = cfg_complex_recursion.detect_left_recursion()
    print(cfg_complex_recursion.detect_disappearing_non_terminals())
    # print(cfg)
    # print(cfg.remove_external_non_terminals())
