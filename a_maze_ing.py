#!/usr/bin/env python3
import sys
import random
from typing import Any
from pydantic import ValidationError
from mazegen.maze_generator import Config
from mazegen import MazeGenerator
from mazegen.bfs import BreadthFirstSearch
from mazegen.visualizer import Visualizer


class ConfigFileError(ValueError):
    """Raised when config.txt cannot be parsed or validated."""


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
        raise ConfigFileError(
            "Usage: python3 a_maze_ing.py config.txt"
        )

    config_path = sys.argv[1]
    try:
        with open(config_path, encoding="utf-8") as config_file:
            lines = config_file.readlines()
    except FileNotFoundError as error:
        raise ConfigFileError(
            f"{config_path!r} was not found"
        ) from error
    except UnicodeDecodeError as error:
        raise ConfigFileError(
            f"{config_path!r} is not valid UTF-8"
        ) from error
    except OSError as error:
        raise ConfigFileError(
            f"could not read {config_path!r}: {error}"
        ) from error

    allowed_keys = {
        "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT", "SEED"
    }
    pairs: dict[str, Any] = {}
    line_numbers: dict[str, int] = {}

    for line_number, raw_line in enumerate(lines, start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigFileError(
                f"line {line_number}: expected KEY=VALUE, "
                f"got {raw_line.rstrip()!r}"
            )

        key, value = (part.strip() for part in line.split("=", 1))
        if not key:
            raise ConfigFileError(
                f"line {line_number}: configuration key is empty"
            )
        if not value:
            raise ConfigFileError(
                f"line {line_number}: value for {key!r} is empty"
            )
        if key not in allowed_keys:
            expected = ", ".join(sorted(allowed_keys))
            raise ConfigFileError(
                f"line {line_number}: unknown key {key!r}; "
                f"expected one of: {expected}"
            )
        if key in pairs:
            raise ConfigFileError(
                f"line {line_number}: duplicate key {key!r}; "
                f"first defined on line {line_numbers[key]}"
            )

        pairs[key] = value
        line_numbers[key] = line_number

    try:
        return Config.model_validate(pairs)
    except ValidationError as error:
        messages = []
        for issue in error.errors():
            field = str(issue["loc"][0]) if issue["loc"] else "config"
            if field == "config":
                entry_line = line_numbers.get("ENTRY", "not present")
                exit_line = line_numbers.get("EXIT", "not present")
                error_line: int | str = f"{entry_line}/{exit_line}"
            else:
                error_line = line_numbers.get(field, "not present")
            message = str(issue["msg"]).replace("Value error, ", "")
            messages.append(f"line {error_line}: {field}: {message}")
        raise ConfigFileError("\n".join(messages)) from error


def main() -> None:
    """
    main関数

    DFS（recursive backtracker）で迷路を生成する
    """
    if len(sys.argv) < 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        config = parse_config()
    except ConfigFileError as error:
        print(f"Config error:\n{error}", file=sys.stderr)
        sys.exit(1)
    maze = MazeGenerator(config)
    random.seed(maze._config.SEED)
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


if __name__ == "__main__":
    # try:
    main()
    # except BaseException as e:
    #     print(f"[Error]{e}")
