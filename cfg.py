from typing import Set, Dict, List, Sequence
from collections import defaultdict
from grammar_symbol import NonTerminal, Terminal, FromNonTerminal, GrammarSymbol
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

        available_rules = list(filter(lambda rule:
                                      rule.left_symbol not in alives,
                                      self.rules, ))

        for rule in available_rules:
            not_alive_symbols = list(
                filter(lambda symb:
                       isinstance(symb, NonTerminal) and symb not in alives,
                       rule.right_symbols, ))

            if not not_alive_symbols:
                new_alives.append(rule.left_symbol)

        return new_alives

    def __get_alive_only_grammar__(self):
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

    def __get_reachable_only_grammar__(self):
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

        start_non_terminal = f"Start non-terminal: {self.start_non_terminal}"

        rules = "Rules: \n"
        for rule in self.rules:
            rules += f"  {rule} \n"

        return f"{terminals}\n{non_terminals}\n{start_non_terminal}\n{rules}"

    def remove_external_non_terminals(self):
        return self \
            .__get_alive_only_grammar__() \
            .__get_reachable_only_grammar__()

    def __get_new_disappearing__(self, disappearing: Set[NonTerminal]) -> List[NonTerminal]:
        new_disappearing: Set[NonTerminal] = set()
        for rule in self.rules:
            if rule.left_symbol in disappearing:
                continue
            not_disappearing_symbols = list(filter(lambda symbol: symbol not in disappearing, rule.right_symbols))
            if not not_disappearing_symbols:
                new_disappearing.add(rule.left_symbol)

        return list(new_disappearing)

    def detect_disappearing_non_terminals(self) -> List[NonTerminal]:
        disappearing: Set[NonTerminal] = set()

        while True:
            new_disappearing = self.__get_new_disappearing__(disappearing)

            if not new_disappearing:
                break

            disappearing.update(new_disappearing)

        return list(disappearing)

    def detect_left_recursion(self) -> bool:

        disappearing: List[NonTerminal] = self.detect_disappearing_non_terminals()

        def find_most_left_non_terminals(rule: GrammarRule) -> List[NonTerminal]:
            left_non_terminals: Set[NonTerminal] = set()
            for symbol in rule.right_symbols:
                if symbol in disappearing:
                    left_non_terminals.add(symbol)
                    continue
                if isinstance(symbol, NonTerminal):
                    left_non_terminals.add(symbol)
                break

            return list(left_non_terminals)

        enter_dict: Dict[NonTerminal, bool] = defaultdict(lambda: False)

        def dfs(cur_symb: NonTerminal) -> bool:

            has_entered = enter_dict[cur_symb]
            if has_entered:
                return True

            enter_dict[cur_symb] = True

            for rule in self.rules_dict[cur_symb]:
                for next_symb in find_most_left_non_terminals(rule):
                    if dfs(next_symb):
                        enter_dict[cur_symb] = False
                        return True

            enter_dict[cur_symb] = False
            return False

        return dfs(self.start_non_terminal)

    def transform_to_greibach_form(self):
        clean_grammar = self
        disappearing = clean_grammar.detect_disappearing_non_terminals()

        new_rules: Set[GrammarRule] = set(clean_grammar.rules)
        new_start: NonTerminal = clean_grammar.start_non_terminal
        new_non_terminals: Sequence[NonTerminal] = clean_grammar.non_terminals

        if disappearing:
            new_rules = set()
            for rule in clean_grammar.rules:
                new_rules \
                    .update(rule.remove_disappearing_from_rule(disappearing))

            if clean_grammar.start_non_terminal in disappearing:
                new_start = FromNonTerminal(new_start, str(len(clean_grammar.non_terminals)))

                new_rules.add(GrammarRule(new_start, []))
                new_rules.add(GrammarRule(new_start, [clean_grammar.start_non_terminal]))
                new_non_terminals = [new_start] + list(new_non_terminals)

        return ContextFreeGrammar(
            clean_grammar.terminals,
            new_non_terminals,
            list(new_rules),
            new_start,
        )

    def __remove_direct_left_recursion__(self, symbol: NonTerminal):
        symbol_rules = self.rules_dict[symbol]

        no_direct_recursion = list(
            filter(
                lambda rule: rule.right_symbols[0] != symbol,
                symbol_rules,
            )
        )

        has_direct_recursion = list(
            filter(
                lambda rule: rule.right_symbols[0] == symbol,
                symbol_rules,
            )
        )
        if not has_direct_recursion:
            return self
        new_symbol = FromNonTerminal(symbol, str(len(self.non_terminals)))

        new_symbol_rules: List[GrammarRule] = list()
        for rule in has_direct_recursion:
            new_symbol_rules += [GrammarRule(new_symbol, rule.right_symbols[1:] + [new_symbol])]
            new_symbol_rules += [GrammarRule(new_symbol, [])]

        old_symbol_rules = list(
            map(
                lambda rule:
                GrammarRule(symbol, rule.right_symbols + [new_symbol]),
                no_direct_recursion,
            )
        )

        old_rules = list(
            filter(
                lambda rule: rule.left_symbol != symbol,
                self.rules,
            )
        )

        return ContextFreeGrammar(
            self.terminals,
            list(self.non_terminals) + [new_symbol],
            old_rules + new_symbol_rules + old_symbol_rules,
            self.start_non_terminal
        )

    def __remove_indirect_recursion_for__(self,
                                          lower_symbol: NonTerminal,
                                          greater_symbol: NonTerminal,
                                          ):
        starts_with_lower = list(
            filter(
                lambda rule: rule.right_symbols and rule.right_symbols[0] == lower_symbol,
                self.rules_dict[greater_symbol],
            )
        )

        new_rules_for_greater: Set[GrammarRule] = set(
            filter(
                lambda rule: rule.right_symbols[0] != lower_symbol,
                self.rules_dict[greater_symbol],
            )
        )

        for rule_with_lower in starts_with_lower:
            new_rules_for_greater.update(list(
                map(
                    lambda rule_for_lower:
                    GrammarRule(greater_symbol, rule_for_lower.right_symbols + rule_with_lower.right_symbols[1:]),
                    self.rules_dict[lower_symbol],
                )
            ))

        old_rules = set(
            filter(
                lambda rule: rule.left_symbol != greater_symbol,
                self.rules,
            )
        )

        new_rules = old_rules

        new_rules.update(new_rules_for_greater)

        return ContextFreeGrammar(
            self.terminals,
            self.non_terminals,
            list(new_rules),
            self.start_non_terminal,
        )

    def remove_left_recursion(self):
        current_grammar = self

        if not current_grammar.detect_left_recursion():
            return current_grammar

        ordered_non_terminals = \
            [current_grammar.start_non_terminal] + \
            list(
                filter(
                    lambda symbol: symbol != current_grammar.start_non_terminal,
                    current_grammar.non_terminals,
                )
            )

        for i in range(len(ordered_non_terminals)):
            greater_symbol = ordered_non_terminals[i]

            for j in range(i):
                lower_symbol = ordered_non_terminals[j]
                current_grammar = \
                    current_grammar.__remove_indirect_recursion_for__(lower_symbol, greater_symbol)

            current_grammar = \
                current_grammar.__remove_direct_left_recursion__(greater_symbol)

        return current_grammar

    def factorize_grammar(self):
        clean_grammar = self

        factorization_set: Set[NonTerminal] = set(clean_grammar.non_terminals)

        rules_dict: Dict[NonTerminal, List[GrammarRule]] = dict(clean_grammar.rules_dict)

        new_rules: Set[GrammarRule] = set()
        new_symbols: List[NonTerminal] = list(clean_grammar.non_terminals)
        additional_symbols_count = len(clean_grammar.non_terminals)

        def is_only_terminals(rule: GrammarRule) -> bool:
            for symbol in rule.right_symbols:
                if not isinstance(symbol, Terminal):
                    return False

            return True

        while factorization_set:
            first_symb_dict: Dict[GrammarSymbol, List[GrammarRule]] = defaultdict(list)
            current_symbol = factorization_set.pop()
            rules_for_current = rules_dict[current_symbol]

            for rule in rules_for_current:
                if is_only_terminals(rule) or len(rule.right_symbols) == 1:
                    new_rules.add(rule)
                    continue

                first_symb_dict[rule.right_symbols[0]].append(rule)

            for start_symbol, rules_for_symb in first_symb_dict.items():

                if len(rules_for_symb) > 1:
                    new_symb = FromNonTerminal(current_symbol, f"{additional_symbols_count}")

                    rules_dict[new_symb] = list(
                        map(
                            lambda rule: GrammarRule(new_symb, rule.right_symbols[1:]),
                            rules_for_symb,
                        )
                    )
                    new_symbols.append(new_symb)
                    new_rules.add(GrammarRule(current_symbol, [start_symbol, new_symb]))

                    factorization_set.add(new_symb)
                    additional_symbols_count += 1
                else:
                    if rules_for_symb:
                        new_rules.update(rules_for_symb)

        return ContextFreeGrammar(
            clean_grammar.terminals,
            new_symbols,
            list(new_rules),
            clean_grammar.start_non_terminal,
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
        [NonTerminal("S"), NonTerminal("A"), ],
        [
            GrammarRule(NonTerminal("S"), [NonTerminal("A"), NonTerminal("B")]),
            GrammarRule(NonTerminal("B"), [NonTerminal("S")]),
            GrammarRule(NonTerminal("A"), [NonTerminal("B")]),
        ],
        NonTerminal("S"),
    )

    cfg_not_greibach = ContextFreeGrammar(
        [Terminal("a"), Terminal("b")],
        [NonTerminal("S"), NonTerminal("B"), NonTerminal("A")],
        [
            GrammarRule(NonTerminal("S"), [NonTerminal("A"), NonTerminal("B")]),
            GrammarRule(NonTerminal("B"), []),
            GrammarRule(NonTerminal("B"), [Terminal("b"), NonTerminal("B")]),
            GrammarRule(NonTerminal("A"), []),
            GrammarRule(NonTerminal("A"), [Terminal("a"), NonTerminal("A")]),
        ],
        NonTerminal("S"),
    )

    cfg_left_recursion = ContextFreeGrammar(
        [Terminal("a"), Terminal("b"), Terminal("g")],
        [NonTerminal("S"), NonTerminal("B"), NonTerminal("A")],
        [
            GrammarRule(NonTerminal("A"), [NonTerminal("S"), Terminal("a")]),
            GrammarRule(NonTerminal("S"), [NonTerminal("S"), Terminal("b")]),
            GrammarRule(NonTerminal("S"), [NonTerminal("A"), Terminal("g")]),
            GrammarRule(NonTerminal("S"), [Terminal("b")]),
        ],
        NonTerminal("S"),
    )

    cfg_for_factorization = ContextFreeGrammar(
        [Terminal("+"), Terminal("*"), Terminal("n"), Terminal("("), Terminal(")")],
        [NonTerminal("E"), NonTerminal("T"), NonTerminal("F")],
        [
            GrammarRule(NonTerminal("E"), [NonTerminal("T"), Terminal("+"), NonTerminal("E")]),
            GrammarRule(NonTerminal("E"), [NonTerminal("T")]),
            GrammarRule(NonTerminal("T"), [NonTerminal("F"), Terminal("*"), NonTerminal("T")]),
            GrammarRule(NonTerminal("T"), [NonTerminal("F")]),
            GrammarRule(NonTerminal("F"), [Terminal("n")]),
            GrammarRule(NonTerminal("F"), [Terminal("("), NonTerminal("E"), Terminal(")")]),
        ],
        NonTerminal("E")
    )

    # print(cfg_not_greibach.transform_to_greibach_form())
    # print(cfg_left_recursion.transform_to_greibach_form())
    """print("*****")
    print(cfg_left_recursion.remove_left_recursion())
    print("*****")
    print(cfg_left_recursion.factorize_grammar())
    print("*****")"""
    print(cfg_for_factorization.factorize_grammar())

    # has_left_recursion = cfg.detect_left_recursion()
    # print(f"has left recursion: {has_left_recursion}")
    # print(cfg)
    # print(cfg.remove_external_non_terminals())
