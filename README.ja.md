# macro-in-python

Pythonでマクロを使えるようにするライブラリ・ツールです。

## 使い方

マクロの使用方法は2つあります。
1. `macro_in_python` をインポートし、コードの中にマクロを記述し、それをそのまま実行する
2. マクロを用いたコードに対し、予め `macro-in-python` コマンドでマクロの展開を行い、 `macro_in_python` ライブラリに依存しない形で実行する

それぞれ詳しい使い方を説明します。

### 1つ目
`from macro_in_python import macro, apply` でマクロの定義・使用に必要なデコレータをインポートします。

`@macro` デコレータを付けて定義された関数は、マクロとなります。
- 関数の中身が単一の式文ならば、それは式マクロとなり、式として使えます。
- 中身が文ならば、文マクロとなります。文マクロは式として使うことはできません。

`@apply(...)` デコレータを付けて定義された関数の中で、マクロを使用することができます。引数には、使用したいマクロを列挙します。

例:
```python
from macro_in_python import macro, apply


@macro
def chmin(a, b):  # 文マクロ
    a = min(a, b)


@macro
def add_1(a):  # 式マクロ
    a + 1


@apply(chmin, add_1)
def main():
    a = 10
    chmin(a, add_1(4))
    print(a)
    # => 5
```

### 2つ目

```
macro-in-python SOURCE OUTPUT
```
`SOURCE` は対象となるPythonファイルのパスで、 `OUTPUT` はマクロを展開した結果を出力するファイルのパスです。

対象となるPythonファイルの中身は、1つ目の使い方の書き方でマクロを記述します。展開後のファイルでは、余分なインポートやデコレータは消去されます。

```
$ cat ./test.py
from macro_in_python import apply, macro

@macro
def chmin(a, b):  # 文マクロ
    a = min(a, b)

@macro
def add_1(a):  # 式マクロ
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
```

## インストール
ツールとして(2つ目の使い方で)インストールする場合、まず [rye](https://rye-up.com/guide/installation/) をインストールしてください。
```commandline
rye install macro-in-python --git https://github.com/nahco314/macro-in-python.git
```

ライブラリとして(1つ目の使い方で)インストールする場合は、普通にライブラリとしてインストールするようにしてください。今のところ PyPI に登録していないので、git指定でインストールしてください。
```
# rye を使う場合:
rye add macro-in-python --git https://github.com/nahco314/macro-in-python.git
# pip を使う場合:
pip install git+https://github.com/nahco314/macro-in-python.git
```

## 例
C++ で一般的に使われる chmin などは式として使えて、更新したかどうかの bool を返します。

Python で普通に chmin を書くと文になるのでこのようなことはできませんが、代入式が導入された Python3.8 以降では bool を返す chmin/chmax を書くことができます。

```python
@macro
def chmin(a, b):  # 文マクロバージョン
    a = min(a, b)

@macro
def chmax(a, b):  # 式マクロバージョン
    # 更新されたら True を返す
    [__b := b, a < __b, a := max(a, __b)][1]

@apply(chmin, chmax)
def test():
    a = 0
    b = 0
    chmin(a, -3)
    print(a, b, chmax(b, chmax(a, 3)), a, b)
    # => -3 0 True 3 True
```
