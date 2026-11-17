This project has been created as part
of the 42 curriculum by *skurita*, *sozawa*.

# A-Maze-ing

42 Tokyoの課題「A-Maze-ing」の迷路生成プログラムです。迷路を生成し、
入口から出口までの最短経路を求め、ターミナル上で表示します。

## Description

設定ファイルから迷路のサイズ、入口、出口、完全迷路モード、乱数シードを読み込み、
迷路を生成します。生成した迷路は16進数形式で保存され、入口から出口までの最短経路と
ともに解析できます。十分な大きさの迷路では中央に42パターンも表示します。

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

## Instructions

### 準備

Python 3.10以上が必要です。次のコマンドで仮想環境を作成し、依存関係をインストール
できます。

```bash
make install
```

### 実行

```bash
make run
# または
python3 a_maze_ing.py config.txt
```

実行時は、まず迷路を生成して `OUTPUT_FILE` に保存し、その後ターミナルのメニューを
表示します。メニューでは再生成、最短経路の表示切り替え、壁色変更、生成アニメーション、
終了を選択できます。

### 解析・品質確認

```bash
make analyze
make analyze-bonus
make lint
make lint-strict
```

`analyze-bonus` は行き止まり0件も検証します。wheelのビルドと別環境での実行確認には
`make review` を使用します。

### 迷路の生成

```bash
make run
```

`make run` は `.venv` を作成し、依存関係をインストールした後、次を実行します。

```bash
python3 a_maze_ing.py config.txt
```

設定ファイルは、空行と `#` から始まるコメントを除き、1行1項目の `KEY=VALUE` 形式です。
キーは大文字で記述し、同じキーを複数回指定できません。必須キーは `WIDTH`、`HEIGHT`、
`ENTRY`、`EXIT`、`OUTPUT_FILE`、`PERFECT` で、`SEED` は任意です。

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

| キー | 型・形式 | 必須 | 説明 |
| --- | --- | --- | --- |
| `WIDTH` | 整数（3以上） | はい | 迷路の幅 |
| `HEIGHT` | 整数（3以上） | はい | 迷路の高さ |
| `ENTRY` | `x,y` | はい | 入口の座標。迷路内で出口と異なること |
| `EXIT` | `x,y` | はい | 出口の座標。迷路内で入口と異なること |
| `OUTPUT_FILE` | 文字列 | はい | 出力先ファイル |
| `PERFECT` | `True` / `False` | はい | 完全迷路か、ループを許可するか |
| `SEED` | 整数 | いいえ | 乱数の再現性を決める値。省略時は `42` |

座標の `x` は左から右、`y` は上から下へ増加します。設定に問題がある場合は、
行番号付きのエラーを表示して迷路生成を開始しません。

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

### 再利用ドキュメント

#### 基本例

```python
from mazegen import Config, MazeGenerator
from mazegen.bfs import BreadthFirstSearch

config = Config(
    WIDTH=20, HEIGHT=15, ENTRY=(0, 0), EXIT=(19, 14),
    OUTPUT_FILE="maze.txt", PERFECT=False, SEED=42,
)
generator = MazeGenerator(config)
generator.maze_gen()
search = BreadthFirstSearch(generator._pos, config)
search.search_maze()
generator.output_to_file(search._path_cardinal)
```

#### カスタムパラメータ

`WIDTH`、`HEIGHT`、`ENTRY`、`EXIT`、`OUTPUT_FILE`、`PERFECT`、`SEED` を
`Config` の引数で変更できます。`SEED` を固定すると同じ入力から同じ乱数系列を
再現できます。`PERFECT=False` では四隅と中央を開通し、ループを持つ迷路を生成します。

#### 構造・解へのアクセス

- 生成済みセルは `generator._pos[x][y]`（`Cell`）から参照できます。
- `Cell.value` は内部表現の壁ビット（`N=8, E=4, S=2, W=1`）です。
- `search._path` は入口から出口までの座標リストです。
- `search._path_cardinal` は最短経路の方角文字列です。
- `generator.output_to_file(...)` で課題仕様のファイル形式へ変換して保存できます。

`_pos` や `_path` は再利用時に利用する内部データ構造です。出力ファイルを別プログラム
から読む場合は、`maze_analyzer.py` の `Maze.from_file()`、`walls()`、`passages()`、
`region_of()` などの解析 API を利用できます。

## 採用アルゴリズムと選定理由

- **迷路生成: recursive backtracker（DFS）**
  未訪問セルへ進み、行き止まりで直前のセルへ戻る方法です。実装が小さく、
  すべてのプレイ可能セルを連結しやすく、課題の完全迷路を自然に生成できるため採用
  しました。プロジェクトでは生成戦略をこの1種類に統一しています。
- **最短経路: BFS**
  入口から距離の近い順に探索するため、各移動コストが同じ迷路で最短経路を保証します。
- **検証: グラフ探索と壁ビット検査**
  共有壁、到達可能領域、ループ、行き止まりなどを独立したアナライザーで確認し、
  生成処理と検証処理を分離しています。

## 再利用可能な部分とその使い方

| 部分 | 再利用方法 |
| --- | --- |
| `Config` | 迷路設定の型・範囲検証に利用 |
| `MazeGenerator` | `Config` を渡して迷路を生成 |
| `BreadthFirstSearch` | 生成済みセルと設定を渡して最短経路を取得 |
| `Visualizer` | セル、設定、経路、生成履歴を渡してターミナル表示 |
| `maze_analyzer.Maze` | 保存済み16進数迷路を読み込み、構造を検査 |

## 高度な機能

実装済みの追加機能として、42パターン、生成アニメーション、最短経路の表示切り替え、
壁色変更、厳密な設定エラー報告、迷路解析、wheelのビルドと別環境での動作確認があります。
`PERFECT=False` では行き止まり0件を目指し、3 x 3以上の開放空間を検出した生成結果は
再生成します。42パターンの完全に閉じた装飾セルは、到達可能性の検査対象外です。

## チーム管理

> この節は提出時に実際の分担・計画へ置き換えるための記録欄です。

- **役割**: `skurita` — [担当を記入] / `sozawa` — [担当を記入]
- **計画と推移**: [課題分解、実装順、レビュー・統合の流れを記入]
- **良かった点**: [うまくいった協力方法や判断を記入]
- **改善点**: [次回改善する点を記入]
- **使用ツール**: Git、GitHub、`make`、flake8、mypy、[その他を記入]

## Resources（参考資料 + AI使用の詳細）

### 参考資料

- [Jamis Buck - 迷路アルゴリズム](https://www.jamisbuck.org/mazes/)
- [深さ優先探索、幅優先探索の解説](https://manabitimes.jp/math/1247)
- [ANSIエスケープシーケンスの解説](https://docsaid.org/ja/blog/colorful-cli-with-ansi-escape-codes/)

### AIの利用

調査、コードレビュー、デバッグ、ドキュメント作成の補助としてAIツールを使用しました。
AIによる提案は作者が確認・修正・テストしたうえで採用しており、最終的な実装については
作者が責任を負います。具体的な利用内容は、アルゴリズムの整理、設定検証・到達可能性の
確認、`MEMO.md` に記録した不具合修正の説明整理、READMEの構成改善です。

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
