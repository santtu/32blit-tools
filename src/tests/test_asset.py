import pathlib

from ttblit.asset.formatter import AssetFormatter
from ttblit.asset import Asset


def test_formatter_components():
    """Verify formatter results contain the declared components."""
    data = 'hello', Asset(b'hello', {"a": 1})
    path = pathlib.Path('/no/such/path')

    for name, formatter in AssetFormatter._by_name.items():
        fragments = formatter.fragments(*data)
        assert tuple(fragments.keys()) == formatter.components
        listified = {k: [v] for k, v in fragments.items()}
        result = formatter.join(path, listified)
        assert tuple(result.keys()) == formatter.components
