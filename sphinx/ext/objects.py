# -*- coding: utf-8 -*-

# Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# There is NO WARRANTY.

# Special object types for the header survey documentation.
# This might wind up getting promoted to a full domain eventually.

import re
from docutils import nodes, utils
from sphinx import addnodes

# This is like sphinx.roles.emph_literal_role, but without the
# hardwired nodes.literal as the root or nodes.emphasis to mark
# variable bits.
litvar_re = re.compile('{([^}]+)}')
def parse_litvar(text, varnode):
    nodelist = []
    text = utils.unescape(text)
    pos = 0
    for m in litvar_re.finditer(text):
        if m.start() > pos:
            txt = text[pos:m.start()]
            nodelist.append(nodes.Text(txt, txt))
        nodelist.append(varnode(m.group(1), m.group(1)))
        pos = m.end()
    if pos < len(text):
        txt = text[pos:]
        nodelist.append(nodes.Text(txt, txt))
    return nodelist

def mark_descname(parsed):
    label = parsed[0].astext()
    paren = None
    if label.endswith('('):
        label = label[:-1]
        paren = nodes.Text('(', '(')

    parsed[0] = addnodes.desc_name(label, label)
    if paren is not None:
        parsed.insert(1, paren)

    return label

keyval_re = re.compile(r'\A([A-Za-z0-9.,/$_{}-]+)\s*=\s*(.+)\Z')

def parse_keyval(env, sig, signode):
    m = keyval_re.match(sig)
    if not m:
        desc = addnodes.desc_name(rawsource=sig)
        desc.extend(parse_litvar(sig, addnodes.desc_parameter))
        signode += desc
        return sig

    parsed_key = parse_litvar(m.group(1), addnodes.desc_parameter)
    parsed_val = parse_litvar(m.group(2), addnodes.desc_parameter)

    if isinstance(parsed_key[0], nodes.Text):
        label = mark_descname(parsed_key)

    elif isinstance(parsed_val[0], nodes.Text):
        label = mark_descname(parsed_val)

    else:
        label = ''

    signode.extend(parsed_key)
    signode.append(nodes.Text(' = ', ' = '))
    signode.extend(parsed_val)

    return label

def setup(app):
    app.add_object_type('convention', 'cvn', 'pair: %s; syntactic convention',
                        ref_nodeclass=nodes.generated)

    app.add_object_type('prop', 'prop', 'pair: %s; config property')

    # Keyvals are too complicated to auto-index.
    app.add_object_type('keyval', 'kv', '',
                        parse_node=parse_keyval)
