*This project has been created as part
of the 42 curriculum by skurita, sozawa*

# A-Maze-ing

42 Tokyoの課題「A-Maze-ing」の迷路生成プログラムです。迷路を生成し、
入口から出口までの最短経路を求め、ターミナル上で表示します。

## Features

- recursive backtracker（深さ優先探索、DFS）による迷路生成
- BFSによる入口から出口までの最短経路探索
- `PERFECT=True` の完全迷路と、ループを持つ `PERFECT=False` の迷路
- `PERFECT=False` での四隅・中央の開通と、実際の行き止まり0の迷路生成
- 迷路が十分な大きさの場合の中央の `42` パターン表示
- ANSIエスケープシーケンスによるターミナル表示
- 迷路生成アニメーション、最短経路表示、壁色変更
- 42課題仕様の16進数形式でのファイル出力
- 生成済み迷路の整合性・到達可能性・ループ・行き止まりの解析

`42` パターン内の完全に閉じた装飾セルは、到達可能でなくてもよいものとして
扱います。迷路のプレイ可能な通路は入口から出口まで到達可能である必要があります。

## Requirements

- Python 3.10以上
- `pydantic`
- `build`（wheelのビルドに使用）

依存関係は `requirements.txt` に固定されています。

## Usage

### 迷路の生成

```bash
make run
```

`make run` は `.venv` を作成し、依存関係をインストールした後、次を実行します。

```bash
python3 a_maze_ing.py config.txt
```

設定ファイルは `KEY=VALUE` 形式です。現在のデフォルト設定は次のとおりです。

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

`SEED` は任意です。省略した場合は `42` が使用されます。

生成後はインタラクティブメニューから次を選択できます。

1. 迷路を再生成
2. 最短経路の表示・非表示
3. 壁色の変更
4. 迷路生成アニメーション
5. 終了

### 迷路の解析

```bash
make analyze
make analyze-bonus
```

`make analyze` は `maze.txt` を解析します。`make analyze-bonus` は
`--max-dead-ends 0` を指定し、行き止まりがないことも確認します。
直接実行する場合は次の形式です。

```bash
python3 maze_analyzer.py maze.txt [--min-loops N] [--max-dead-ends N]
```

### 設定エラー

設定ファイルに問題がある場合、迷路生成を開始せず、行番号付きのエラーを
標準エラー出力へ表示して終了します。次の入力を検証します。

- `KEY=VALUE` 形式、未知のキー、重複したキー、空の値
- 必須キー（`WIDTH`、`HEIGHT`、`ENTRY`、`EXIT`、`OUTPUT_FILE`、`PERFECT`）
- 数値・座標・真偽値の形式
- `WIDTH`、`HEIGHT`、`ENTRY`、`EXIT` の範囲
- `ENTRY` と `EXIT` が異なること

`PERFECT` に指定できる値は大文字小文字を含めて `True` または `False` だけです。

## Output format

`OUTPUT_FILE` には、次の順で出力されます。

1. 迷路本体（各セル1文字の16進数、`HEIGHT` 行）
2. 空行
3. 入口座標（`x,y`）
4. 出口座標（`x,y`）
5. 最短経路の方角文字列

迷路内部では壁を `N=8`、`E=4`、`S=2`、`W=1` のビットで管理し、出力時に
課題仕様のビット順へ変換します。

## Packaging and checks

```bash
make lint          # flake8とmypy
make lint-strict   # strict設定のflake8とmypy
make review        # wheelをビルドし、別環境へインストールして実行
```

wheelだけをビルドする場合は次を実行します。

```bash
python3 -m build
```

## Python API

`mazegen` パッケージから設定、生成器、ビジュアライザーを利用できます。

```python
from mazegen import Config, MazeGenerator

config = Config(
    WIDTH=20,
    HEIGHT=15,
    ENTRY=(0, 0),
    EXIT=(19, 14),
    OUTPUT_FILE="maze.txt",
    PERFECT=False,
    SEED=42,
)

maze = MazeGenerator(config)
maze.maze_gen()
```

## Project structure

```text
.
├── a_maze_ing.py             # メインエントリーポイント
├── config.txt                # 迷路設定のサンプル
├── maze_analyzer.py          # 出力ファイルの解析
├── mazegen/
│   ├── __init__.py
│   ├── bfs.py                # 最短経路探索
│   ├── maze_gen_recursive.py # recursive backtracker
│   ├── maze_generator.py     # 設定・共通処理・出力
│   └── visualizer.py         # ターミナル表示
├── Makefile
├── pyproject.toml
├── requirements.txt
└── README.md
```



## 参考資料

- [Jamis Buck - 迷路アルゴリズム](https://www.jamisbuck.org/mazes/)
- [深さ優先探索、幅優先探索の解説](https://manabitimes.jp/math/1247)
- [ANSIエスケープシーケンスの解説](https://docsaid.org/ja/blog/colorful-cli-with-ansi-escape-codes/)

## AIの利用

調査、コードレビュー、デバッグ、ドキュメント作成の補助としてAIツールを
使用しました。AIによる提案は作者が確認・修正・テストしたうえで採用しており、
最終的な実装については作者が責任を負います。
