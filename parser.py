from cfg import ContextFreeGrammar
from grammar_symbol import GrammarSymbol, Terminal, NonTerminal
from grammar_rule import GrammarRule
from typing import Sequence, Dict, List, Set
from collections import defaultdict


class Parser:
    epsilon = Terminal("epsilon")

    end_symbol = Terminal("$")

    def __init__(self, cfg: ContextFreeGrammar):
        self.grammar = cfg \
            .remove_external_non_terminals() \
            .transform_to_greibach_form() \
            .remove_left_recursion() \
            .factorize_grammar()

        self.first_dict: Dict[NonTerminal, Set[Terminal]] = defaultdict(set)
        self.follows_dict: Dict[NonTerminal, Set[Terminal]] = defaultdict(set)
        self.__create_first__()
        self.__create_follows__()

    def __create_first__(self):
        first_dict = self.first_dict
        changed = True
        while changed:
            changed = False

            for rule in self.grammar.rules:
                current_symbol = rule.left_symbol
                previous_size = len(first_dict[current_symbol])

                first_dict[current_symbol].update(self.first(rule.right_symbols))

                current_size = len(first_dict[current_symbol])
                changed = changed or previous_size != current_size

        return first_dict

    def first(self, word: Sequence[GrammarSymbol]) -> List[Terminal]:
        if not word:
            return [Parser.epsilon]

        result: List[Terminal] = list()
        has_epsilon_before = True

        for symbol in word:
            if isinstance(symbol, Terminal):
                result += [symbol]
                has_epsilon_before = False

            if not has_epsilon_before:
                break

            result += list(self.first_dict[symbol])
            has_epsilon_before = Parser.epsilon in self.first_dict[symbol]

        return result
        # def parse(self,symbols:Sequence[str]):

    def __create_follows__(self) -> Dict[NonTerminal, Set[Terminal]]:
        follows_dict = self.follows_dict
        follows_dict[self.grammar.start_non_terminal].add(Parser.end_symbol)

        def filter_epsilon(terminals: Sequence[Terminal]) -> List[Terminal]:
            result: List[Terminal] = list()
            for terminal in terminals:
                if terminal != Parser.epsilon:
                    result.append(terminal)
            return result

        def handle_rule(left_symbol: NonTerminal, current_symbol: NonTerminal, word: Sequence[GrammarSymbol]):
            if not word:
                follows_dict[current_symbol].update(follows_dict[left_symbol])
                return

            first_word = self.first(word)

            follows_dict[current_symbol].update(filter_epsilon(first_word))
            if Parser.epsilon in first_word:
                follows_dict[current_symbol].update(follows_dict[left_symbol])

        changed = True
        while changed:
            changed = False

            for rule in self.grammar.rules:
                beta: List[GrammarSymbol] = list()
                for i in reversed(range(0, len(rule.right_symbols))):
                    beta = [rule.right_symbols[i]] + beta
                    current_symbol = rule.right_symbols[i]

                    if not isinstance(current_symbol, NonTerminal):
                        continue
                    previous_size = len(follows_dict[current_symbol])

                    handle_rule(rule.left_symbol, current_symbol, beta[1:])

                    current_size = len(follows_dict[current_symbol])
                    changed = changed or previous_size != current_size

        return follows_dict


if __name__ == "__main__":
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

    parser = Parser(cfg_for_factorization)

    parser.first_dict
