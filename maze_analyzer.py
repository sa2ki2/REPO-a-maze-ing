#!/usr/bin/env python3
"""a_maze_ingの出力迷路を検査する解析ツール。

迷路ファイルを読み込み、共有壁の整合性、到達可能領域、ループ数、
行き止まり、入口・出口・四隅・中央の到達性を確認する。壊れた入力は
トレースバックではなく明確なエラーと終了コードで報告する。

ファイルの各セルは16進数1桁で表し、ビットが1なら壁が閉じている。
ビット0から順に北・東・南・西を表す。空行の後には入口座標、出口座標、
最短経路が続く。
"""

from __future__ import annotations

import argparse
import sys
from collections import deque
from dataclasses import dataclass
from enum import IntFlag
from functools import cached_property
from typing import Dict, FrozenSet, Iterator, List, Optional, Set, Tuple

Cell = Tuple[int, int]                 # 不変な(row, col)座標


class Direction(IntFlag):
    """壁の方向を表す列挙型。値は出力ファイル内のビットに対応する。"""

    NORTH = 1
    EAST = 2
    SOUTH = 4
    WEST = 8

    @property
    def opposite(self) -> "Direction":
        """隣接セル側から見た反対方向を返す。"""
        return _OPPOSITE[self]

    @property
    def step(self) -> Cell:
        """この方向の隣接セルへ移動する(row, col)差分を返す。"""
        return _STEP[self]


_OPPOSITE: Dict[Direction, Direction] = {
    Direction.NORTH: Direction.SOUTH,
    Direction.SOUTH: Direction.NORTH,
    Direction.EAST: Direction.WEST,
    Direction.WEST: Direction.EAST,
}
_STEP: Dict[Direction, Cell] = {
    Direction.NORTH: (-1, 0),
    Direction.EAST: (0, 1),
    Direction.SOUTH: (1, 0),
    Direction.WEST: (0, -1),
}
ALL_WALLS = Direction.NORTH | Direction.EAST | Direction.SOUTH | Direction.WEST

DEFAULT_MIN_LOOPS = 2
DEFAULT_MAX_DEAD_ENDS = 2
EXIT_OK = 0
EXIT_MALFORMED = 2

HEX_DIGITS = frozenset("0123456789abcdefABCDEF")


class MazeError(Exception):
    """入力ファイルを迷路グリッドとして解析できない場合の例外。"""


# --------------------------------------------------------------------------- #
# 迷路モデル
# --------------------------------------------------------------------------- #
class Maze:
    """解析済み迷路の壁グリッド、入口、出口を保持するクラス。

    各セルの整数値は閉じた壁をビットで表し、隣接セル間の開いた壁を
    グラフの辺として到達性やループ数を計算する。
    """

    def __init__(self, grid: List[List[int]], entry: Optional[Cell],
                 exit: Optional[Cell]) -> None:
        """壁グリッドと入口・出口を保持し、行数と列数を初期化する。"""
        self.grid = grid
        self.entry = entry
        self.exit = exit
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0

    # -- 生成 --------------------------------------------------------------- #
    @classmethod
    def from_file(cls, path: str) -> "Maze":
        """指定ファイルを解析してMazeを作る。不正なグリッドではMazeErrorを送出する。"""
        grid: List[List[int]] = []
        footer: List[str] = []
        reading_grid = True
        with open(path, encoding="utf-8", errors="replace") as stream:
            for number, raw in enumerate(stream, start=1):
                line = raw.rstrip("\n\r")
                if reading_grid:
                    if not line.strip():
                        reading_grid = False
                        continue
                    cells = line.strip(" \t")
                    grid.append(cls._parse_row(cells, number, grid))
                elif line.strip():
                    footer.append(line.strip())
        if not grid:
            raise MazeError("no grid rows were found before the footer.")
        entry = cls._parse_coordinate(footer[0]) if footer else None
        exit_ = cls._parse_coordinate(footer[1]) if len(footer) > 1 else None
        return cls(grid, entry, exit_)

    @staticmethod
    def _parse_row(text: str, number: int, grid: List[List[int]]) -> List[int]:
        """1行分の16進数セルを検証し、整数のリストへ変換する。"""
        row = []
        for column, char in enumerate(text, start=1):
            if char not in HEX_DIGITS:
                raise MazeError(
                    f"line {number}, column {column}: {char!r} is not a "
                    f"hexadecimal digit (the grid must use digits 0-F)."
                )
            row.append(int(char, 16))
        if grid and len(row) != len(grid[0]):
            raise MazeError(
                f"line {number}: row has {len(row)} cells but the first row "
                f"has {len(grid[0])} (the grid must be rectangular)."
            )
        return row

    @staticmethod
    def _parse_coordinate(text: str) -> Optional[Cell]:
        """x,y形式の座標を内部の(row, col)形式へ変換する。"""
        try:
            x_text, y_text = text.split(",")
            return int(y_text), int(x_text)
        except ValueError:
            return None

    # -- グリッドアクセス --------------------------------------------------- #
    def __contains__(self, cell: Cell) -> bool:
        """指定セルが迷路の範囲内にあるか返す。"""
        row, col = cell
        return 0 <= row < self.rows and 0 <= col < self.cols

    def __iter__(self) -> Iterator[Cell]:
        """迷路内の全セルを行優先順で順番に返す。"""
        for row in range(self.rows):
            for col in range(self.cols):
                yield row, col

    def walls(self, cell: Cell) -> int:
        """指定セルの閉じた壁をビット値で返す。"""
        return self.grid[cell[0]][cell[1]]

    def is_fully_closed(self, cell: Cell) -> bool:
        """42の固定表示に使われる全方向閉鎖セルか返す。"""
        return self.walls(cell) == ALL_WALLS

    # -- グラフ ------------------------------------------------------------- #
    def neighbour(self, cell: Cell, side: Direction) -> Cell:
        """指定方向に隣接するセルの座標を返す。"""
        return cell[0] + side.step[0], cell[1] + side.step[1]

    def is_open(self, cell: Cell, side: Direction) -> bool:
        """指定方向の壁が両隣接セルで開いているか返す。"""
        other = self.neighbour(cell, side)
        if other not in self:
            return False
        return not (self.walls(cell) & side) \
            and not (self.walls(other) & side.opposite)

    def passages(self, cell: Cell) -> Iterator[Cell]:
        """指定セルから開いた通路で移動できる隣接セルを返す。"""
        for side in Direction:
            if self.is_open(cell, side):
                yield self.neighbour(cell, side)

    def region_of(self, start: Cell) -> FrozenSet[Cell]:
        """指定セルからBFSで到達できるセル集合を返す。"""
        seen = {start}
        queue = deque([start])
        while queue:
            for nxt in self.passages(queue.popleft()):
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return frozenset(seen)

    def largest_region(self) -> FrozenSet[Cell]:
        """迷路内で最大の連結領域を返す。"""
        seen: Set[Cell] = set()
        best: FrozenSet[Cell] = frozenset()
        for cell in self:
            if cell in seen:
                continue
            component = self.region_of(cell)
            seen |= component
            if len(component) > len(best):
                best = component
        return best

    def incoherent_cells(self) -> Tuple[Cell, ...]:
        """隣接セルと共有壁の値が一致しないセルを返す。"""
        return tuple(
            cell
            for cell in self
            if any(
                self.neighbour(cell, side) in self
                and bool(self.walls(cell) & side)
                != bool(self.walls(self.neighbour(cell, side)) & side.opposite)
                for side in Direction
            )
        )


# --------------------------------------------------------------------------- #
# 解析結果
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class MazeReport:
    """プレイ可能領域の接続性を測定した解析結果。

    基本的な個数だけを保持し、ループ数や割合などは必要なときに計算する。
    """

    maze: Maze
    region: FrozenSet[Cell]
    entry: Cell
    entry_from_footer: bool
    incoherent: Tuple[Cell, ...]

    @cached_property
    def open_passages(self) -> int:
        """プレイ可能領域内の開通辺数を返す。各辺は一度だけ数える。"""
        return sum(
            1
            for cell in self.region
            for nxt in self.maze.passages(cell)
            if nxt in self.region and nxt > cell
        )

    @cached_property
    def potential_passages(self) -> int:
        """領域内の壁を全て開けた場合に作れる辺数を返す。"""
        return sum(
            ((r, c + 1) in self.region) + ((r + 1, c) in self.region)
            for r, c in self.region
        )

    @property
    def loops(self) -> int:
        """独立ループ数を「辺数 - ノード数 + 1」で計算して返す。"""
        return self.open_passages - len(self.region) + 1

    @property
    def max_loops(self) -> int:
        """現在の領域で理論上作れる最大ループ数を返す。"""
        return max(self.potential_passages - max(len(self.region) - 1, 0), 0)

    @property
    def path_ratio(self) -> float:
        """実際のループ数が最大値に占める割合を返す。"""
        return self.loops / self.max_loops if self.max_loops else 0.0

    @property
    def isolated(self) -> int:
        """プレイ可能領域から分離しているセル数を返す。"""
        return self.maze.rows * self.maze.cols - len(self.region)

    @cached_property
    def disconnected_corridors(self) -> int:
        """42固定壁を除く、プレイ可能領域外の通常通路セル数を返す。

        これらはプレイヤーが到達できないため、迷路全体の接続性違反になる。
        """
        return sum(
            1
            for cell in self.maze
            if cell not in self.region and not self.maze.is_fully_closed(cell)
        )

    @property
    def exit_reachable(self) -> Optional[bool]:
        """出口が設定されている場合、その領域から到達可能か返す。"""
        if self.maze.exit is None:
            return None
        return self.maze.exit in self.region

    @cached_property
    def dead_ends(self) -> Tuple[int, int]:
        """一方向だけ開いたセルを(通常, 42に囲まれたもの)の順で数える。

        閉じた壁の先に通常セルがあれば通常の行き止まり、42固定セルまたは
        外周しかなければ許容される42内の行き止まりとして分類する。
        """
        real = enclosed = 0
        for cell in self.region:
            if sum(1 for _ in self.maze.passages(cell)) != 1:
                continue
            if self._has_openable_wall(cell):
                real += 1
            else:
                enclosed += 1
        return real, enclosed

    def _has_openable_wall(self, cell: Cell) -> bool:
        """指定セルに通常セルへ開けられる閉じた壁があるか返す。"""
        return any(
            (self.maze.walls(cell) & side)
            and self.maze.neighbour(cell, side) in self.maze
            and not self.maze.is_fully_closed(self.maze.neighbour(cell, side))
            for side in Direction
        )

    @cached_property
    def unreachable_key_cells(self) -> Tuple[Cell, ...]:
        """四隅と中央のうち、プレイ可能領域へ到達できないセルを返す。

        行または列が偶数の場合、中央を囲む最大4セルのいずれかが到達可能
        であれば中央到達とみなす。
        """
        rows, cols = self.maze.rows, self.maze.cols
        corners = {(0, 0), (0, cols - 1), (rows - 1, 0), (rows - 1, cols - 1)}
        missing = {cell for cell in corners if cell not in self.region}
        centre_candidates = self._centre_candidates()
        if not any(cell in self.region for cell in centre_candidates):
            missing |= centre_candidates
        return tuple(sorted(missing))

    def _centre_candidates(self) -> FrozenSet[Cell]:
        """迷路サイズの偶奇を考慮して中央候補セルを返す。"""
        rows, cols = self.maze.rows, self.maze.cols
        row_mid = {rows // 2} if rows % 2 else {rows // 2 - 1, rows // 2}
        col_mid = {cols // 2} if cols % 2 else {cols // 2 - 1, cols // 2}
        return frozenset((r, c) for r in row_mid for c in col_mid)


def analyze(maze: Maze) -> MazeReport:
    """入口領域、または入口が無効なら最大領域を選び、解析結果を作る。"""
    if maze.entry is not None and maze.entry in maze:
        region, from_footer = maze.region_of(maze.entry), True
        entry = maze.entry
    else:
        region = maze.largest_region()
        entry = min(region) if region else (0, 0)
        from_footer = False
    return MazeReport(
        maze, region, entry, from_footer, maze.incoherent_cells()
    )


# --------------------------------------------------------------------------- #
# 判定とレポート出力
# --------------------------------------------------------------------------- #
def verdict(report: MazeReport, min_loops: int, max_dead_ends: int) -> str:
    """解析結果を課題基準に沿った1行の判定文へ変換する。

    min_loopsは必要な独立経路数、max_dead_endsは許容する通常行き止まり数を
    表す。max_dead_endsを0にするとdead-end 0のボーナス条件を確認できる。
    """
    real_dead_ends = report.dead_ends[0]
    if report.incoherent:
        return (
            f"INCOHERENT walls: {len(report.incoherent)} cell(s) encode a "
            f"shared wall differently from their neighbour - the maze is "
            f"invalid (fix the encoding first)."
        )
    if len(report.region) <= 1:
        return (
            "DEGENERATE: the entry has no open passage (no navigable "
            "corridors) - check the wall encoding and the entry cell."
        )
    if report.disconnected_corridors:
        return (
            f"NOT fully connected: {report.disconnected_corridors} corridor "
            f"cell(s) cannot be reached from the entry - a Pac-Man level here "
            f"would be unwinnable (only the '42' cells may be isolated)."
        )
    if report.loops == 0:
        return (
            "PERFECT maze: a single path, no loop -> matches PERFECT=True "
            "(this is not a multi-route board for Pac-Man)."
        )
    if report.unreachable_key_cells:
        return (
            "Not Pac-Man-ready: the player start (centre) or a corner is not "
            "an open corridor - ghosts, super-pacgums or the player can't be "
            "placed."
        )
    if report.loops < min_loops:
        return (
            f"Not Pac-Man-ready: only {report.loops} independent route(s); a "
            f"usable board needs at least {min_loops} so a chased player "
            f"always has an alternative."
        )
    if real_dead_ends > max_dead_ends:
        return (
            f"Not Pac-Man-ready: {real_dead_ends} real dead-ends (at most "
            f"{max_dead_ends} tolerated) - too many traps for a chased player."
        )
    extra = (
        "no real dead-end -> bonus-grade (perfectly braided)"
        if real_dead_ends == 0 else
        f"{real_dead_ends} real dead-end(s) within tolerance "
        f"(0 would be bonus-grade)"
    )
    return (
        f"Pac-Man-USABLE: fully connected, corners and centre reachable, "
        f"{report.loops} independent routes; {extra}."
    )


def render(report: MazeReport, min_loops: int, max_dead_ends: int) -> str:
    """解析結果を人間が読みやすい複数行のレポートへ整形する。"""
    maze = report.maze
    real, enclosed = report.dead_ends
    lines = [
        f"Maze size        : {maze.cols} x {maze.rows} "
        f"({maze.rows * maze.cols} cells)",
        f"Entry            : {_xy(report.entry)}   Exit: {_exit(report)}",
    ]
    if not report.entry_from_footer:
        lines.append("                   (no valid entry in footer; using the "
                     "largest reachable region)")
    lines += [
        f"Reachable region : {len(report.region)} cells "
        f"({report.disconnected_corridors} corridor(s) unreachable)",
        f"Independent loops: {report.loops} / {report.max_loops} possible "
        f"(path ratio {report.path_ratio:.0%})",
        f"Dead-ends        : {real} real + {enclosed} enclosed by the '42' "
        f"(tolerated)",
        f"Corners + centre : {_key_cells(report.unreachable_key_cells)}",
        f"Wall coherence   : {_coherence(report.incoherent)}",
        "",
        f"Verdict: {verdict(report, min_loops, max_dead_ends)}",
    ]
    return "\n".join(lines)


def _xy(cell: Cell) -> str:
    """内部の(row, col)座標を課題仕様の(x, y)表記へ変換する。"""
    return f"({cell[1]}, {cell[0]})"


def _exit(report: MazeReport) -> str:
    """出口座標と到達状態を表示用の文字列へ変換する。"""
    if report.maze.exit is None:
        return "?"
    states: Dict[Optional[bool], str] = {
        True: " (reachable)", False: " (UNREACHABLE)",
    }
    state = states.get(report.exit_reachable, "")
    return f"{_xy(report.maze.exit)}{state}"


def _key_cells(cells: Tuple[Cell, ...]) -> str:
    """未到達の重要セル一覧を表示用の文字列へ変換する。"""
    if not cells:
        return "all reachable"
    return "NOT reachable -> " + ", ".join(_xy(cell) for cell in cells)


def _coherence(cells: Tuple[Cell, ...]) -> str:
    """共有壁の不整合セル一覧を短い表示用文字列へ変換する。"""
    if not cells:
        return "OK (all shared walls match)"
    shown = ", ".join(_xy(cell) for cell in cells[:5])
    extra = "" if len(cells) <= 5 else f", ... (+{len(cells) - 5} more)"
    return f"{len(cells)} mismatching cell(s) -> {shown}{extra}"


# --------------------------------------------------------------------------- #
# エントリーポイント
# --------------------------------------------------------------------------- #
def parse_args(argv: List[str]) -> argparse.Namespace:
    """コマンドライン引数を解析し、設定値を保持するNamespaceを返す。"""
    parser = argparse.ArgumentParser(
        description="Analyze an a_maze_ing output file: wall coherence and "
                    "whether the maze is perfect or a playable Pac-Man board.",
    )
    parser.add_argument("output_file", help="maze output file to analyze")
    parser.add_argument(
        "--min-loops", type=int, default=DEFAULT_MIN_LOOPS, metavar="N",
        help="independent routes a playable (non-perfect) maze must keep "
             "(default: %(default)s)",
    )
    parser.add_argument(
        "--max-dead-ends", type=int, default=DEFAULT_MAX_DEAD_ENDS,
        metavar="N",
        help="real dead-ends tolerated; use 0 for the no-dead-end bonus "
             "(default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv: List[str]) -> int:
    """迷路を読み込んで解析結果を表示し、終了コードを返す。"""
    args = parse_args(argv)
    try:
        maze = Maze.from_file(args.output_file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.output_file}")
        return EXIT_MALFORMED
    except (OSError, MazeError) as error:
        print(f"Malformed maze file: {error}")
        return EXIT_MALFORMED
    print(render(analyze(maze), args.min_loops, args.max_dead_ends))
    return EXIT_OK


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as error:        # 想定外の入力でもトレースバックを表示しない
        print(f"Unexpected error while analyzing the maze: {error}")
        sys.exit(EXIT_MALFORMED)
