#!/usr/bin/env python3
import sys
import random
from typing import Any
from mazegen.maze_generator import Config
from mazegen import MazeGenerator
from mazegen.maze_gen_prims import MazeGeneratorPrims
from mazegen.maze_gen_kruskals import MazeGeneratorKruskals
from mazegen.bfs import BreadthFirstSearch
from mazegen.visualizer import Visualizer


def parse_config() -> Config:
    """
    config.txtのパースを行う。

    config.txtを読み取り、Configにして返す。

    Returns:
        Config: パースされた設定オブジェクト。

    Raises:
        Exception: コマンドライン引数が不足している場合。
    """
    if len(sys.argv) < 2:
        raise Exception("Usage: python a-maze-ing.py config.txt")
    with open(sys.argv[1]) as f:
        content = f.read()
        pairs_str = content.split("\n")
        pairs = []
        for item in pairs_str:
            if not item.startswith("# "):
                pairs.append(item)
        pairs_dict: dict[str, Any] = dict(
            item.split("=", 1)
            for item in pairs if "=" in item
        )
        config = Config(**pairs_dict)
    return config


def main() -> None:
    """
    main関数

    STRATEGYによって迷路生成アルゴリズムを切り替える
    """
    if len(sys.argv) < 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    config = parse_config()
    maze = MazeGenerator(config)
    random.seed(maze._config.SEED)

    if maze._config.STRATEGY == "recursive":
        maze.maze_gen()
        bfs = BreadthFirstSearch(maze._pos, maze._config)
        bfs.search_maze()
        maze.output_to_file(bfs._path_cardinal)
        visualizer = Visualizer(
            bfs._pos, bfs._config, bfs._path,
            maze._history, bfs._history_bfs, maze._exist_42
        )
        visualizer.visualize()
        visualizer.show()
    elif maze._config.STRATEGY == "prims":
        maze_prims = MazeGeneratorPrims(config)
        maze_prims.maze_gen()
        bfs_prims = BreadthFirstSearch(
            maze_prims._pos, maze_prims._config
        )
        bfs_prims.search_maze()
        maze_prims.output_to_file(bfs_prims._path_cardinal)
        vis_prims = Visualizer(
            bfs_prims._pos, bfs_prims._config, bfs_prims._path,
            maze_prims._history, bfs_prims._history_bfs,
            maze_prims._exist_42
        )
        vis_prims.visualize()
        vis_prims.show()
    elif maze._config.STRATEGY == "kruskals":
        maze_kruskals = MazeGeneratorKruskals(config)
        maze_kruskals.maze_gen()
        bfs_kruskals = BreadthFirstSearch(
            maze_kruskals._pos, maze_kruskals._config
        )
        bfs_kruskals.search_maze()
        maze_kruskals.output_to_file(bfs_kruskals._path_cardinal)
        vis_kruskals = Visualizer(
            bfs_kruskals._pos, bfs_kruskals._config, bfs_kruskals._path,
            maze_kruskals._history, bfs_kruskals._history_bfs,
            maze_kruskals._exist_42
        )
        vis_kruskals.visualize()
        vis_kruskals.show()


if __name__ == "__main__":
    # try:
    main()
    # except BaseException as e:
    #     print(f"[Error]{e}")
