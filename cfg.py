from __future__ import annotations
from typing import Set, Dict, List, Sequence
from collections import defaultdict


class GrammarSymbol:
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other):
        return type(other) is type(self) and self.name == other.name

    def __hash__(self):
        return len(self.name)


class NonTerminalSymbol(GrammarSymbol):
    def __init__(self, name):
        super().__init__(name)


class TerminalSymbol(GrammarSymbol):
    def __init__(self, name):
        super().__init__(name)


class GrammarRule:
    def __init__(self, left_symbol: NonTerminalSymbol, right_symbols: Sequence[GrammarSymbol]):
        self.left_symbol = left_symbol
        self.right_symbols = right_symbols

    def __str__(self):
        right_str = ""
        for symb in self.right_symbols:
            right_str += f" {symb}"

        return f"{self.left_symbol} ->{right_str}"


class ContextFreeGrammar:
    def __init__(self,
                 terminals: Sequence[TerminalSymbol],
                 non_terminals: Sequence[NonTerminalSymbol],
                 rules: Sequence[GrammarRule],
                 start_non_terminal: NonTerminalSymbol,
                 ):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.rules = rules

        rules_dict: Dict[NonTerminalSymbol, List[GrammarRule]] = defaultdict(list)

        for rule in rules:
            rules_dict[rule.left_symbol].append(rule)

        self.rules_dict = rules_dict
        self.start_non_terminal = start_non_terminal

    def __get_new_alives__(self, alives: Set[NonTerminalSymbol]) -> List[NonTerminalSymbol]:
        new_alives: List[NonTerminalSymbol] = list()

        available_rules = filter(lambda rule:
                                 rule.left_symbol not in alives and rule.right_symbols,
                                 self.rules, )

        for rule in available_rules:
            not_alive_symbols = list(
                filter(lambda symb:
                       isinstance(symb, NonTerminalSymbol) and symb not in alives,
                       rule.right_symbols, ))

            if not not_alive_symbols:
                new_alives.append(rule.left_symbol)

        return new_alives

    def __get_alive_only_grammar(self) -> ContextFreeGrammar:
        alives: Set[NonTerminalSymbol] = set()

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
        reachables: Set[NonTerminalSymbol] = {self.start_non_terminal}

        reachable_rules = self.rules_dict[self.start_non_terminal]

        while reachable_rules:
            rule = reachable_rules.pop()

            for symbol in rule.right_symbols:
                if isinstance(symbol, NonTerminalSymbol) and symbol not in reachables:
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
            .__get_alive_only_grammar(self) \
            .__get_reachable_only_grammar__()

    def __get_new_disappearing__(self, disappearing: Set[NonTerminalSymbol]) -> List[NonTerminalSymbol]:
        new_disappearing: Set[NonTerminalSymbol] = set()
        for rule in self.rules:
            if rule.left_symbol in disappearing : continue
            not_disappearing_symbols = list(filter(lambda symbol: symbol not in disappearing, rule.right_symbols))
            if not not_disappearing_symbols: new_disappearing.add(rule.left_symbol)

        return list(new_disappearing)

    def detect_disappearing_non_terminals(self) -> List[NonTerminalSymbol]:
        disappearing: Set[NonTerminalSymbol] = set()

        while True:
            new_disappearing = self.__get_new_disappearing__(disappearing)

            if not new_disappearing: break

            disappearing.update(new_disappearing)

        return list(disappearing)


if __name__ == "__main__":
    cfg = ContextFreeGrammar(
        [TerminalSymbol("chr"), TerminalSymbol("ast")],
        [NonTerminalSymbol("A"), NonTerminalSymbol("B")],
        [GrammarRule(NonTerminalSymbol("A"), [TerminalSymbol("chr"), TerminalSymbol("ast")])],
        NonTerminalSymbol("A"),
    )

    cfg_non_terminals = ContextFreeGrammar(
        [TerminalSymbol("chr"), TerminalSymbol("ast")],
        [NonTerminalSymbol("A"), NonTerminalSymbol("B"), NonTerminalSymbol("S")],
        [
            GrammarRule(NonTerminalSymbol("S"), [NonTerminalSymbol("A"), NonTerminalSymbol("B")]),
            GrammarRule(NonTerminalSymbol("A"), []),
            GrammarRule(NonTerminalSymbol("B"), [])
         ],
        NonTerminalSymbol("S"),
    )
    print(cfg_non_terminals.detect_disappearing_non_terminals())
    #print(cfg)
    #print(cfg.remove_external_non_terminals())
