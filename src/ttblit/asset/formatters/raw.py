from ..formatter import AssetFormatter


@AssetFormatter(extensions=('.raw', '.bin'))
def raw_binary(symbol, asset):
    return {None: asset.data}


@raw_binary.joiner
def raw_binary(path, fragments):
    return {None: b''.join(fragments[None])}
