*This project has been created as part
of the 42 curriculum by skurita, sozawa.*

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

  ### 生成アニメーション

迷路生成時に `break_wall()` が記録する「どのセルのどの方向の壁を壊したか」という
履歴を、`Visualizer.show_animation()` が先頭から順番に再生します。アニメーション用に
全セルを壁ありの状態から作り直し、各ステップで実際の生成と同じ壁ビット操作を適用する
ため、recursive backtracker の探索過程を生成順に確認できます。

各ステップでは ANSI カラーで迷路を再描画し、`Generating maze (現在のステップ/総数)`
を表示します。表示間隔は 0.03 秒です。再生中は完成前の状態を見せるため最短経路を
一時的に非表示にし、終了後は元の迷路データ、最短経路の表示状態、壁色を維持したまま
完成した迷路を再表示します。42パターンの固定セル情報もアニメーション用データへ引き
継ぐため、装飾部分を壊さずに再生できます。

実行中のメニューで `4. Show maze generate animation` を選ぶと利用できます。生成履歴が
ない場合はメッセージを表示して通常メニューへ戻ります。

## 再利用可能な部分とその使い方

| 部分 | 再利用方法 |
| --- | --- |
| `Config` | 迷路設定の型・範囲検証に利用 |
| `MazeGenerator` | `Config` を渡して迷路を生成 |
| `BreadthFirstSearch` | 生成済みセルと設定を渡して最短経路を取得 |
| `Visualizer` | セル、設定、経路、生成履歴を渡してターミナル表示 |
| `maze_analyzer.Maze` | 保存済み16進数迷路を読み込み、構造を検査 |

## 高度な機能

### 42パターン

迷路が幅9以上、高さ7以上の場合、中央に課題指定の `42` パターンを配置します。
パターンを構成するセルは `is_42` として管理され、DFSの開始地点や行き止まり除去の
対象から除外されます。`break_wall()` でも42セルを始点または終点とする壁変更を拒否
するため、生成や再生成で固定表示が壊れません。完全に閉じた装飾セルは意図的に孤立
してよく、到達可能性の検査では例外として扱います。

### Perfect / Non-perfect モード

`PERFECT=True` ではDFSで作った単一経路の完全迷路を維持します。`PERFECT=False` では
生成後に四隅と中央を開通し、行き止まりを見つけるたびに通常セルとの壁を追加で開けて
ループを作ります。これにより、パックマン形式で複数の移動経路を持つ迷路を生成し、
通常の行き止まり0件を目指します。

### 生成結果の自動再試行

両モードで、3 x 3以上の開放空間を `check_big_space()` で検出します。条件に違反した
場合は生成結果を破棄して `reset()` からやり直し、課題の開放空間制限を満たした結果
だけを採用します。

### インタラクティブ表示

`Visualizer` はANSIエスケープシーケンスで壁、通路、入口・出口、42パターン、最短経路
を色分けして表示します。実行中のメニューから最短経路の表示・非表示を切り替えたり、
壁色を定義済みの色の順に変更したりできます。生成過程の再生については、上記の
「生成アニメーション」で説明している履歴再生機能を利用します。

### 厳密な設定エラー処理

設定ファイルは `KEY=VALUE` 形式として解析され、未知のキー、重複キー、空値、必須キー
不足、型、座標範囲、入口と出口の重複を検証します。不正な場合は行番号付きのエラーを
標準エラー出力へ表示し、トレースバックを出さずに終了します。`PERFECT` は `True` または
`False` の明示値だけを受け付けます。

### 独立した迷路アナライザー

`maze_analyzer.py` は出力ファイルを再読み込みし、16進数グリッド、共有壁の整合性、
入口からの到達可能領域、ループ数、四隅・中央・出口の到達性、通常の行き止まりを
検査します。`--max-dead-ends 0` を指定すると、行き止まり0件のボーナス条件も確認
できます。42パターンの完全閉鎖セルは、通常の通路と区別して扱います。

### パッケージ化と品質確認

`make lint` / `make lint-strict` でflake8とmypyを実行でき、`python3 -m build` または
`make review` でwheelをビルドできます。`make review` は別の仮想環境へインストール
して起動するため、開発環境だけで動く実装になっていないかを確認できます。

## チーム管理

> この節は提出時に実際の分担・計画へ置き換えるための記録欄です。

- **役割**: `skurita` — [プログラム全体のアルゴリズム選定、迷路生成部分の実装] / `sozawa` — [エラーハンドリング、ターミナルとのやり取り、プログラム全体のデバック]
- **計画と推移**: [実装に関しては、ロジックから選択し、そこからビジュアライズ、４２のえらんだ保存形式への保存、課題を提出できるように整形という形にしました。]
- **良かった点**: [コーディング、デバックともに対面で行うことで迅速に対応できた。]
- **改善点**: [プッシュする際に過去の記入内容と重複する部分があっても、その文言をコメントしていなかったためバージョンやブランチがごちゃごちゃになってしまうシーンがあった。]
- **使用ツール**: Git、GitHub、`make`、flake8、mypy、Google Gemini

## Resources（参考資料 + AI使用の詳細）

### 参考資料

- [Jamis Buck - 迷路アルゴリズム](https://www.jamisbuck.org/mazes/)
- [深さ優先探索、幅優先探索の解説](https://manabitimes.jp/math/1247)
- [ANSIエスケープシーケンスの解説](https://docsaid.org/ja/blog/colorful-cli-with-ansi-escape-codes/)
- [INFOMISC難しい迷路を自動生成する](https://infomisc.blog/?p=2367)

### AIの利用

調査、コードレビュー、ドキュメント作成の補助としてAIツールを使用しました。
AIによる提案は作者が確認・修正・テストしたうえで採用しており、最終的な実装については
作者が行っております。具体的な利用内容は、アルゴリズムの整理、設定検証・到達可能性の
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
