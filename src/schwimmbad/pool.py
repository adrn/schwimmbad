# type: ignore
import abc
from collections.abc import Iterable
from typing import Any, Callable

# This package
from .utils import batch_tasks

__all__ = ["BasePool"]


def _callback_wrapper(
    callback: Callable[..., Any], generator: Iterable[Any]
) -> Iterable[Any]:
    for element in generator:
        callback(element)
        yield element


class BasePool(metaclass=abc.ABCMeta):
    """A base class multiprocessing pool with a ``map`` method."""

    def __init__(self, **_: Any):
        self.rank = 0

    @staticmethod
    def enabled() -> bool:
        return False

    def is_master(self) -> bool:
        return self.rank == 0

    def is_worker(self) -> bool:
        return self.rank != 0

    def wait(self) -> None:
        return

    @abc.abstractmethod
    def map(self, *args: Any, **kwargs: Any) -> Any:
        return

    def batched_map(
        self,
        worker: Callable[..., Any],
        tasks: Iterable[Any],
        *args: Any,
        **kwargs: Any,
    ) -> Iterable[Any]:
        batches = batch_tasks(n_batches=self.size, data=tasks)
        return self.map(worker, batches, *args, **kwargs)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def _call_callback(self, callback, generator):
        if callback is None:
            return generator
        return _callback_wrapper(callback, generator)
