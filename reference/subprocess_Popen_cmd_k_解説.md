# `subprocess.Popen()` で別コンソールからPythonアプリを起動する方法

## 1. 今回の目的

Python製のランチャーから別のPythonアプリを起動するとき、次のようにしたい。

-   起動対象アプリは**ランチャーとは別のコンソール**で実行する
-   起動対象アプリが終了しても、コンソールをすぐ閉じない
-   異常終了した場合も、Tracebackなどのエラー表示を残す
-   ランチャー自身は、起動対象アプリの終了を待たない

今回使用したコードは次のとおり。

``` python
subprocess.Popen(
    [
        "cmd",
        "/k",
        str(python_path),
        str(app_path),
    ],
    cwd=app_path.parent,
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)
```

一見すると少し複雑だが、役割ごとに分解すると理解しやすい。

------------------------------------------------------------------------

## 2. 全体として何をしているのか

大まかな流れは次のようになる。

``` text
ランチャー
    │
    └─ subprocess.Popen()
           │
           └─ 新しいコンソールを作る
                  │
                  └─ cmd.exe を起動
                         │
                         └─ Pythonを実行
                                │
                                └─ 対象の.pyファイルを実行
```

さらに `cmd /k` を使用しているため、Pythonアプリが終了しても `cmd.exe`
は終了しない。

そのため、コンソール画面が残る。

------------------------------------------------------------------------

# 3. `subprocess` とは

`subprocess` は、Pythonから別のプログラムやコマンドを実行するための
標準ライブラリである。

今回のプログラムでは冒頭で次のように読み込んでいる。

``` python
import subprocess
```

例えばPythonからWindowsの `ipconfig` を実行することもできる。

``` python
subprocess.run(["ipconfig"])
```

つまり、

> Pythonから別プロセスを起動するための機能

と考えると分かりやすい。

------------------------------------------------------------------------

# 4. `Popen()` とは

今回使用しているのは次の命令である。

``` python
subprocess.Popen(...)
```

`Popen` は **新しいプロセスを開始する**ための機能である。

今回の場合は、

``` text
ランチャーのPython
        ↓
新しい cmd.exe
        ↓
起動対象のPython
```

という別プロセスを作っている。

## `run()` との大きな違い

よく使われるものに次の命令もある。

``` python
subprocess.run(...)
```

基本的には、

``` text
subprocess.run()
    → 起動した処理の終了を待つ

subprocess.Popen()
    → 起動したあと、呼び出し元はそのまま先へ進める
```

という違いがある。

ランチャーでは、起動したアプリの終了までランチャーを待たせる必要がないため、
`Popen()` が適している。

------------------------------------------------------------------------

# 5. 第1引数のリスト

``` python
[
    "cmd",
    "/k",
    str(python_path),
    str(app_path),
]
```

ここが「何を実行するか」を指定している部分である。

それぞれを順番に見る。

------------------------------------------------------------------------

## 5.1 `"cmd"`

``` python
"cmd"
```

これはWindowsの **コマンドプロンプト（cmd.exe）** を起動する指定である。

Windows上で、

``` cmd
cmd
```

と実行するのと同じ考え方である。

今回、Pythonを直接起動するのではなく、一度 `cmd.exe` を起動している。

``` text
ランチャー
   ↓
cmd.exe
   ↓
Python
```

この `cmd.exe` を間に入れることによって、Python終了後も
コンソールを残せるようにしている。

------------------------------------------------------------------------

# 6. `/k` とは

``` python
"/k"
```

これは `cmd.exe` のオプションである。

意味は、

> 指定されたコマンドを実行したあとも、cmd.exeを終了しない

である。

イメージとしては、

``` cmd
cmd /k python sample.py
```

を実行している。

`sample.py` が終了しても、

``` text
C:\some_folder>
```

というコマンドプロンプトが残る。

そのため、Pythonでエラーが発生した場合でも、

``` text
Traceback (most recent call last):
    ...
ValueError: ...
```

などの表示を確認できる。

------------------------------------------------------------------------

# 7. `/c` と `/k` の違い

`cmd.exe` には `/c` という似たオプションもある。

## `/c`

``` cmd
cmd /c python sample.py
```

意味は、

> コマンドを実行して、その後cmd.exeを終了する

である。

そのためPythonが終了するとコンソールも閉じる。

## `/k`

``` cmd
cmd /k python sample.py
```

意味は、

> コマンドを実行して、その後もcmd.exeを残す

である。

今回はこちらを採用した。

まとめると、

  オプション   Python終了後
  ------------ -------------------
  `/c`         cmd.exeも終了する
  `/k`         cmd.exeを残す

エラー内容を確認したい開発用ランチャーでは `/k` が便利である。

------------------------------------------------------------------------

# 8. `str(python_path)`

``` python
str(python_path)
```

これは、実行するPythonの場所を指定している。

今回のランチャーでは仮想環境が指定されている場合、

``` python
python_path = (
    Path(venv_path)
    / "Scripts"
    / "python.exe"
)
```

としている。

例えば、

``` text
C:\myProgram\sample\.venv\Scripts\python.exe
```

のようなパスになる。

`Path` オブジェクトとして保持しているため、

``` python
str(python_path)
```

で文字列へ変換して `subprocess` に渡している。

仮想環境が指定されていない場合は、

``` python
python_path = "python"
```

となる。

この場合はWindowsのPATHから `python` を探して実行する。

------------------------------------------------------------------------

# 9. `str(app_path)`

``` python
str(app_path)
```

これは実行したいPythonファイルのパスである。

例えば、

``` text
C:\myProgram\sample\app.py
```

などが入る。

したがって、実際には概念的に次のコマンドを実行している。

``` cmd
cmd /k C:\...\python.exe C:\...\app.py
```

つまり、

``` text
cmd.exeを起動
    ↓
指定したPythonを起動
    ↓
指定した.pyファイルを実行
```

という流れになる。

------------------------------------------------------------------------

# 10. なぜリスト形式で書くのか

今回のコードでは、

``` python
[
    "cmd",
    "/k",
    str(python_path),
    str(app_path),
]
```

とリストで指定している。

これは非常に重要である。

例えば全部を1つの文字列にすると、

``` python
command = f'cmd /k "{python_path}" "{app_path}"'
```

のようになる。

しかしWindowsのコマンドラインでは、

-   スペースを含むパス
-   ダブルクォーテーション
-   `cmd.exe` 独自の解釈

などが絡むため、引用符の扱いが複雑になりやすい。

リスト形式なら、

``` python
[
    "cmd",
    "/k",
    str(python_path),
    str(app_path),
]
```

のように、**引数を最初から別々の要素として扱える**。

今回のような用途では、こちらの方が読みやすく、トラブルも少ない。

------------------------------------------------------------------------

# 11. `cwd=app_path.parent`

``` python
cwd=app_path.parent,
```

`cwd` は、

**Current Working Directory**

の略である。

日本語では「カレントディレクトリ」「現在の作業フォルダ」などと呼ばれる。

`app_path` が、

``` text
C:\myProgram\sample\app.py
```

なら、

``` python
app_path.parent
```

は、

``` text
C:\myProgram\sample
```

になる。

つまり、

``` python
cwd=app_path.parent
```

によって、

> 起動対象Pythonファイルが置かれているフォルダを
> カレントディレクトリとして実行する

という指定をしている。

これは非常に重要である。

例えば起動対象アプリが、

``` python
JSON_FILE = "setting.json"
```

としている場合、Pythonはカレントディレクトリから `setting.json`
を探すことがある。

`cwd` を正しく指定しておけば、

``` text
sample/
├─ app.py
└─ setting.json
```

という構成で正常にファイルを見つけやすくなる。

------------------------------------------------------------------------

# 12. `creationflags=subprocess.CREATE_NEW_CONSOLE`

``` python
creationflags=subprocess.CREATE_NEW_CONSOLE,
```

これはWindowsで新しいプロセスを作るときの指定である。

`CREATE_NEW_CONSOLE` は、

> 新しいコンソールウィンドウを作成する

という意味を持つ。

これが今回のランチャーでは非常に重要である。

指定しない場合、起動したプログラムの出力がランチャー側のコンソールと
混ざる可能性がある。

指定すると、

``` text
┌──────────────────────────┐
│ ランチャーのコンソール   │
└──────────────────────────┘

           ＋

┌──────────────────────────┐
│ 起動アプリのコンソール   │
└──────────────────────────┘
```

というように別々の画面になる。

複数のPythonアプリをランチャーから起動する場合、
どのアプリのログなのか分かりやすくなる。

------------------------------------------------------------------------

# 13. コードを日本語にすると

今回のコード、

``` python
subprocess.Popen(
    [
        "cmd",
        "/k",
        str(python_path),
        str(app_path),
    ],
    cwd=app_path.parent,
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)
```

を日本語で表現すると、おおよそ次のようになる。

> 新しいコンソールウィンドウを作成して `cmd.exe` を起動する。\
> その `cmd.exe` から指定したPythonで指定したPythonファイルを実行する。\
> 作業フォルダは起動対象Pythonファイルのあるフォルダにする。\
> Pythonアプリが終了しても `cmd.exe` は終了させず、
> コンソール画面を残しておく。

------------------------------------------------------------------------

# 14. 実行時のイメージ

例えば、

``` python
python_path = Path(
    r"C:\myProgram\sample\.venv\Scripts\python.exe"
)

app_path = Path(
    r"C:\myProgram\sample\app.py"
)
```

だったとする。

ランチャーから見ると、概念的には、

``` cmd
cmd /k C:\myProgram\sample\.venv\Scripts\python.exe C:\myProgram\sample\app.py
```

のような処理を起動している。

そして、

``` python
cwd=app_path.parent
```

によってカレントディレクトリは、

``` text
C:\myProgram\sample
```

になる。

------------------------------------------------------------------------

# 15. 正常終了した場合

アプリが正常終了すると、例えば次のようになる。

``` text
Application started.

Processing...

Finished.

C:\myProgram\sample>
```

最後にコマンドプロンプトが残る。

確認後は、

``` cmd
exit
```

と入力するか、ウィンドウ右上の `×` で閉じればよい。

------------------------------------------------------------------------

# 16. 異常終了した場合

例えば起動対象Pythonで、

``` python
raise ValueError("Test error")
```

が発生した場合、

``` text
Traceback (most recent call last):
  ...
ValueError: Test error

C:\myProgram\sample>
```

のようにTracebackが画面に残る。

通常なら一瞬でコンソールが閉じて読めないエラーでも、 `cmd /k`
によって確認できる。

今回のランチャーで `/k` を使う大きな理由がこれである。

------------------------------------------------------------------------

# 17. `pause` との違い

Windows Batchでは、

``` bat
python app.py
pause
```

という書き方がよく使われる。

`pause` の場合は、

``` text
続行するには何かキーを押してください . . .
```

と表示され、キーを押すまで待機する。

一方、今回の `/k` は、

``` text
C:\myProgram\sample>
```

という通常のコマンドプロンプトに戻る。

つまり、

``` text
pause
    → キー入力待ち

cmd /k
    → コマンドプロンプトそのものを残す
```

という違いがある。

今回の目的は、

> 正常終了・異常終了に関係なく、実行結果を確認できるようにする

ことであるため、`cmd /k` でも十分目的を達成できる。

さらに、`pause` を文字列として組み込む場合に発生しやすい
Windowsの引用符処理を避けられる利点もある。

------------------------------------------------------------------------

# 18. 今回のコードで特に重要な3点

今回のランチャーを理解するときは、まず次の3つを覚えておけばよい。

### 1. `Popen()`

``` python
subprocess.Popen(...)
```

別プロセスを起動する。

### 2. `cmd /k`

``` text
cmd /k
```

コマンドを実行したあともコマンドプロンプトを残す。

### 3. `CREATE_NEW_CONSOLE`

``` python
creationflags=subprocess.CREATE_NEW_CONSOLE
```

ランチャーとは別のコンソールウィンドウを作る。

この3つを組み合わせることで、

``` text
ランチャー
    │
    ├─ アプリA用コンソール
    │      └─ 終了後も残る
    │
    └─ アプリB用コンソール
           └─ 終了後も残る
```

というランチャーらしい動作を実現できる。

------------------------------------------------------------------------

# 19. まとめ

今回採用したコードは次のとおり。

``` python
subprocess.Popen(
    [
        "cmd",
        "/k",
        str(python_path),
        str(app_path),
    ],
    cwd=app_path.parent,
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)
```

各部分の役割は次のようになる。

  コード                  役割
  ----------------------- ----------------------------------------------
  `subprocess.Popen()`    別プロセスを起動する
  `"cmd"`                 Windowsのコマンドプロンプトを起動する
  `"/k"`                  実行終了後もcmd.exeを閉じない
  `str(python_path)`      使用するPythonを指定する
  `str(app_path)`         実行するPythonファイルを指定する
  `cwd=app_path.parent`   起動対象アプリのフォルダを作業フォルダにする
  `CREATE_NEW_CONSOLE`    新しいコンソールウィンドウを作る

今回のランチャーでは、

**「別コンソールで起動」**

と

**「終了後もコンソールを残す」**

という2つの目的を、Windowsの `cmd /k` と `CREATE_NEW_CONSOLE`
を組み合わせることでシンプルに実現している。
