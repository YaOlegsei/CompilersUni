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
    def __init__(self, non_terminal: NonTerminal):
        self.internal_terminal = non_terminal
        super().__init__(f"{non_terminal.name}'")

    def __eq__(self, other):
        return type(other) is type(self) and self.internal_terminal == other.internal_terminal


class Terminal(GrammarSymbol):
    def __init__(self, name):
        super().__init__(name)
