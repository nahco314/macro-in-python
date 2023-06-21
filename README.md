# macro-in-python

[日本語版の `README.md`](https://github.com/nahco314/macro-in-python/blob/master/README.ja.md)

Using Macros in Python.

## Usage

There are two ways to use macros.
1. import `macro_in_python`, write a macro in your code, and execute it as is.
2. To execute the code using macros without depending on the `macro_in_python` library, by extracting the macros with the `macro-in-python` command.

The following is a detailed explanation of how to use each of these commands.

### 1st
`from macro_in_python import macro, apply` imports the decorators needed to define and use macros.

A function defined with the `@macro` decorator becomes a macro.
- If the function contains a single expression statement, it becomes an expression macro and can be used as an expression.
- If the content of the function is a statement, it is a statement macro. A statement macro cannot be used as an expression.

`@apply(...)` You can use a macro in a function defined with a decorator. The argument lists the macros you want to use.

Example:
```python
from macro_in_python import macro, apply


@macro
def chmin(a, b): # statement macro
    a = min(a, b)


@macro
def add_1(a): # expression macro
    a + 1


@apply(chmin, add_1)
def main():
    a = 10
    chmin(a, add_1(4))
    print(a)
    # => 5
```

### 2nd

```
macro-in-python SOURCE OUTPUT
```
`SOURCE` is the path to the target Python file, and `OUTPUT` is the path to the file that will output the result of the macro expansion.

The contents of the target Python file are written in the first usage of the macro. In the expanded file, any extra imports or decorators will be erased.

````
$ cat ./test.py
from macro_in_python import apply, macro

@macro
def chmin(a, b):  # statement macro
    a = min(a, b)

@macro
def add_1(a):  # expression macro
    a + 1

@apply(chmin, add_1)
def main():
    a = 10
    chmin(a, add_1(4))
    print(a)

$ macro-in-python ./test.py ./test-out.py
Done.
$ cat ./test-out.py
def main():
    a = 10
    a = min(a, 4 + 1)
    print(a)
````

## Installation
If you want to install it as a tool (in the second usage), first install [rye](https://rye-up.com/guide/installation/).
```commandline
rye install macro-in-python --git https://github.com/nahco314/macro-in-python.git
````

If you want to install it as a library (for the 1st usage), install it as a normal library. For now, it is not registered with PyPI, so you can install it using the git specification.
```
# If you use rye:
rye add macro-in-python --git https://github.com/nahco314/macro-in-python.git
# If you use pip:
pip install git+https://github.com/nahco314/macro-in-python.git
```

## Examples
In C++, chmin, for example, can be used as an expression to return a bool indicating whether or not an update has been made.

In Python, chmin is normally written as a statement, so you can't do this, but in Python 3.8 and later, with the introduction of assignment expressions, you can write chmin/chmax to return a bool.

```python
@macro
def chmin(a, b):  # statement macro version
    a = min(a, b)

@macro
def chmax(a, b):  # expression macro version
    # return True if updated
    [__b := b, a < __b, a := max(a, __b)][1].

@apply(chmin, chmax)
def test():
    a = 0
    b = 0
    chmin(a, -3)
    print(a, b, chmax(b, chmax(a, 3)), a, b)
    # => -3 0 True 3 True
```
