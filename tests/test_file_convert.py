from pathlib import Path
from tempfile import NamedTemporaryFile
from textwrap import dedent

from macro_in_python import convert_file


def test_convert_file():
    base = dedent(
        """\
        from macro_in_python import macro, apply
        import some_library
        from os import system
        
        
        @macro
        def chmin(a, b):
            [__b := b, a < __b, a := max(a, __b)][1]
        
        
        @macro
        def chmax(a, b):
            [__b := b, a < __b, a := max(a, __b)][1]
        
        
        @some
        @decorator
        @apply(chmin, chmax)
        def main():
            a = 0
            b = 1
            chmax(a, chmin(b, -2))
    
        """
    )

    expected = dedent(
        """\
        import some_library
        from os import system
        
        @some
        @decorator
        def main():
            a = 0
            b = 1
            [(__b := [(__b := (-2)), b < __b, (b := max(b, __b))][1]), a < __b, (a := max(a, __b))][1]
        """
    )

    with NamedTemporaryFile("r+") as f:
        f.write(base)
        f.flush()
        convert_file(Path(f.name), Path(f.name))

        f.seek(0)
        result = f.read()

    assert result.rstrip() == expected.rstrip()
