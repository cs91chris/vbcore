try:
    # priority to the installed package: pip install flatdict
    from flatdict import FlatDict, FlatterDict  # type: ignore[import]
except ImportError:
    from .flatter_dict import FlatDict, FlatterDict
