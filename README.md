# Python Application Launcher

JSONファイルに登録したPythonアプリケーションを、CLIメニューから選択して起動するシンプルなランチャーです。

アプリごとに使用する仮想環境を指定できます。仮想環境を指定しない場合は、`python`
コマンドを使用します。起動したアプリはランチャーとは別のコンソールで実行されます。

## 特徴

-   JSONファイルからアプリ一覧を読み込み
-   CLIメニューから番号を選択して起動
-   アプリごとに仮想環境を指定可能
-   仮想環境を指定しない場合は `python` コマンドを使用
-   起動したアプリは別コンソールで実行
-   アプリの追加・変更はJSONファイルの編集だけで対応
-   PC固有の設定と配布用テンプレートを分離

## ファイル構成

``` text
python_application_launcher/
├─ launcher.py
├─ launcher_apps.json
├─ template_launcher_apps.json
├─ .gitignore
└─ README.md
```

### `launcher.py`

ランチャー本体です。`launcher_apps.json`
を読み込み、登録されたアプリをCLIメニューとして表示します。

### `launcher_apps.json`

実際に使用する設定ファイルです。アプリや仮想環境の絶対パスを記述するため、PCごとに内容が異なります。

そのためGitでは管理しません。

### `template_launcher_apps.json`

`launcher_apps.json` を作成するための配布用テンプレートです。

## 設定ファイル

基本形式は次のとおりです。

``` json
{
    "Tool A": {
        "app_path": "C:\\myProgram\\tool_a\\tool_a.py",
        "venv_path": "C:\\myProgram\\tool_a\\.venv"
    },
    "Tool B": {
        "app_path": "C:\\myProgram\\tool_b\\tool_b.py"
    }
}
```

JSONのキーが、ランチャーのメニューに表示されるアプリ名称になります。

### `app_path`

起動するPythonプログラムの絶対パスです。必須項目です。

``` json
"app_path": "C:\\myProgram\\tool_a\\tool_a.py"
```

### `venv_path`

使用するPython仮想環境のフォルダを絶対パスで指定します。

``` json
"venv_path": "C:\\myProgram\\tool_a\\.venv"
```

指定した場合、次のPythonを使用します。

``` text
<venv_path>\Scripts\python.exe
```

例えば上記設定なら、

``` text
C:\myProgram\tool_a\.venv\Scripts\python.exe
```

でアプリを起動します。

## 仮想環境を使用しない場合

`venv_path` は省略できます。

``` json
{
    "Tool B": {
        "app_path": "C:\\myProgram\\tool_b\\tool_b.py"
    }
}
```

この場合は、次のような実行になります。

``` text
python C:\myProgram\tool_b\tool_b.py
```

そのため、`python`
コマンドが使用できるようにPATHが設定されている必要があります。

## WindowsパスをJSONに記述する際の注意

JSONでは `\`
がエスケープ文字として使用されるため、Windowsのパスに含まれる `\` は
`\\` と記述します。

``` text
C:\myProgram\tool_a\tool_a.py
```

JSONでは、

``` json
"C:\\myProgram\\tool_a\\tool_a.py"
```

とします。

エクスプローラーの「パスのコピー」で取得したパスを貼り付ける場合は、`\`
を `\\` に変換してください。

## 使い方

### 1. `launcher_apps.json` を準備

`template_launcher_apps.json` を参考に、各PC用の `launcher_apps.json`
を作成します。

例：

``` json
{
    "Text Input Helper": {
        "app_path": "C:\\myProgram\\GitHub\\TOOLS\\text_input_helper\\app.py",
        "venv_path": "C:\\myProgram\\GitHub\\TOOLS\\text_input_helper\\.venv"
    }
}
```

### 2. ランチャーを起動

``` text
python launcher.py
```

### 3. アプリを選択

``` text
=== Python Application Launcher ===

1. Tool A
2. Tool B
3. Wi-Fi Switch Tool

0. Exit

Select application:
```

起動したいアプリの番号を入力します。`0` を入力すると終了します。

## アプリの起動方法

仮想環境が指定されている場合：

``` text
指定した仮想環境
        ↓
Scripts\python.exe
        ↓
対象のPythonプログラム
```

仮想環境が指定されていない場合：

``` text
python
   ↓
対象のPythonプログラム
```

このため、ランチャー自身を実行しているPython環境とは別に、各アプリで使用するPython環境を選択できます。

## 別コンソールでの起動

アプリは `subprocess.Popen()` と `CREATE_NEW_CONSOLE`
を使用して起動します。

``` text
Launcher Console

Tool A Console

Tool B Console
```

各アプリの出力や `input()`
がランチャー側に混在しないため、CLIツールを扱いやすくなります。

## アプリを追加する方法

`launcher.py` の変更は不要です。`launcher_apps.json`
に設定を追加します。

``` json
{
    "Tool A": {
        "app_path": "C:\\myProgram\\tool_a\\tool_a.py",
        "venv_path": "C:\\myProgram\\tool_a\\.venv"
    },
    "New Tool": {
        "app_path": "C:\\myProgram\\new_tool\\main.py",
        "venv_path": "C:\\myProgram\\new_tool\\.venv"
    }
}
```

次回起動時から `New Tool` がメニューに表示されます。

## `.gitignore`

``` gitignore
# ================================================
# Local settings
# ================================================
launcher_apps.json


# ================================================
# Python virtual environments
# ================================================
.venv/
venv/
env/


# ================================================
# Python cache
# ================================================
__pycache__/
*.py[cod]
```

`launcher_apps.json` はPC固有の絶対パスを含むためGit管理から除外します。

代わりに `template_launcher_apps.json`
をGitで管理し、新しいPCではテンプレートを基に設定ファイルを作成します。

## 動作環境

-   Windows
-   Python
-   Python標準ライブラリのみ使用

主な使用モジュール：

``` python
import json
import subprocess
from pathlib import Path
```

追加パッケージのインストールは不要です。

## 補足

このランチャーはWindows用です。

仮想環境のPythonを、

``` text
<venv_path>\Scripts\python.exe
```

として扱い、`CREATE_NEW_CONSOLE`
で別コンソールを作成するため、Windows以外のOSでそのまま使用することは想定していません。
