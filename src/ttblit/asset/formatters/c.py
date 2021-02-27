import textwrap
import re

from ..formatter import AssetFormatter

wrapper = textwrap.TextWrapper(
    initial_indent='    ', subsequent_indent='    ', width=80
)


def name_to_cname(s):
    return re.sub(r'\W|^(?=\d)', '_', s)


def type_to_ctype(t):
    if t is int:
        return "int"
    elif t is str:
        return "const char *"
    else:
        assert False, "type {t!r} not handled"


def type_to_default(t):
    if t is int:
        return "0";
    elif t is str:
        return "(char*) 0";
    else:
        assert False, "type {t!r} not handled"


def value_to_cvalue(v):
    if isinstance(v, int):
        return str(v)
    elif isinstance(v, str):
        return '\"' + re.sub(r'([^\w\s])', lambda m: ''.join([f'\\x{c:02x}' for c in m.group(1).encode('utf-8')]), v) + '\"'


def c_attr_initializer(symbol, asset):
    c_fields = [f'  .{name_to_cname(k)} = {value_to_cvalue(v)}' for k, v in asset.attributes.items() if v is not None]
    return (f'const ttblit_attrs_t {symbol}_attrs = {{\n' +
            ',\n'.join(c_fields) +
            '};\n')


def c_attr_type_declaration(types):
    c_fields = [f'  {type_to_ctype(v)} {name_to_cname(k)} = {type_to_default(v)}' for k, v in types.items()]

    return ('typedef struct ttblit_attrs {\n' +
            ';\n'.join(c_fields) +
            ';\n} ttblit_attrs_t;\n')


def c_attr_declaration(symbol):
    return f'extern const ttblit_attrs_t {symbol}_attrs;'


def c_initializer(asset):
    if type(asset.data) is str:
        data = asset.data.encode('utf-8')
    else:
        data = asset.data
    values = ', '.join(f'0x{c:02x}' for c in data)
    return f' = {{\n{wrapper.fill(values)}\n}}'


def c_declaration(types, symbol, data=None):
    return textwrap.dedent(
        '''\
        {types} uint8_t {symbol}[]{initializer};
        {types} uint32_t {symbol}_length{size};
        '''
    ).format(
        types=types,
        symbol=symbol,
        initializer=c_initializer(data) if data else '',
        size=f' = sizeof({symbol})' if data else '',
    )


def c_boilerplate(data, include, header=True):
    lines = ['// Auto Generated File - DO NOT EDIT!']
    if header:
        lines.append('#pragma once')
    lines.append(f'#include <{include}>')
    lines.append('')
    lines.extend(data)
    return '\n'.join(lines)


@AssetFormatter(extensions=('.hpp', '.h'))
def c_header(symbol, asset):
    return {None: c_declaration('inline const', symbol, asset)}


@c_header.joiner
def c_header(path, fragments):
    return {None: c_boilerplate(fragments[None], include="cstdint", header=True)}


@c_header.attribute_typer
def c_header(types):
    return {None: c_attr_declaration(types)}


@c_header.attributer
def c_header(symbol, asset):
    return {None: c_attr_initializer(symbol, asset)}



@AssetFormatter(components=('hpp', 'cpp'), extensions=('.cpp', '.c'))
def c_source(symbol, asset):
    return {
        'hpp': c_declaration('extern const', symbol),
        'cpp': c_declaration('const', symbol, asset),
    }


@c_source.joiner
def c_source(path, fragments):
    include = path.with_suffix('.hpp').name
    return {
        'hpp': c_boilerplate(fragments['hpp'], include='cstdint', header=True),
        'cpp': c_boilerplate(fragments['cpp'], include=include, header=False),
    }


@c_source.attributer
def c_source(symbol, asset):
    return {"cpp": c_attr_initializer(symbol, asset),
            "hpp": c_attr_declaration(symbol)}


@c_source.attribute_typer
def c_source(types):
    return {"hpp": c_attr_type_declaration(types)}
