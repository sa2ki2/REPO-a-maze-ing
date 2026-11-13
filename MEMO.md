# Review memo

## Review date

2026-11-14

## Errors found

### PERFECT mode did not enforce the 3 x 3 open-space restriction

`MazeGenerator.maze_gen()` checked `check_big_space()` only when
`PERFECT=False`. As a result, `PERFECT=True` could produce a maze containing a
3 x 3 or larger open space, which violated the mandatory maze restriction.

Reproduction with a 20 x 15 maze and 100 seeds:

```text
PERFECT=False: big_space_failures=[]
PERFECT=True:  big_space_failures=[6, 9, 26, 29, 50, 61, 97]
```

This was fixed by applying the same open-space validation to perfect mazes.
The generator now retries both modes when a large open space is found.

### Reachability of the 42 pattern

Fully closed cells belonging to the 42 pattern are intentionally allowed to
be isolated. The project decision is that these decorative 42 cells do not
need to be reachable; the reachability requirement applies to playable maze
corridors. The analyzer follows this rule by allowing isolated fully closed
42 cells while rejecting unreachable normal corridors.

## Changes made before this review

- Maze generation was reduced to DFS recursive backtracking.
- Prim and Kruskal implementations were removed from the active package.
- Non-perfect mazes remove real dead-ends and pass
  `--max-dead-ends 0`.
- BFS remains responsible for shortest-path calculation.
- BFS animation was removed; maze-generation animation remains.
- The package was reorganized under `mazegen/`.
- `config.txt` parsing was made strict:
  - line-numbered errors
  - malformed `KEY=VALUE` detection
  - unknown and duplicate key detection
  - empty value detection
  - coordinate, integer, boolean, and range validation
  - missing-file and invalid-UTF-8 handling
  - exit status 1 without a traceback

## Verified successfully

- Default configuration runs successfully.
- Default non-perfect maze passes the analyzer with
  `--max-dead-ends 0`.
- Both perfect and non-perfect modes produced no large open space for 100
  tested seeds after the fix.
- Configuration error cases return status 1 with detailed messages.
- flake8 and mypy pass.
- The wheel builds, installs, and imports successfully.

## Code explained simply

### `a_maze_ing.py`

This is the program's starting point. It reads the configuration file, creates
the maze, finds the route from the entry to the exit, saves the result, and
starts the terminal menu. Configuration mistakes are reported here before
maze generation begins.

### `mazegen/maze_generator.py`

This file defines the settings and the basic maze data. It stores each cell's
walls, creates the 42 pattern, opens walls between neighbouring cells, checks
large open spaces, opens the corners and centre for non-perfect mazes, and
writes the final hexadecimal maze file.

For a non-perfect maze, it repeatedly opens one extra wall from every
dead-end until no real dead-end remains. For both maze types, it rejects a
result containing a 3 x 3 or larger open space and generates it again.

### `mazegen/maze_gen_recursive.py`

This is the only maze-generation algorithm in the project. It starts at a
random cell, moves to an unvisited neighbour, and removes the wall between
the two cells. When it cannot move forward, it goes back to an earlier cell
and tries another direction. This is depth-first search with backtracking.

### `mazegen/bfs.py`

This file finds the shortest route. It checks cells in expanding distance
from the entry, remembers where each cell was reached from, and follows those
remembered parents backwards from the exit to rebuild the shortest path.

### `mazegen/visualizer.py`

This file draws the maze in the terminal using coloured ANSI blocks. It also
provides the menu for regenerating a maze, showing the shortest route,
changing wall colours, and replaying the maze-generation animation.

### `maze_analyzer.py`

This is a separate checker for the generated output file. It validates the
hexadecimal grid, shared-wall consistency, reachability, loops, corners,
centre, exit, and dead-ends. The `--max-dead-ends 0` option checks the
no-dead-end condition.

### `config.txt`

This is the user's input file. It contains the maze size, entry and exit,
output filename, perfect/non-perfect mode, and optional seed.

### `Makefile`

This provides short commands for installing dependencies, running the
program, analyzing output, linting, type-checking, and building a wheel.

### `pyproject.toml`

This describes the Python package, its metadata, required Python version, and
the dependencies needed to build and use it.
