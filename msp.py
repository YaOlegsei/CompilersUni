from typing import Set, Dict, List, Tuple, Sequence, Optional
from collections import defaultdict


class Transition:
    def __init__(self,
                 from_state: int,
                 to_state: int,
                 label: str,
                 ):
        self.from_state = from_state
        self.to_state = to_state
        self.label = label


class LTS:
    def __init__(self,
                 start: int,
                 end: int,
                 states: Set[int],
                 transitions: Set[Transition],
                 tokens: Set[str],
                 ):
        self.start = start
        self.end = end
        # self.tokens = tokens
        self.states = states
        self.transitions = transitions

        trans_dict: Dict[Tuple[int, str], List[Transition]] = defaultdict(list)
        for tr in transitions:
            trans_dict[(tr.from_state, tr.label)].append(tr)
        self.trans_from_lbl = dict(trans_dict)

    def __get_suitable_transitions__(self, from_state: int, label: str) -> Optional[List[Transition]]:
        return self.trans_from_lbl.get((from_state, label))

    def __get_reachable_states__(self, states: List[int]) -> Set[int]:
        result_set = set(states)
        added = list(result_set)
        while added:
            current_state = added.pop()
            suitable_transitions = self.__get_suitable_transitions__(current_state, "")

            # if no epsilon transitions
            if suitable_transitions is None:
                continue
            for transition in suitable_transitions:
                # to prevent cycles
                if transition.to_state not in result_set:
                    result_set.add(transition.to_state)
                    added.append(transition.to_state)
        return result_set

    def accepts(self, chain: Sequence[str]) -> bool:

        expected_length = len(chain)

        reached_states = {(x, 0) for x in self.__get_reachable_states__([self.start])}

        while reached_states:
            current_state, current_length = reached_states.pop()

            if current_length == expected_length and current_state == self.end:
                return True

            if current_length >= expected_length:
                continue

            current_label = chain[current_length]

            to_transitions = self.__get_suitable_transitions__(current_state, current_label)

            if to_transitions:
                new_states = list(map(lambda tr: tr.to_state, to_transitions))

                reached_states.update([(x, current_length + 1) for x in self.__get_reachable_states__(new_states)])
        return False
