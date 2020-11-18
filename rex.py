from msp import LTS, LabelledTransition


class ReX:
    def __str__(self) -> str:
        pass

    def accepts(self, string: str) -> bool:
        pass

    def rex2lts(self, first_state: int = 0) -> LTS:
        label = self.__str__()
        start, end = first_state, first_state + 1

        return LTS(start,
                   end,
                   set(range(start, end + 1)),
                   {LabelledTransition(start, end, label, )},
                   )


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
    def __init__(self, left_rex: ReX, right_rex: ReX):
        self.left_rex = left_rex
        self.right_rex = right_rex

    def __str__(self) -> str:
        return f"{self.left_rex}|{self.right_rex}"

    def accepts(self, string: str) -> bool:
        return self.left_rex.accepts(string) or self.right_rex.accepts(string)

    def rex2lts(self, first_state: int = 0) -> LTS:
        """
        startState ->  ltsLeft.startState     ltsLeft.endState
            |                                        |
            |                                    endState
            |                                        |
        ltsRight                                ltsRight
        """
        lts_left = self.left_rex.rex2lts(first_state + 1)
        lts_right = self.right_rex.rex2lts(
            first_state + 1 + len(lts_left.states))
        start, end = first_state, lts_right.end + 1
        transitions = lts_left.transitions

        transitions.update(lts_right.transitions)
        transitions.add(LabelledTransition(start, lts_left.start, "", ))
        transitions.add(LabelledTransition(start, lts_right.start, "", ))
        transitions.add(LabelledTransition(lts_left.end, end, "", ))
        transitions.add(LabelledTransition(lts_right.end, end, "", ))

        return LTS(start,
                   end,
                   set(range(start, end + 1)),
                   transitions, )


class Concatenation(ReX):
    def __init__(self, left_rex: ReX, right_rex: ReX):
        self.leftRex = left_rex
        self.rightRex = right_rex

    def __str__(self) -> str:
        return f"{self.leftRex},{self.rightRex}"

    def accepts(self, string: str) -> bool:
        for left_part_size in range(len(string) + 1):
            left_string, right_string = string[:left_part_size], string[left_part_size:]
            if self.leftRex.accepts(left_string) and self.rightRex.accepts(right_string):
                return True
        return False

    def rex2lts(self, first_state: int = 0) -> LTS:
        """
         ltsLeft.endState -> ltsRight.startState
        """
        lts_left = self.leftRex.rex2lts(0)
        lts_right = self.rightRex.rex2lts(first_state + len(lts_left.states))
        start, end = lts_left.start, lts_right.end
        transitions = lts_left.transitions

        transitions.update(lts_right.transitions)
        transitions.add(LabelledTransition(lts_left.end, lts_right.start, "", ))
        return LTS(
            start,
            end,
            set(range(start, end + 1)),
            transitions,
        )


class KleneeStar(ReX):
    def __init__(self, rex: ReX):
        self.rex = rex

    def __str__(self) -> str:
        return f"{self.rex}*"

    def accepts(self, string: str) -> bool:
        if not string:
            return True

        for left_part_size in range(len(string) + 1):
            left_string, right_string = string[:left_part_size], string[left_part_size:]
            if self.rex.accepts(left_string) and self.accepts(right_string):
                return True
        return False

    def rex2lts(self, first_state: int = 0) -> LTS:
        """
        startState ->  lts.startState <-> lts.endState -> endState
        """
        lts_inner = self.rex.rex2lts(first_state + 1)
        start, end = first_state, lts_inner.end + 1
        transitions = lts_inner.transitions

        transitions.add(LabelledTransition(start, lts_inner.start, "", ))
        transitions.add(LabelledTransition(lts_inner.end, end, "", ))
        transitions.add(LabelledTransition(lts_inner.end, lts_inner.start, "", ))
        transitions.add(LabelledTransition(lts_inner.start, lts_inner.end, "", ))

        return LTS(start,
                   end,
                   set(range(start, end + 1)),
                   transitions,
                   )
