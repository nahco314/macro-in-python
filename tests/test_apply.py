from contextlib import redirect_stdout
from io import StringIO

from macro_in_python import apply, macro


def test_chmax():
    @macro
    def chmin(a, b):
        a = min(a, b)

    @macro
    def chmax(a, b):
        [__b := b, a < __b, a := max(a, __b)][1]

    @apply(chmin, chmax)
    def test():
        a = 0
        b = 0
        chmin(a, -3)
        print(a, b, chmax(b, chmax(a, 3)), a, b)

    s = StringIO()

    with redirect_stdout(s):
        test()

    assert s.getvalue() == "-3 0 True 3 True\n"
