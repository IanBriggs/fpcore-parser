#  ____  __  _  _  __  __ _   ___     ____  _  _
# (_  _)(  )( \/ )(  )(  ( \ / __)   (  _ \( \/ )
#   )(   )( / \/ \ )( /    /( (_ \ _  ) __/ )  /
#  (__) (__)\_)(_/(__)\_)__) \___/(_)(__)  (__/
#
# A simple start/stop code segment timer
#

from __future__ import annotations

import statistics
import time
from typing import Any, Optional, Union

NS_PER_SEC = 1_000_000_000
NS_PER_MS = 1_000_000


def ns_to_sec(ns: int) -> float:
    return ns / NS_PER_SEC


def ns_to_ms(ns: int) -> float:
    return ns / NS_PER_MS


class TimerRunningError(Exception):
    """Raised when an improper method is called on a Timer that is running"""

    def __init__(self, method: str) -> None:
        self.method = method
        msg = f"Method '{method}' was called while Timer was running"
        super().__init__(msg)


class TimerStoppedError(Exception):
    """Raised when a 'stop' is called on a Timer that is not running"""

    def __init__(self) -> None:
        msg = "Method 'stop' was called while Timer was not running"
        super().__init__(msg)


class TimerLengthError(Exception):
    """Raised when a method is called requiring more sessions"""

    def __init__(self, method: str, length: int) -> None:
        self.method = method
        self.length = length
        msg = f"To call '{method}' at least {length} sessions are needed"
        super().__init__(msg)


class Timer:
    """A Timer object is simple way to measure elapsed time"""

    def __init__(self) -> None:
        # A list of session times in nanoseconds
        self._times_ns: list[int] = list()
        # Either the current start point when active or None when inactive
        self._start_ns: Optional[int] = None

    def __enter__(self) -> Timer:
        self.start()
        return self

    def __exit__(self,
                 exc_type: Optional[type],
                 exc_value: Optional[BaseException],
                 traceback: Optional[Any]) -> Optional[bool]:
        # TODO: should we do anything for exceptional circumstances?
        self.stop()
        return None

    def __len__(self) -> int:
        """Number of timing sessions"""
        return len(self._times_ns)

    def __getitem__(self, key: Any) -> Union(float, list[float]):
        """Get specific elapsed time(s) in seconds"""
        if self._start_ns is not None:
            raise TimerRunningError("__getitem__")
        res = self._times_ns[key]
        if type(res) == int:
            return ns_to_sec(res)
        return [ns_to_sec(r) for r in res]

    def reset(self) -> None:
        """Clears the timer history and stops the current session"""
        self._times_ns.clear()
        self._start_ns = None

    def start(self) -> None:
        """Starts a timing session"""
        if self._start_ns is not None:
            raise TimerRunningError("start")
        # Grab time last when starting
        self._start_ns = time.perf_counter_ns()

    def stop(self) -> float:
        """Stops the timing session and returns the session time in seconds"""
        # Grab time first when stopping
        end_ns = time.perf_counter_ns()
        if self._start_ns is None:
            raise TimerStoppedError()
        next_elapsed_ns = end_ns - self._start_ns
        self._times_ns.append(next_elapsed_ns)
        self._start_ns = None
        return ns_to_sec(next_elapsed_ns)

    def elapsed_time(self) -> float:
        """Returns the total elapsed time in seconds"""
        if self._start_ns is not None:
            raise TimerRunningError("elapsed_ns")
        return ns_to_sec(sum(self._times_ns))

    def elapsed_time_ms(self) -> float:
        """Returns the total elapsed time in milliseconds"""
        if self._start_ns is not None:
            raise TimerRunningError("elapsed_ns")
        return ns_to_ms(sum(self._times_ns))

    def mean(self) -> float:
        """Returns the mean time per session in seconds"""
        if self._start_ns is not None:
            raise TimerRunningError("mean")
        if len(self._times_ns) < 1:
            raise TimerLengthError("mean", 1)
        mean_ns = statistics.mean(self._times_ns)
        return ns_to_sec(mean_ns)

    def average(self) -> float:
        """Returns the average time per session in seconds"""
        return self.mean()

    def stddev(self) -> float:
        """Returns the standard deviation of time per session"""
        if self._start_ns is not None:
            raise TimerRunningError("stddev")
        if len(self._times_ns) < 2:
            raise TimerLengthError("stddev", 2)
        stddev_ns = statistics.stdev(self._times_ns)
        return ns_to_sec(stddev_ns)

    def median(self) -> float:
        """Returns the median time per session"""
        if self._start_ns is not None:
            raise TimerRunningError("median")
        if len(self._times_ns) < 1:
            raise TimerLengthError("median", 1)
        median_ns = statistics.median(self._times_ns)
        return ns_to_sec(median_ns)


def main(argv: list[str]) -> int:
    # Get iteration count
    target_iterations = 1_000_000
    try:
        target_iterations = int(argv[1])
    except IndexError:
        pass
    except ValueError:
        print("Ignoring non integer iteration argument: '{}'".format(argv[1]))

    # Run a loop with the timer
    with_timer_start = time.perf_counter()

    my_timer = Timer()
    for _ in range(target_iterations):
        my_timer.start()
        my_timer.stop()

    with_timer_stop = time.perf_counter()

    # Run same loop without timer
    without_timer_start = time.perf_counter()

    for _ in range(target_iterations):
        pass

    without_timer_stop = time.perf_counter()

    # Sanity check
    iterations = len(my_timer)
    assert target_iterations == iterations, "Iteration counts do not match"

    # Stats
    stats = {
        "iterations": "{:,}".format(iterations),
        "average": "{:,.1f} ns".format(NS_PER_SEC * my_timer.average()),
        "stddev": "{:,.1f} ns".format(NS_PER_SEC * my_timer.stddev()),
        "minimum": "{:,.1f} ns".format(NS_PER_SEC * min(my_timer)),
        "median": "{:,.1f} ns".format(NS_PER_SEC * my_timer.median()),
        "maximum": "{:,.1f} ns".format(NS_PER_SEC * max(my_timer)),
    }
    stats_label_len = max(len(label) for label in stats.keys())
    stats_value_len = max(len(s) for s in stats.values())

    # Overhead
    with_timer_time = with_timer_stop - with_timer_start
    without_timer_time = without_timer_stop - without_timer_start
    timer_overhead = with_timer_time - without_timer_time
    per_pair_overhead = NS_PER_SEC * timer_overhead / iterations
    overhead = {
        "with_timer": "{:,.4f} sec".format(with_timer_time),
        "without timer": "{:,.4f} sec".format(without_timer_time),
        "timer overhead": "{:,.4f} sec".format(timer_overhead),
        "per pair overhead": "{:,.1f} ns".format(per_pair_overhead),
    }
    overhead_label_len = max(len(label) for label in overhead.keys())
    overhead_value_len = max(len(s) for s in overhead.values())

    # Output
    print("Stats:")
    fmt_str = f"{{:>{stats_label_len+2}}}: {{:>{stats_value_len}}}"
    for label, value in stats.items():
        print(fmt_str.format(label, value))
    print()

    print("Overhead:")
    fmt_str = f"{{:>{overhead_label_len+2}}}: {{:>{overhead_value_len}}}"
    for label, value in overhead.items():
        print(fmt_str.format(label, value))

    return 0


if __name__ == "__main__":
    import sys

    try:
        return_code = main(sys.argv)
    except KeyboardInterrupt:
        print("")
        print("Goodbye")
        return_code = 130  # meaning "Script terminated by Control-C"

    sys.exit(return_code)
