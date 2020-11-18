class ReX:
    def __str__(self) -> str:
        pass

    def accepts(self, string: str) -> bool:
        pass


class Epsilon(ReX):
    def __str__(self) -> str:
        return ""

    def accepts(self, string: str) -> bool:
        return not string


class Symbol(ReX):
    def __init__(self, symb: str):
        self.symb = symb

    def __str__(self) -> str:
        return self.symb

    def accepts(self, string: str) -> bool:
        return self.symb == string


class Union(ReX):
    def __init__(self, leftRex: ReX, rightRex: ReX):
        self.leftRex = leftRex
        self.rightRex = rightRex

    def __str__(self) -> str:
        return f"{self.leftRex}|{self.rightRex}"

    def accepts(self, string: str) -> bool:
        return self.leftRex.accepts(string) or self.rightRex.accepts(string)


class Concatenation(Union):
    def __str__(self) -> str:
        return f"{self.leftRex},{self.rightRex}"

    def accepts(self, string: str) -> bool:
        for leftPartSize in range(len(string) + 1):
            leftString, rightString = str[:leftPartSize], str[leftPartSize:]
            if self.leftRex.accepts(leftString) and self.rightRex.accepts(rightString):
                return True
        return False


class KleneeStar(ReX):
    def __init__(self, rex: ReX):
        self.rex = rex

    def __str__(self) -> str:
        return f"{self.rex}*"

    def accepts(self, string: str) -> bool:
        for leftPartSize in range(len(string) + 1):
            leftString, rightString = str[:leftPartSize], str[leftPartSize:]
            if self.rex.accepts(leftString) and self.accepts(rightString):
                return True
        return False
