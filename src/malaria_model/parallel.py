"""Run independent simulations in parallel processes.

Only call from code reached under `if __name__ == "__main__":` (see main.py):
macOS starts worker processes by re-importing the main module.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from concurrent.futures import ProcessPoolExecutor
from typing import Any

from malaria_model import params as p


def parallel_map(func: Callable[[Any], Any], items: Iterable[Any],
                 workers: int = p.N_WORKERS) -> list[Any]:
    """[func(item) for item in items], spread over `workers` processes (1 = serial).

    func must be a top-level function so it can be sent to worker processes.
    Worker processes see params.py as written on disk, not runtime overrides.
    """
    items = list(items)
    if workers <= 1:
        return [func(item) for item in items]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(func, items))
