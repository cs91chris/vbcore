from typing import Callable

from sqlalchemy import event


class Listener:
    @classmethod
    def register_after_create(cls, target, callback, *args, **kwargs) -> None:
        event.listen(target, "after_create", callback, *args, **kwargs)

    @classmethod
    def register_before_drop(cls, target, callback, *args, **kwargs) -> None:
        event.listen(target, "before_drop", callback, *args, **kwargs)

    @classmethod
    def register_handle_error(cls, engine, callback, *args, **kwargs) -> None:
        event.listen(engine, "handle_error", callback, *args, **kwargs)

    @classmethod
    def register_at_commit(cls, engine, callback, *args, **kwargs) -> None:
        event.listen(engine, "commit", callback, *args, **kwargs)

    @classmethod
    def register_at_rollback(cls, engine, callback, *args, **kwargs) -> None:
        event.listen(engine, "rollback", callback, *args, **kwargs)

    @classmethod
    def register_at_rollback_savepoint(cls, engine, callback, *args, **kwargs) -> None:
        event.listen(engine, "rollback_savepoint", callback, *args, **kwargs)

    @classmethod
    def register_at_checkin(cls, engine, callback, *args, **kwargs) -> None:
        event.listen(engine, "checkin", callback, *args, **kwargs)

    @classmethod
    def listens_for_after_create(cls, target, *args, **kwargs) -> Callable:
        def wrapper(fn):
            cls.register_after_create(target, fn, *args, **kwargs)
            return fn

        return wrapper

    @classmethod
    def listens_for_before_drop(cls, target, *args, **kwargs) -> Callable:
        def wrapper(fn):
            cls.register_before_drop(target, fn, *args, **kwargs)
            return fn

        return wrapper

    @classmethod
    def listens_for_handle_error(cls, target, *args, **kwargs) -> Callable:
        def wrapper(fn):
            cls.register_handle_error(target, fn, *args, **kwargs)
            return fn

        return wrapper

    @classmethod
    def listens_for_commit(cls, engine, *args, **kwargs) -> Callable:
        def wrapper(fn):
            cls.register_at_commit(engine, fn, *args, **kwargs)
            return fn

        return wrapper

    @classmethod
    def listens_for_rollback(cls, engine, *args, **kwargs) -> Callable:
        def wrapper(fn):
            cls.register_at_rollback(engine, fn, *args, **kwargs)
            return fn

        return wrapper

    @classmethod
    def listens_for_rollback_savepoint(cls, engine, *args, **kwargs) -> Callable:
        def wrapper(fn):
            cls.register_at_rollback_savepoint(engine, fn, *args, **kwargs)
            return fn

        return wrapper

    @classmethod
    def listens_for_checkin(cls, engine, *args, **kwargs) -> Callable:
        def wrapper(fn):
            cls.register_at_checkin(engine, fn, *args, **kwargs)
            return fn

        return wrapper
