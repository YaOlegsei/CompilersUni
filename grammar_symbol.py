class GrammarSymbol:
    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return self.name

    def __eq__(self, other):
        return type(other) is type(self) and self.name == other.name

    def __hash__(self):
        return len(self.name)


class NonTerminal(GrammarSymbol):
    def __init__(self, name):
        super().__init__(name)


class FromNonTerminal(NonTerminal):
    def __init__(self, non_terminal: NonTerminal, additional_symbol: str):
        self.internal_terminal = non_terminal
        self.additional_symbol = additional_symbol
        super().__init__(f"{non_terminal.name}({additional_symbol})")


class Terminal(GrammarSymbol):
    def __init__(self, name):
        super().__init__(name)
