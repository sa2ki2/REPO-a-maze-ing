# A-Maze-ing

## Description

A-Maze-ingは42cursus Milestone 2の迷路生成課題です。迷路の生成、最短経路の導出、ターミナル上でのビジュアライズを行います。

- 迷路生成: recursive backtrackerによる深さ優先探索（DFS）
- 最短経路: 幅優先探索（BFS）
- 表示: ANSIエスケープシーケンスを利用したASCII rendering
- 製作者: skurita、sozawa

`PERFECT=True`では完全迷路を生成します。`PERFECT=False`では、ループを持ち、dead-endが存在しないbraided mazeを生成します。

## Requirements

### Mandatory

1. `config.txt`で迷路の幅、高さ、入口、出口などを指定できる。
2. `SEED`によって同じ迷路を再現できる。
3. 各セルは東西南北の壁を0から4個持つ。
4. 入口と出口は異なり、迷路内に存在する。
5. 3 x 3以上のオープンスペースを作らない。
6. 十分なサイズの迷路では中央に42のパターンを表示する。
7. `PERFECT=True`では任意の2点間の経路が1つになる。
8. `PERFECT=False`では42パターン内部の閉じた装飾セルを除く全通路が到達可能で、四隅と中央が開いており、複数の経路を持つ。
9. 迷路が小さく42を配置できない場合は、その旨を表示する。
10. 課題仕様の16進数形式で迷路をファイルへ出力する。
11. ASCII renderingで迷路を表示する。
12. Python wheelパッケージとしてビルドできる。

### Bonus

- `PERFECT=False`の迷路をdead-end 0のbraided boardとして生成する。
- 迷路生成のアニメーションを表示する。

## Usage

```bash
make run
```

デフォルトの`config.txt`は次の設定です。

```text
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
SEED=42
```

実行後のメニューでは、次の操作を選択できます。

1. 迷路を再生成する
2. 最短経路の表示・非表示を切り替える
3. 壁の色を変更する
4. 迷路生成アニメーションを表示する
5. 終了する

生成した迷路は、次のコマンドで解析できます。

```bash
make analyze
make analyze-bonus
```

`make analyze-bonus`は、解析スクリプトを`--max-dead-ends 0`で実行し、braided boardの条件を確認します。

### Configuration errors

`config.txt`に問題がある場合は、処理を開始せず、行番号付きのエラーをstderrへ表示して終了します。次のような入力を検出します。

- `KEY=VALUE`形式でない行
- 未知のキー、重複したキー、空の値
- 数値・真偽値・座標の形式不正
- `PERFECT`に大文字小文字を含めて厳密に`True`または`False`以外を指定
- 必須キー（`WIDTH`、`HEIGHT`、`ENTRY`、`EXIT`、`OUTPUT_FILE`、`PERFECT`）の欠落
- `WIDTH`と`HEIGHT`の範囲外
- 迷路の範囲外にあるEntry / Exit
- EntryとExitが同じ座標

例:

```text
Config error:
line 3: ENTRY: must contain exactly two comma-separated integers (x,y)
```

## Algorithms

### Maze generation

recursive backtrackerは、現在のセルから未訪問の隣接セルを選び、壁を壊して移動します。進めるセルがなくなった場合は、親セルへ戻って探索を続けます。全セルを訪問するまでこの処理を繰り返すため、DFSとして動作します。

生成直後の迷路は木構造です。`PERFECT=False`の場合は、四隅と中央を開けた後、dead-endがなくなるまで壁を追加で壊します。これにより、追跡中にプレイヤーが行き止まりへ閉じ込められないbraided mazeになります。42パターン内部の閉じた装飾セルは到達可能でなくてもよいものとして扱います。

### Shortest path

BFSで入口から出口まで探索し、各セルの親を記録します。出口へ到達した後、親を逆にたどることで最短経路を復元します。

### Maze output

迷路内部では、壁を次のビットで管理します。

| Bit | Direction |
| --- | --- |
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

出力時には課題仕様のビット順へ変換し、迷路本体、空行、入口座標、出口座標、経路の方角文字列を順に書き込みます。

## Visualization

ANSIエスケープシーケンスで壁、通路、入口、出口、42、最短経路に色を付けます。迷路生成アニメーションでは、壁を壊した履歴を順番に再生します。

## Packaging

wheelをビルドするには次を実行します。

```bash
make review
```

別のプロジェクトから利用する場合は、次のようにインポートできます。

```python
from mazegen import Config, MazeGenerator

config = Config(
    WIDTH=20,
    HEIGHT=15,
    ENTRY=(0, 0),
    EXIT=(19, 14),
    OUTPUT_FILE="maze.txt",
    PERFECT=False,
)

maze = MazeGenerator(config)
maze.maze_gen()
```

## Project structure

```text
a-maze-ing
├── a_maze_ing.py
├── config.txt
├── maze_analyzer.py
├── mazegen
│   ├── __init__.py
│   ├── bfs.py
│   ├── maze_gen_recursive.py
│   ├── maze_generator.py
│   └── visualizer.py
├── Makefile
├── pyproject.toml
└── README.md
```

## Resources

- [Jamis Buck - Maze algorithms](https://www.jamisbuck.org/mazes/)
- [深さ優先探索、幅優先探索の解説](https://manabitimes.jp/math/1247)
- [ANSIエスケープシーケンスの解説](https://docsaid.org/ja/blog/colorful-cli-with-ansi-escape-codes/)
