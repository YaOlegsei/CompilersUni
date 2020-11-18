from rex import Symbol, KleneeStar, Union, Concatenation

if __name__ == "__main__":
    a_lts = Symbol('a').rex2lts()
    assert a_lts.accepts("a")
    assert not a_lts.accepts("b")

    ab_union_lts = Union(Symbol("a"), Symbol("b"))

    assert ab_union_lts.accepts("a")
    assert ab_union_lts.accepts("b")
    assert not ab_union_lts.accepts("ab")

    concat = Concatenation(Symbol("a"), Symbol("b"))

    ab_concat_lts = concat.rex2lts()

    assert ab_concat_lts.accepts("ab")
    assert not ab_concat_lts.accepts("a")
    assert not ab_concat_lts.accepts("b")

    ab_star_lts = KleneeStar(concat).rex2lts()
    assert ab_star_lts.accepts("")
    assert ab_star_lts.accepts("ababab")
    assert not ab_star_lts.accepts("aaaa")
