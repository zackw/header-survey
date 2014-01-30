# -*- coding: utf-8 -*-

# Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# There is NO WARRANTY.

# Much of the code in this file is copied with only small changes from
# docutils.writers.html4css1 by David Goodger (which is in the
# public domain) and sphinx.writers.html (BSD-licensed).

__docformat__ = 'reStructuredText'

import sys
import posixpath
import os.path
import re
import urllib.request
try: # check for the Python Imaging Library
    import PIL.Image
except ImportError:
    try:  # sometimes PIL modules are put in PYTHONPATH's root
        import Image
        class PIL(object): pass  # dummy wrapper
        PIL.Image = Image
    except ImportError:
        PIL = None
import docutils
from docutils import frontend, nodes, utils, writers, languages, io
from docutils.utils.error_reporting import SafeString
from docutils.transforms import writer_aux
from docutils.utils.math import unichar2tex, pick_math_environment, math2html
from docutils.utils.math.latex2mathml import parse_latex_math
from docutils.writers.html4css1 import SimpleListChecker

from sphinx import addnodes
from sphinx.locale import admonitionlabels, _
from sphinx.util.smartypants import sphinx_smarty_pants
from sphinx.writers.html import HTMLTranslator as SphinxHTMLTranslator

class BaseTranslator(nodes.NodeVisitor):
    """This class is a clone of
       docutils.writers.html4css1.HTMLTranslator, systematically
       modified to generate HTML5 instead of HTML4.  In large part
       this means using new semantic tags instead of <div>, <span>,
       <tt>, etc. with semantic classes.  We have also cleaned out all
       the XML-isms and gratuitous type tags."""

    doctype = '<!doctype html>\n'
    head_prefix_template = ('<html lang="%(lang)s">\n<head>\n')
    charset_decl = '<meta charset="%s">\n'

    generator = ('<meta name="generator" content="Docutils %s: '
                 'http://docutils.sourceforge.net/">\n')

    # Template for the MathJax script in the header:
    mathjax_script = '<script src="%s"></script>\n'
    # The latest version of MathJax from the distributed server:
    # avaliable to the public under the `MathJax CDN Terms of Service`__
    # __http://www.mathjax.org/download/mathjax-cdn-terms-of-service/
    mathjax_url = ('http://cdn.mathjax.org/mathjax/latest/MathJax.js?'
                   'config=TeX-AMS-MML_HTMLorMML')
    # may be overwritten by custom URL appended to "mathjax"

    stylesheet_link = '<link rel="stylesheet" href="%s">\n'
    embedded_stylesheet = '<style>\n%s\n</style>\n'
    words_and_spaces = re.compile(r'[\S\u00a0]+|\s+', re.U)
    # wrap point inside word
    sollbruchstelle = re.compile(r'.+\W\W.+|[-?].+', re.U)

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        lcode = settings.language_code
        self.language = languages.get_language(lcode, document.reporter)
        self.meta = [self.generator % docutils.__version__]
        self.head_prefix = []
        self.html_prolog = []
        self.head = self.meta[:]
        self.stylesheet = [self.stylesheet_call(path)
                           for path in utils.get_stylesheet_list(settings)]
        self.body_prefix = ['</head>\n<body>\n']
        # document title, subtitle display
        self.body_pre_docinfo = []
        # author, date, etc.
        self.docinfo = []
        self.body = []
        self.fragment = []
        self.body_suffix = ['</body>\n</html>\n']
        self.section_level = 0
        self.initial_header_level = int(settings.initial_header_level)

        self.math_output = settings.math_output.split()
        self.math_output_options = self.math_output[1:]
        self.math_output = self.math_output[0].lower()

        # A heterogenous stack used in conjunction with the tree traversal.
        # Make sure that the pops correspond to the pushes:
        self.context = []
        self.topic_classes = []
        self.colspecs = []
        self.compact_p = True
        self.compact_simple = False
        self.compact_field_list = False
        self.in_docinfo = False
        self.in_sidebar = False
        self.title = []
        self.subtitle = []
        self.header = []
        self.footer = []
        self.html_head = []
        self.html_title = []
        self.html_subtitle = []
        self.html_body = []
        self.in_document_title = 0   # len(self.body) or 0
        self.in_mailto = False
        self.author_in_authors = False
        self.math_header = []

    def astext(self):
        return ''.join(self.head_prefix + self.head
                       + self.stylesheet + self.body_prefix
                       + self.body_pre_docinfo + self.docinfo
                       + self.body + self.body_suffix)

    def encode(self, text):
        """Encode special characters in `text` & return."""
        # @@@ A codec to do these and all other HTML entities would be nice.
        text = str(text)
        return text.translate({
            ord('&'): '&amp;',
            ord('<'): '&lt;',
            ord('"'): '&quot;',
            ord('>'): '&gt;',
            ord('@'): '&#64;', # may thwart some address harvesters
            # TODO: convert non-breaking space only if needed?
            0xa0: '&nbsp;'}) # non-breaking space

    def cloak_mailto(self, uri):
        """Try to hide a mailto: URL from harvesters."""
        # Encode "@" using a URL octet reference (see RFC 1738).
        # Further cloaking with HTML entities will be done in the
        # `attval` function.
        return uri.replace('@', '%40')

    def cloak_email(self, addr):
        """Try to hide the link text of a email link from harversters."""
        # Surround at-signs and periods with <span> tags.  ("@" has
        # already been encoded to "&#64;" by the `encode` method.)
        addr = addr.replace('&#64;', '<span>&#64;</span>')
        addr = addr.replace('.', '<span>&#46;</span>')
        return addr

    def attval(self, text,
               whitespace=re.compile('[\n\r\t\v\f]')):
        """Cleanse, HTML encode, and return attribute value text."""
        encoded = self.encode(whitespace.sub(' ', text))
        if self.in_mailto and self.settings.cloak_email_addresses:
            # Cloak at-signs ("%40") and periods with HTML entities.
            encoded = encoded.replace('%40', '&#37;&#52;&#48;')
            encoded = encoded.replace('.', '&#46;')
        return encoded

    def stylesheet_call(self, path):
        """Return code to reference or embed stylesheet file `path`"""
        if self.settings.embed_stylesheet:
            try:
                content = io.FileInput(source_path=path,
                                       encoding='utf-8').read()
                self.settings.record_dependencies.add(path)
            except IOError as err:
                msg = "Cannot embed stylesheet '%s': %s." % (
                                path, SafeString(err.strerror))
                self.document.reporter.error(msg)
                return '<--- %s --->\n' % msg
            return self.embedded_stylesheet % content
        # else link to style file:
        if self.settings.stylesheet_path:
            # adapt path relative to output (cf. config.html#stylesheet-path)
            path = utils.relative_path(self.settings._destination, path)
        return self.stylesheet_link % self.encode(path)

    def starttag(self, node, tagname, suffix='\n', empty=False, **attributes):
        """
        Construct and return a start tag given a node (id & class attributes
        are extracted), tag name, and optional attributes.
        """
        tagname = tagname.lower()
        prefix = []
        atts = {}
        ids = []
        for (name, value) in list(attributes.items()):
            atts[name.lower()] = value
        classes = []
        languages = []
        # unify class arguments and move language specification
        for cls in node.get('classes', []) + atts.pop('class', '').split() :
            if cls.startswith('language-'):
                languages.append(cls[9:])
            elif cls.strip() and cls not in classes:
                classes.append(cls)
        if languages:
            atts['lang'] = languages[0]
        if classes:
            atts['class'] = ' '.join(classes)
        assert 'id' not in atts
        ids.extend(node.get('ids', []))
        if 'ids' in atts:
            ids.extend(atts['ids'])
            del atts['ids']
        if ids:
            atts['id'] = ids[0]
            for id in ids[1:]:
                # Add empty "span" elements for additional IDs.
                # (I'm not sure what the status of nested "a" elements
                # is in HTML5, but in any case <a> to create a link *target*
                # appears to be deprecated.)
                if empty:
                    # Empty tag.  Insert target right in front of element.
                    prefix.append('<span id="%s"></span>' % id)
                else:
                    # Non-empty tag.  Place the auxiliary <span> tag
                    # *inside* the element, as the first child.
                    suffix += '<span id="%s"></span>' % id
        attlist = list(atts.items())
        attlist.sort()
        parts = [tagname]
        for name, value in attlist:
            # value=None was used for boolean attributes without
            # value, but this wasn't supported by XHTML and so was
            # deprecated on the input side; we retain this
            # strictness. Generating compact attributes when possible
            # is too much work.
            assert value is not None
            if isinstance(value, list):
                values = [str(v) for v in value]
                parts.append('%s="%s"' % (name.lower(),
                                          self.attval(' '.join(values))))
            else:
                parts.append('%s="%s"' % (name.lower(),
                                          self.attval(str(value))))
        return ''.join(prefix) + '<%s>' % (' '.join(parts)) + suffix

    def emptytag(self, node, tagname, suffix='\n', **attributes):
        """Construct and return an empty tag."""
        return self.starttag(node, tagname, suffix, empty=True, **attributes)

    def set_class_on_child(self, node, class_, index=0):
        """
        Set class `class_` on the visible child no. index of `node`.
        Do nothing if node has fewer children than `index`.
        """
        children = [n for n in node if not isinstance(n, nodes.Invisible)]
        try:
            child = children[index]
        except IndexError:
            return
        child['classes'].append(class_)

    def set_first_last(self, node):
        self.set_class_on_child(node, 'first', 0)
        self.set_class_on_child(node, 'last', -1)

    def visit_Text(self, node):
        text = node.astext()
        encoded = self.encode(text)
        if self.in_mailto and self.settings.cloak_email_addresses:
            encoded = self.cloak_email(encoded)
        self.body.append(encoded)

    def depart_Text(self, node):
        pass

    def visit_abbreviation(self, node):
        # @@@ implementation incomplete ("title" attribute)
        self.body.append(self.starttag(node, 'abbr', ''))

    def depart_abbreviation(self, node):
        self.body.append('</abbr>')

    def visit_acronym(self, node):
        # @@@ implementation incomplete ("title" attribute)
        self.body.append(self.starttag(node, 'acronym', ''))

    def depart_acronym(self, node):
        self.body.append('</acronym>')

    def visit_address(self, node):
        # @@@ Not using '<address>' here because I'm not sure whether
        # this is guaranteed only to be used for "the contact information
        # for [the document]".
        self.visit_docinfo_item(node, 'address', meta=False)
        self.body.append(self.starttag(node, 'pre', CLASS='address'))

    def depart_address(self, node):
        self.body.append('\n</pre>\n')
        self.depart_docinfo_item()

    def visit_admonition(self, node):
        # ??? Might be appropriate to change this to <p> or <aside>.
        self.body.append(self.starttag(node, 'div'))
        self.set_first_last(node)

    def depart_admonition(self, node=None):
        self.body.append('</div>\n')

    attribution_formats = {'dash': ('&mdash;', ''),
                           'parentheses': ('(', ')'),
                           'parens': ('(', ')'),
                           'none': ('', '')}

    def visit_attribution(self, node):
        # ??? If this is used exclusively in conjunction with block
        # quotes, we could wrap <figure> around the whole thing and
        # use <figcaption> here.
        prefix, suffix = self.attribution_formats[self.settings.attribution]
        self.context.append(suffix)
        self.body.append(
            self.starttag(node, 'p', prefix, CLASS='attribution'))

    def depart_attribution(self, node):
        self.body.append(self.context.pop() + '</p>\n')

    def visit_author(self, node):
        if isinstance(node.parent, nodes.authors):
            if self.author_in_authors:
                self.body.append('\n<br>')
        else:
            self.visit_docinfo_item(node, 'author')

    def depart_author(self, node):
        if isinstance(node.parent, nodes.authors):
            self.author_in_authors = True
        else:
            self.depart_docinfo_item()

    def visit_authors(self, node):
        self.visit_docinfo_item(node, 'authors')
        self.author_in_authors = False  # initialize

    def depart_authors(self, node):
        self.depart_docinfo_item()

    def visit_block_quote(self, node):
        self.body.append(self.starttag(node, 'blockquote'))

    def depart_block_quote(self, node):
        self.body.append('</blockquote>\n')

    def check_simple_list(self, node):
        """Check for a simple list that can be rendered compactly."""
        visitor = SimpleListChecker(self.document)
        try:
            node.walk(visitor)
        except nodes.NodeFound:
            return None
        else:
            return 1

    def is_compactable(self, node):
        return ('compact' in node['classes']
                or (self.settings.compact_lists
                    and 'open' not in node['classes']
                    and (self.compact_simple
                         or self.topic_classes == ['contents']
                         or self.check_simple_list(node))))

    def visit_bullet_list(self, node):
        atts = {}
        old_compact_simple = self.compact_simple
        self.context.append((self.compact_simple, self.compact_p))
        self.compact_p = None
        self.compact_simple = self.is_compactable(node)
        if self.compact_simple and not old_compact_simple:
            atts['class'] = 'simple'
        self.body.append(self.starttag(node, 'ul', **atts))

    def depart_bullet_list(self, node):
        self.compact_simple, self.compact_p = self.context.pop()
        self.body.append('</ul>\n')

    def visit_caption(self, node):
        # ??? It would be appropriate to use <figcaption> here but we
        # would need to ensure a parent <figure>.
        self.body.append(self.starttag(node, 'p', '', CLASS='caption'))

    def depart_caption(self, node):
        self.body.append('</p>\n')

    def visit_citation(self, node):
        # @@@ Evil use of table for layout.  If only <dl compact> worked...
        self.body.append(self.starttag(node, 'table',
                                       CLASS='docutils citation',
                                       frame="void", rules="none"))
        self.body.append('<colgroup><col class="label"><col></colgroup>\n'
                         '<tbody valign="top">\n'
                         '<tr>')
        self.footnote_backrefs(node)

    def depart_citation(self, node):
        self.body.append('</td></tr>\n'
                         '</tbody>\n</table>\n')

    def visit_citation_reference(self, node):
        href = '#'
        if 'refid' in node:
            href += node['refid']
        elif 'refname' in node:
            href += self.document.nameids[node['refname']]
        # else: # TODO system message (or already in the transform)?
        # 'Citation reference missing.'
        self.body.append(self.starttag(
            node, 'a', '[', CLASS='citation-reference', href=href))

    def depart_citation_reference(self, node):
        self.body.append(']</a>')

    def visit_classifier(self, node):
        self.body.append(' <span class="classifier-delimiter">:</span> ')
        self.body.append(self.starttag(node, 'span', '', CLASS='classifier'))

    def depart_classifier(self, node):
        self.body.append('</span>')

    def visit_colspec(self, node):
        self.colspecs.append(node)
        # "stubs" list is an attribute of the tgroup element:
        node.parent.stubs.append(node.attributes.get('stub'))

    def depart_colspec(self, node):
        pass

    def write_colspecs(self):
        width = 0
        for node in self.colspecs:
            width += node['colwidth']
        for node in self.colspecs:
            colwidth = int(node['colwidth'] * 100.0 / width + 0.5)
            self.body.append(self.emptytag(node, 'col',
                                           width='%i%%' % colwidth))
        self.colspecs = []

    def visit_comment(self, node,
                      sub=re.compile('-(?=-)').sub):
        """Escape double-dashes in comment text."""
        self.body.append('<!-- %s -->\n' % sub('- ', node.astext()))
        # Content already processed:
        raise nodes.SkipNode

    def visit_compound(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='compound'))
        if len(node) > 1:
            node[0]['classes'].append('compound-first')
            node[-1]['classes'].append('compound-last')
            for child in node[1:-1]:
                child['classes'].append('compound-middle')

    def depart_compound(self, node):
        self.body.append('</div>\n')

    def visit_container(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='container'))

    def depart_container(self, node):
        self.body.append('</div>\n')

    def visit_contact(self, node):
        self.visit_docinfo_item(node, 'contact', meta=False)

    def depart_contact(self, node):
        self.depart_docinfo_item()

    def visit_copyright(self, node):
        self.visit_docinfo_item(node, 'copyright')

    def depart_copyright(self, node):
        self.depart_docinfo_item()

    def visit_date(self, node):
        self.visit_docinfo_item(node, 'date')

    def depart_date(self, node):
        self.depart_docinfo_item()

    def visit_decoration(self, node):
        pass

    def depart_decoration(self, node):
        pass

    def visit_definition(self, node):
        self.body.append('</dt>\n')
        self.body.append(self.starttag(node, 'dd', ''))
        self.set_first_last(node)

    def depart_definition(self, node):
        self.body.append('</dd>\n')

    def visit_definition_list(self, node):
        # ??? Gratuitous class?
        self.body.append(self.starttag(node, 'dl', CLASS='docutils'))

    def depart_definition_list(self, node):
        self.body.append('</dl>\n')

    def visit_definition_list_item(self, node):
        pass

    def depart_definition_list_item(self, node):
        pass

    def visit_description(self, node):
        self.body.append(self.starttag(node, 'td', ''))
        self.set_first_last(node)

    def depart_description(self, node):
        self.body.append('</td>')

    def visit_docinfo(self, node):
        # @@@ Evil use of table for layout.  If only <dl compact> worked...
        self.context.append(len(self.body))
        self.body.append(self.starttag(node, 'table',
                                       CLASS='docinfo',
                                       frame="void", rules="none"))
        self.body.append('<col class="docinfo-name">\n'
                         '<col class="docinfo-content">\n'
                         '<tbody valign="top">\n')
        self.in_docinfo = True

    def depart_docinfo(self, node):
        self.body.append('</tbody>\n</table>\n')
        self.in_docinfo = False
        start = self.context.pop()
        self.docinfo = self.body[start:]
        self.body = []

    def visit_docinfo_item(self, node, name, meta=True):
        if meta:
            meta_tag = '<meta name="%s" content="%s">\n' \
                       % (name, self.attval(node.astext()))
            self.add_meta(meta_tag)
        self.body.append(self.starttag(node, 'tr', ''))
        self.body.append('<th class="docinfo-name">%s:</th>\n<td>'
                         % self.language.labels[name])
        if len(node):
            if isinstance(node[0], nodes.Element):
                node[0]['classes'].append('first')
            if isinstance(node[-1], nodes.Element):
                node[-1]['classes'].append('last')

    def depart_docinfo_item(self):
        self.body.append('</td></tr>\n')

    def visit_doctest_block(self, node):
        self.body.append(self.starttag(node, 'pre', CLASS='doctest-block'))

    def depart_doctest_block(self, node):
        self.body.append('\n</pre>\n')

    def visit_document(self, node):
        self.head.append('<title>%s</title>\n'
                         % self.encode(node.get('title', '')))

    def depart_document(self, node):
        self.head_prefix.extend([self.doctype,
                                 self.head_prefix_template %
                                 {'lang': self.settings.language_code}])
        self.html_prolog.append(self.doctype)
        self.meta.insert(0, self.charset_decl % self.settings.output_encoding)
        self.head.insert(0, self.charset_decl % self.settings.output_encoding)
        if self.math_header:
            if self.math_output == 'mathjax':
                self.head.extend(self.math_header)
            else:
                self.stylesheet.extend(self.math_header)
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.body_prefix.append(self.starttag(node, 'main'))
        self.body_suffix.insert(0, '</main>\n')
        self.fragment.extend(self.body) # self.fragment is the "naked" body
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])
        assert not self.context, 'len(context) = %s' % len(self.context)

    def visit_emphasis(self, node):
        self.body.append(self.starttag(node, 'em', ''))

    def depart_emphasis(self, node):
        self.body.append('</em>')

    def visit_entry(self, node):
        atts = {'class': []}
        if isinstance(node.parent.parent, nodes.thead):
            atts['class'].append('head')
        if node.parent.parent.parent.stubs[node.parent.column]:
            # "stubs" list is an attribute of the tgroup element
            atts['class'].append('stub')
        if atts['class']:
            tagname = 'th'
            atts['class'] = ' '.join(atts['class'])
        else:
            tagname = 'td'
            del atts['class']
        node.parent.column += 1
        if 'morerows' in node:
            atts['rowspan'] = node['morerows'] + 1
        if 'morecols' in node:
            atts['colspan'] = node['morecols'] + 1
            node.parent.column += node['morecols']
        self.body.append(self.starttag(node, tagname, '', **atts))
        self.context.append('</%s>\n' % tagname.lower())
        if len(node) == 0:              # empty cell
            self.body.append('&nbsp;')
        self.set_first_last(node)

    def depart_entry(self, node):
        self.body.append(self.context.pop())

    def visit_enumerated_list(self, node):
        atts = {}
        if 'start' in node:
            # 'start' was restored to acceptability by HTML5 after
            # cooler heads realized that the numbering of ordered
            # lists is, in fact, part of the content.  It must be an
            # integer, though.
            atts['start'] = str(int(node['start']))
        if 'enumtype' in node:
            atts['class'] = node['enumtype']
        # @@@ To do: prefix, suffix. How? Change prefix/suffix to a
        # single "format" attribute? Use CSS2?
        old_compact_simple = self.compact_simple
        self.context.append((self.compact_simple, self.compact_p))
        self.compact_p = None
        self.compact_simple = self.is_compactable(node)
        if self.compact_simple and not old_compact_simple:
            atts['class'] = (atts.get('class', '') + ' simple').strip()
        self.body.append(self.starttag(node, 'ol', **atts))

    def depart_enumerated_list(self, node):
        self.compact_simple, self.compact_p = self.context.pop()
        self.body.append('</ol>\n')

    def visit_field(self, node):
        self.body.append(self.starttag(node, 'tr', '', CLASS='field'))

    def depart_field(self, node):
        self.body.append('</tr>\n')

    def visit_field_body(self, node):
        self.body.append(self.starttag(node, 'td', '', CLASS='field-body'))
        self.set_class_on_child(node, 'first', 0)
        field = node.parent
        if (self.compact_field_list or
            isinstance(field.parent, nodes.docinfo) or
            field.parent.index(field) == len(field.parent) - 1):
            # If we are in a compact list, the docinfo, or if this is
            # the last field of the field list, do not add vertical
            # space after last element.
            self.set_class_on_child(node, 'last', -1)

    def depart_field_body(self, node):
        self.body.append('</td>\n')

    def visit_field_list(self, node):
        # @@@ Evil use of table for layout.  If only <dl compact> worked...
        self.context.append((self.compact_field_list, self.compact_p))
        self.compact_p = None
        if 'compact' in node['classes']:
            self.compact_field_list = True
        elif (self.settings.compact_field_lists
              and 'open' not in node['classes']):
            self.compact_field_list = True
        if self.compact_field_list:
            for field in node:
                field_body = field[-1]
                assert isinstance(field_body, nodes.field_body)
                children = [n for n in field_body
                            if not isinstance(n, nodes.Invisible)]
                if not (len(children) == 0 or
                        len(children) == 1 and
                        isinstance(children[0],
                                   (nodes.paragraph, nodes.line_block))):
                    self.compact_field_list = False
                    break
        self.body.append(self.starttag(node, 'table', frame='void',
                                       rules='none',
                                       CLASS='docutils field-list'))
        self.body.append('<col class="field-name">\n'
                         '<col class="field-body">\n'
                         '<tbody valign="top">\n')

    def depart_field_list(self, node):
        self.body.append('</tbody>\n</table>\n')
        self.compact_field_list, self.compact_p = self.context.pop()

    def visit_field_name(self, node):
        atts = {}
        if self.in_docinfo:
            atts['class'] = 'docinfo-name'
        else:
            atts['class'] = 'field-name'
        if ( self.settings.field_name_limit
             and len(node.astext()) > self.settings.field_name_limit):
            atts['colspan'] = 2
            self.context.append('</tr>\n'
                                + self.starttag(node.parent, 'tr', '',
                                                CLASS='field')
                                + '<td>&nbsp;</td>')
        else:
            self.context.append('')
        self.body.append(self.starttag(node, 'th', '', **atts))

    def depart_field_name(self, node):
        self.body.append(':</th>')
        self.body.append(self.context.pop())

    def visit_figure(self, node):
        if node.get('width'):
            atts['style'] = 'width: %s' % node['width']
        if node.get('align'):
            atts['class'] += " align-" + node['align']
        self.body.append(self.starttag(node, 'figure'))

    def depart_figure(self, node):
        self.body.append('</figure>\n')

    def visit_footer(self, node):
        self.context.append(len(self.body))

    def depart_footer(self, node):
        start = self.context.pop()
        footer = [self.starttag(node, 'footer')]
        footer.extend(self.body[start:])
        footer.append('\n</footer>\n')
        self.footer.extend(footer)
        self.body_suffix[:0] = footer
        del self.body[start:]

    def visit_footnote(self, node):
        # @@@ Evil use of table for layout.  Not clear why in this instance.
        self.body.append(self.starttag(node, 'table',
                                       CLASS='docutils footnote',
                                       frame="void", rules="none"))
        self.body.append('<colgroup><col class="label"><col></colgroup>\n'
                         '<tbody valign="top">\n'
                         '<tr>')
        self.footnote_backrefs(node)

    def footnote_backrefs(self, node):
        backlinks = []
        backrefs = node['backrefs']
        if self.settings.footnote_backlinks and backrefs:
            if len(backrefs) == 1:
                self.context.append('')
                self.context.append('</a>')
                self.context.append('<a class="fn-backref" href="#%s">'
                                    % backrefs[0])
            else:
                i = 1
                for backref in backrefs:
                    backlinks.append('<a class="fn-backref" href="#%s">%s</a>'
                                     % (backref, i))
                    i += 1
                self.context.append('<em>(%s)</em> ' % ', '.join(backlinks))
                self.context += ['', '']
        else:
            self.context.append('')
            self.context += ['', '']
        # If the node does not only consist of a label.
        if len(node) > 1:
            # If there are preceding backlinks, we do not set class
            # 'first', because we need to retain the top-margin.
            if not backlinks:
                node[1]['classes'].append('first')
            node[-1]['classes'].append('last')

    def depart_footnote(self, node):
        self.body.append('</td></tr>\n'
                         '</tbody>\n</table>\n')

    def visit_footnote_reference(self, node):
        href = '#' + node['refid']
        format = self.settings.footnote_references
        if format == 'brackets':
            suffix = '['
            self.context.append(']')
        else:
            assert format == 'superscript'
            suffix = '<sup>'
            self.context.append('</sup>')
        self.body.append(self.starttag(node, 'a', suffix,
                                       CLASS='footnote-reference', href=href))

    def depart_footnote_reference(self, node):
        self.body.append(self.context.pop() + '</a>')

    def visit_generated(self, node):
        pass

    def depart_generated(self, node):
        pass

    def visit_header(self, node):
        self.context.append(len(self.body))

    def depart_header(self, node):
        start = self.context.pop()
        header = [self.starttag(node, 'header')]
        header.extend(self.body[start:])
        header.append('\n</header>\n')
        self.body_prefix.extend(header)
        self.header.extend(header)
        del self.body[start:]

    def visit_image(self, node):
        atts = {}
        uri = node['uri']
        # SVG works in <img> now
        # place SWF images in an <object> element
        types = {'.swf': 'application/x-shockwave-flash'}
        ext = os.path.splitext(uri)[1].lower()
        if ext == '.swf':
            atts['data'] = uri
            atts['type'] = types[ext]
        else:
            atts['src'] = uri
            atts['alt'] = node.get('alt', uri)
        # image size
        if 'width' in node:
            atts['width'] = node['width']
        if 'height' in node:
            atts['height'] = node['height']
        if 'scale' in node:
            if (PIL and not ('width' in node and 'height' in node)
                and self.settings.file_insertion_enabled):
                imagepath = urllib.request.url2pathname(uri)
                try:
                    img = PIL.Image.open(
                            imagepath.encode(sys.getfilesystemencoding()))
                except (IOError, UnicodeEncodeError):
                    pass # TODO: warn?
                else:
                    self.settings.record_dependencies.add(
                        imagepath.replace('\\', '/'))
                    if 'width' not in atts:
                        atts['width'] = str(img.size[0])
                    if 'height' not in atts:
                        atts['height'] = str(img.size[1])
                    del img
            for att_name in 'width', 'height':
                if att_name in atts:
                    match = re.match(r'([0-9.]+)(\S*)$', atts[att_name])
                    assert match
                    atts[att_name] = '%s%s' % (
                        float(match.group(1)) * (float(node['scale']) / 100),
                        match.group(2))
        style = []
        for att_name in 'width', 'height':
            if att_name in atts:
                if re.match(r'^[0-9.]+$', atts[att_name]):
                    # Interpret unitless values as pixels.
                    atts[att_name] += 'px'
                style.append('%s: %s;' % (att_name, atts[att_name]))
                del atts[att_name]
        if style:
            atts['style'] = ' '.join(style)
        if (isinstance(node.parent, nodes.TextElement) or
            (isinstance(node.parent, nodes.reference) and
             not isinstance(node.parent.parent, nodes.TextElement))):
            # Inline context or surrounded by <a>...</a>.
            suffix = ''
        else:
            suffix = '\n'
        if 'align' in node:
            atts['class'] = 'align-%s' % node['align']
        self.context.append('')
        if ext == '.swf': # place in an object element,
            # do NOT use an empty tag: incorrect rendering in browsers
            self.body.append(self.starttag(node, 'object', suffix, **atts) +
                             node.get('alt', uri) + '</object>' + suffix)
        else:
            self.body.append(self.emptytag(node, 'img', suffix, **atts))

    def depart_image(self, node):
        self.body.append(self.context.pop())

    def visit_inline(self, node):
        self.body.append(self.starttag(node, 'span', ''))

    def depart_inline(self, node):
        self.body.append('</span>')

    def visit_label(self, node):
        # Context added in footnote_backrefs.
        self.body.append(self.starttag(node, 'td', '%s[' % self.context.pop(),
                                       CLASS='label'))

    def depart_label(self, node):
        # Context added in footnote_backrefs.
        self.body.append(']%s</td><td>%s' % (self.context.pop(), self.context.pop()))

    def visit_legend(self, node):
        # ??? <figcaption> might be appropriate here if we could ensure a
        # parent <figure>.
        self.body.append(self.starttag(node, 'div', CLASS='legend'))

    def depart_legend(self, node):
        self.body.append('</div>\n')

    def visit_line(self, node):
        # ??? What's this for?
        self.body.append(self.starttag(node, 'div', suffix='', CLASS='line'))
        if not len(node):
            self.body.append('<br>')

    def depart_line(self, node):
        self.body.append('</div>\n')

    def visit_line_block(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='line-block'))

    def depart_line_block(self, node):
        self.body.append('</div>\n')

    def visit_list_item(self, node):
        self.body.append(self.starttag(node, 'li', ''))
        if len(node):
            node[0]['classes'].append('first')

    def depart_list_item(self, node):
        self.body.append('</li>\n')

    def visit_literal(self, node):
        # special-case roles that map directly to HTML5 inline tags:
        html5_known_roles = ('code', 'kbd', 'samp', 'var')
        classes = node.get('classes', [])
        if not classes:
            self.body.append(self.starttag(node, 'code', ''))
            self.context.append('</code>')
            return
        for cls in classes:
            if cls in html5_known_roles:
                node['classes'] = [c for c in classes if c != cls]
                self.body.append(self.starttag(node, cls, ''))
                self.context.append('</%s>' % cls)
                return

        self.body.append(self.starttag(node, 'span', '', CLASS='literal'))

        # ??? This treatment is arguably appropriate for the above roles
        # as well.
        text = node.astext()
        for token in self.words_and_spaces.findall(text):
            if token.strip():
                # Protect text like "--an-option" and the regular expression
                # ``[+]?(\d+(\.\d*)?|\.\d+)`` from bad line wrapping
                if self.sollbruchstelle.search(token):
                    self.body.append('<span class="pre">%s</span>'
                                     % self.encode(token))
                else:
                    self.body.append(self.encode(token))
            elif token in ('\n', ' '):
                # Allow breaks at whitespace:
                self.body.append(token)
            else:
                # Protect runs of multiple spaces; the last space can wrap:
                self.body.append('&nbsp;' * (len(token) - 1) + ' ')
        self.body.append('</span>')
        # Content already processed:
        raise nodes.SkipNode

    def depart_literal(self, node):
        self.body.append(self.context.pop())

    def visit_literal_block(self, node):
        self.body.append(self.starttag(node, 'pre', CLASS='literal-block'))

    def depart_literal_block(self, node):
        self.body.append('\n</pre>\n')

    def visit_math(self, node, math_env=''):
        # If the method is called from visit_math_block(), math_env != ''.

        # As there is no native HTML math support, we provide alternatives:
        # LaTeX and MathJax math_output modes simply wrap the content,
        # HTML and MathML math_output modes also convert the math_code.
        if self.math_output not in ('mathml', 'html', 'mathjax', 'latex'):
            self.document.reporter.error(
                'math-output format "%s" not supported '
                'falling back to "latex"'% self.math_output)
            self.math_output = 'latex'
        #
        # HTML container
        tags = {# math_output: (block, inline, class-arguments)
                'mathml':      ('div', '', ''),
                'html':        ('div', 'span', 'formula'),
                'mathjax':     ('div', 'span', 'math'),
                'latex':       ('pre', 'code', 'math'),
               }
        tag = tags[self.math_output][math_env == '']
        clsarg = tags[self.math_output][2]
        # LaTeX container
        wrappers = {# math_mode: (inline, block)
                    'mathml':  (None,     None),
                    'html':    ('$%s$',   '\\begin{%s}\n%s\n\\end{%s}'),
                    'mathjax': ('\(%s\)', '\\begin{%s}\n%s\n\\end{%s}'),
                    'latex':   (None,     None),
                   }
        wrapper = wrappers[self.math_output][math_env != '']
        # get and wrap content
        math_code = node.astext().translate(unichar2tex.uni2tex_table)
        if wrapper and math_env:
            math_code = wrapper % (math_env, math_code, math_env)
        elif wrapper:
            math_code = wrapper % math_code
        # settings and conversion
        if self.math_output in ('latex', 'mathjax'):
            math_code = self.encode(math_code)
        if self.math_output == 'mathjax' and not self.math_header:
            if self.math_output_options:
                self.mathjax_url = self.math_output_options[0]
            self.math_header = [self.mathjax_script % self.mathjax_url]
        elif self.math_output == 'html':
            if self.math_output_options and not self.math_header:
                self.math_header = [self.stylesheet_call(
                    utils.find_file_in_dirs(s, self.settings.stylesheet_dirs))
                    for s in self.math_output_options[0].split(',')]
            # TODO: fix display mode in matrices and fractions
            math2html.DocumentParameters.displaymode = (math_env != '')
            math_code = math2html.math2html(math_code)
        elif self.math_output == 'mathml':
            self.doctype = self.doctype_mathml
            self.content_type = self.content_type_mathml
            try:
                mathml_tree = parse_latex_math(math_code, inline=not(math_env))
                math_code = ''.join(mathml_tree.xml())
            except SyntaxError as err:
                err_node = self.document.reporter.error(err, base_node=node)
                self.visit_system_message(err_node)
                self.body.append(self.starttag(node, 'p'))
                self.body.append(','.join(err.args))
                self.body.append('</p>\n')
                self.body.append(self.starttag(node, 'pre',
                                               CLASS='literal-block'))
                self.body.append(self.encode(math_code))
                self.body.append('\n</pre>\n')
                self.depart_system_message(err_node)
                raise nodes.SkipNode
        # append to document body
        if tag:
            self.body.append(self.starttag(node, tag,
                                           suffix='\n'*bool(math_env),
                                           CLASS=clsarg))
        self.body.append(math_code)
        if math_env:
            self.body.append('\n')
        if tag:
            self.body.append('</%s>\n' % tag)
        # Content already processed:
        raise nodes.SkipNode

    def depart_math(self, node):
        pass # never reached

    def visit_math_block(self, node):
        # print node.astext().encode('utf8')
        math_env = pick_math_environment(node.astext())
        self.visit_math(node, math_env=math_env)

    def depart_math_block(self, node):
        pass # never reached

    def visit_meta(self, node):
        meta = self.emptytag(node, 'meta', **node.non_default_attributes())
        self.add_meta(meta)

    def depart_meta(self, node):
        pass

    def add_meta(self, tag):
        self.meta.append(tag)
        self.head.append(tag)

    def visit_option(self, node):
        if self.context[-1]:
            self.body.append(', ')
        self.body.append(self.starttag(node, 'span', '', CLASS='option'))

    def depart_option(self, node):
        self.body.append('</span>')
        self.context[-1] += 1

    def visit_option_argument(self, node):
        self.body.append(node.get('delimiter', ' '))
        self.body.append(self.starttag(node, 'var', ''))

    def depart_option_argument(self, node):
        self.body.append('</var>')

    def visit_option_group(self, node):
        atts = {}
        if ( self.settings.option_limit
             and len(node.astext()) > self.settings.option_limit):
            atts['colspan'] = 2
            self.context.append('</tr>\n<tr><td>&nbsp;</td>')
        else:
            self.context.append('')
        self.body.append(
            self.starttag(node, 'td', CLASS='option-group', **atts))
        self.body.append('<kbd>')
        self.context.append(0)          # count number of options

    def depart_option_group(self, node):
        self.context.pop()
        self.body.append('</kbd></td>\n')
        self.body.append(self.context.pop())

    def visit_option_list(self, node):
        # @@@ Evil use of table for layout.  If only <dl compact> worked...
        self.body.append(
              self.starttag(node, 'table', CLASS='docutils option-list',
                            frame="void", rules="none"))
        self.body.append('<col class="option">\n'
                         '<col class="description">\n'
                         '<tbody valign="top">\n')

    def depart_option_list(self, node):
        self.body.append('</tbody>\n</table>\n')

    def visit_option_list_item(self, node):
        self.body.append(self.starttag(node, 'tr', ''))

    def depart_option_list_item(self, node):
        self.body.append('</tr>\n')

    def visit_option_string(self, node):
        pass

    def depart_option_string(self, node):
        pass

    def visit_organization(self, node):
        self.visit_docinfo_item(node, 'organization')

    def depart_organization(self, node):
        self.depart_docinfo_item()

    def should_be_compact_paragraph(self, node):
        """
        Determine if the <p> tags around paragraph ``node`` can be omitted.
        """
        if (isinstance(node.parent, nodes.document) or
            isinstance(node.parent, nodes.compound)):
            # Never compact paragraphs in document or compound.
            return False
        for key, value in node.attlist():
            if (node.is_not_default(key) and
                not (key == 'classes' and value in
                     ([], ['first'], ['last'], ['first', 'last']))):
                # Attribute which needs to survive.
                return False
        first = isinstance(node.parent[0], nodes.label) # skip label
        for child in node.parent.children[first:]:
            # only first paragraph can be compact
            if isinstance(child, nodes.Invisible):
                continue
            if child is node:
                break
            return False
        parent_length = len([n for n in node.parent if not isinstance(
            n, (nodes.Invisible, nodes.label))])
        if ( self.compact_simple
             or self.compact_field_list
             or self.compact_p and parent_length == 1):
            return True
        return False

    def visit_paragraph(self, node):
        if self.should_be_compact_paragraph(node):
            self.context.append('')
        else:
            self.body.append(self.starttag(node, 'p', ''))
            self.context.append('</p>\n')

    def depart_paragraph(self, node):
        self.body.append(self.context.pop())

    def visit_problematic(self, node):
        if node.hasattr('refid'):
            self.body.append('<a href="#%s">' % node['refid'])
            self.context.append('</a>')
        else:
            self.context.append('')
        self.body.append(self.starttag(node, 'span', '', CLASS='problematic'))

    def depart_problematic(self, node):
        self.body.append('</span>')
        self.body.append(self.context.pop())

    def visit_raw(self, node):
        if 'html' in node.get('format', '').split():
            t = isinstance(node.parent, nodes.TextElement) and 'span' or 'div'
            if node['classes']:
                self.body.append(self.starttag(node, t, suffix=''))
            self.body.append(node.astext())
            if node['classes']:
                self.body.append('</%s>' % t)
        # Keep non-HTML raw text out of output:
        raise nodes.SkipNode

    def visit_reference(self, node):
        atts = {'class': 'reference'}
        if 'refuri' in node:
            atts['href'] = node['refuri']
            if ( self.settings.cloak_email_addresses
                 and atts['href'].startswith('mailto:')):
                atts['href'] = self.cloak_mailto(atts['href'])
                self.in_mailto = True
            atts['class'] += ' external'
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            atts['href'] = '#' + node['refid']
            atts['class'] += ' internal'
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        self.body.append(self.starttag(node, 'a', '', **atts))

    def depart_reference(self, node):
        self.body.append('</a>')
        if not isinstance(node.parent, nodes.TextElement):
            self.body.append('\n')
        self.in_mailto = False

    def visit_revision(self, node):
        self.visit_docinfo_item(node, 'revision', meta=False)

    def depart_revision(self, node):
        self.depart_docinfo_item()

    def visit_row(self, node):
        self.body.append(self.starttag(node, 'tr', ''))
        node.column = 0

    def depart_row(self, node):
        self.body.append('</tr>\n')

    def visit_rubric(self, node):
        self.body.append(self.starttag(node, 'p', '', CLASS='rubric'))

    def depart_rubric(self, node):
        self.body.append('</p>\n')

    def visit_section(self, node):
        self.section_level += 1
        self.body.append(
            self.starttag(node, 'section'))

    def depart_section(self, node):
        self.section_level -= 1
        self.body.append('</section>\n')

    def visit_sidebar(self, node):
        self.body.append(
            self.starttag(node, 'aside', CLASS='sidebar'))
        self.set_first_last(node)
        self.in_sidebar = True

    def depart_sidebar(self, node):
        self.body.append('</aside>\n')
        self.in_sidebar = False

    def visit_status(self, node):
        self.visit_docinfo_item(node, 'status', meta=False)

    def depart_status(self, node):
        self.depart_docinfo_item()

    def visit_strong(self, node):
        self.body.append(self.starttag(node, 'strong', ''))

    def depart_strong(self, node):
        self.body.append('</strong>')

    def visit_subscript(self, node):
        self.body.append(self.starttag(node, 'sub', ''))

    def depart_subscript(self, node):
        self.body.append('</sub>')

    def visit_substitution_definition(self, node):
        """Internal only."""
        raise nodes.SkipNode

    def visit_substitution_reference(self, node):
        self.unimplemented_visit(node)

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.sidebar):
            self.body.append(self.starttag(node, 'p', '',
                                           CLASS='sidebar-subtitle'))
            self.context.append('</p>\n')
        elif isinstance(node.parent, nodes.document):
            self.body.append(self.starttag(node, 'h2', '', CLASS='subtitle'))
            self.context.append('</h2>\n')
            self.in_document_title = len(self.body)
        elif isinstance(node.parent, nodes.section):
            tag = 'h%s' % (self.section_level + self.initial_header_level - 1)
            self.body.append(
                self.starttag(node, tag, '', CLASS='section-subtitle') +
                self.starttag({}, 'span', '', CLASS='section-subtitle'))
            self.context.append('</span></%s>\n' % tag)

    def depart_subtitle(self, node):
        self.body.append(self.context.pop())
        if self.in_document_title:
            self.subtitle = self.body[self.in_document_title:-1]
            self.in_document_title = 0
            self.body_pre_docinfo.extend(self.body)
            self.html_subtitle.extend(self.body)
            del self.body[:]

    def visit_superscript(self, node):
        self.body.append(self.starttag(node, 'sup', ''))

    def depart_superscript(self, node):
        self.body.append('</sup>')

    def visit_system_message(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='system-message'))
        self.body.append('<p class="system-message-title">')
        backref_text = ''
        if len(node['backrefs']):
            backrefs = node['backrefs']
            if len(backrefs) == 1:
                backref_text = ('; <em><a href="#%s">backlink</a></em>'
                                % backrefs[0])
            else:
                i = 1
                backlinks = []
                for backref in backrefs:
                    backlinks.append('<a href="#%s">%s</a>' % (backref, i))
                    i += 1
                backref_text = ('; <em>backlinks: %s</em>'
                                % ', '.join(backlinks))
        if node.hasattr('line'):
            line = ', line %s' % node['line']
        else:
            line = ''
        self.body.append('System Message: %s/%s '
                         '(<span class="literal">%s</span>%s)%s</p>\n'
                         % (node['type'], node['level'],
                            self.encode(node['source']), line, backref_text))

    def depart_system_message(self, node):
        self.body.append('</div>\n')

    def visit_table(self, node):
        self.context.append(self.compact_p)
        self.compact_p = True
        classes = ' '.join(['docutils', self.settings.table_style]).strip()
        self.body.append(
            self.starttag(node, 'table', CLASS=classes, border="1"))

    def depart_table(self, node):
        self.compact_p = self.context.pop()
        self.body.append('</table>\n')

    def visit_target(self, node):
        if not ('refuri' in node or 'refid' in node
                or 'refname' in node):
            self.body.append(self.starttag(node, 'span', '', CLASS='target'))
            self.context.append('</span>')
        else:
            self.context.append('')

    def depart_target(self, node):
        self.body.append(self.context.pop())

    def visit_tbody(self, node):
        self.write_colspecs()
        self.body.append(self.context.pop()) # '</colgroup>\n' or ''
        self.body.append(self.starttag(node, 'tbody', valign='top'))

    def depart_tbody(self, node):
        self.body.append('</tbody>\n')

    def visit_term(self, node):
        self.body.append(self.starttag(node, 'dt', ''))

    def depart_term(self, node):
        """
        Leave the end tag to `self.visit_definition()`, in case there's a
        classifier.
        """
        pass

    def visit_tgroup(self, node):
        # Mozilla needs <colgroup>:
        self.body.append(self.starttag(node, 'colgroup'))
        # Appended by thead or tbody:
        self.context.append('</colgroup>\n')
        node.stubs = []

    def depart_tgroup(self, node):
        pass

    def visit_thead(self, node):
        self.write_colspecs()
        self.body.append(self.context.pop()) # '</colgroup>\n'
        # There may or may not be a <thead>; this is for <tbody> to use:
        self.context.append('')
        self.body.append(self.starttag(node, 'thead', valign='bottom'))

    def depart_thead(self, node):
        self.body.append('</thead>\n')

    def visit_title(self, node):
        """Only 6 section levels are supported by HTML."""
        check_id = 0  # TODO: is this a bool (False) or a counter?
        close_tag = '</p>\n'
        if isinstance(node.parent, nodes.topic):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='topic-title first'))
        elif isinstance(node.parent, nodes.sidebar):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='sidebar-title'))
        elif isinstance(node.parent, nodes.Admonition):
            self.body.append(
                  self.starttag(node, 'p', '', CLASS='admonition-title'))
        elif isinstance(node.parent, nodes.table):
            self.body.append(
                  self.starttag(node, 'caption', ''))
            close_tag = '</caption>\n'
        elif isinstance(node.parent, nodes.document):
            self.body.append(self.starttag(node, 'h1', '', CLASS='title'))
            close_tag = '</h1>\n'
            self.in_document_title = len(self.body)
        else:
            assert isinstance(node.parent, nodes.section)
            h_level = self.section_level + self.initial_header_level - 1
            atts = {}
            if (len(node.parent) >= 2 and
                isinstance(node.parent[1], nodes.subtitle)):
                atts['CLASS'] = 'with-subtitle'
            self.body.append(
                  self.starttag(node, 'h%s' % h_level, '', **atts))
            atts = {}
            if node.hasattr('refid'):
                atts['class'] = 'toc-backref'
                atts['href'] = '#' + node['refid']
            if atts:
                self.body.append(self.starttag({}, 'a', '', **atts))
                close_tag = '</a></h%s>\n' % (h_level)
            else:
                close_tag = '</h%s>\n' % (h_level)
        self.context.append(close_tag)

    def depart_title(self, node):
        self.body.append(self.context.pop())
        if self.in_document_title:
            self.title = self.body[self.in_document_title:-1]
            self.in_document_title = 0
            self.body_pre_docinfo.extend(self.body)
            self.html_title.extend(self.body)
            del self.body[:]

    def visit_title_reference(self, node):
        self.body.append(self.starttag(node, 'cite', ''))

    def depart_title_reference(self, node):
        self.body.append('</cite>')

    def visit_topic(self, node):
        self.body.append(self.starttag(node, 'div', CLASS='topic'))
        self.topic_classes = node['classes']

    def depart_topic(self, node):
        self.body.append('</div>\n')
        self.topic_classes = []

    def visit_transition(self, node):
        self.body.append(self.emptytag(node, 'hr', CLASS='transition'))

    def depart_transition(self, node):
        pass

    def visit_version(self, node):
        self.visit_docinfo_item(node, 'version', meta=False)

    def depart_version(self, node):
        self.depart_docinfo_item()

    def unimplemented_visit(self, node):
        raise NotImplementedError('visiting unimplemented node type: %s'
                                  % node.__class__.__name__)

class HTML5Translator(BaseTranslator):
    """This class is a clone of sphinx.writers.html.HTMLTranslator,
       with similar modifications to those described above for
       BaseTranslator."""

    def __init__(self, builder, *args, **kwds):
        BaseTranslator.__init__(self, *args, **kwds)
        self.highlighter = builder.highlighter
        self.no_smarty = 0
        self.builder = builder
        self.highlightlang = builder.config.highlight_language
        self.highlightlinenothreshold = sys.maxsize
        self.protect_literal_text = 0
        self.permalink_text = builder.config.html_add_permalinks
        # support backwards-compatible setting to a bool
        # '\u00B6' is the paragraph symbol
        if not isinstance(self.permalink_text, str):
            self.permalink_text = self.permalink_text and '\u00B6' or ''
        self.permalink_text = self.encode(self.permalink_text)
        self.secnumber_suffix = builder.config.html_secnumber_suffix
        self.param_separator = ''
        self.first_param = 0
        self._table_row_index = 0

    def visit_start_of_file(self, node):
        # only occurs in the single-file builder
        self.body.append('<span id="document-%s"></span>' % node['docname'])
    def depart_start_of_file(self, node):
        pass

    # Make an effort not to emit a bunch of one-element <dl>s in a row.
    # A sequence of .. whatever:: directives in the RST will produce an
    # alternating sequence of index and desc nodes in the intermediate form.
    def same_desctype_as_sibling(self, node, direction):
        idx = node.parent.index(node)
        if direction == 'next':
            limit = len(node.parent)
            idx += 1
            while idx < limit:
                if not isinstance(node.parent[idx], addnodes.index):
                    sib = node.parent[idx]
                    break
                idx += 1
            else:
                return False

        elif direction == 'prev':
            limit = -1
            idx -= 1
            while idx > limit:
                if not isinstance(node.parent[idx], addnodes.index):
                    sib = node.parent[idx]
                    break
                idx -= 1
            else:
                return False

        else:
            raise RuntimeError("invalid 'direction' argument %s"
                               % repr(direction))

        if not isinstance(sib, type(node)):
            return False
        return sib['objtype'] == node['objtype']

    def visit_desc(self, node):
        if not self.same_desctype_as_sibling(node, 'prev'):
            self.body.append(self.starttag(node, 'dl', CLASS=node['objtype']))

    def depart_desc(self, node):
        if self.same_desctype_as_sibling(node, 'next'):
            self.body.append('\n\n')
        else:
            self.body.append('</dl>\n\n')

    def visit_desc_signature(self, node):
        # the id is set automatically
        self.body.append(self.starttag(node, 'dt', ''))
        # anchor for per-desc interactive data
        if node.parent['objtype'] != 'describe' \
               and node['ids'] and node['first']:
            self.body.append('<!--[%s]-->' % node['ids'][0])
    def depart_desc_signature(self, node):
        if node['ids'] and self.permalink_text and self.builder.add_permalinks:
            self.body.append('<a class="headerlink" href="#%s" '
                             % node['ids'][0] +
                             'title="%s">%s</a>' % (
                             _('Permalink to this definition'),
                             self.permalink_text))
        self.body.append('</dt>\n')

    def visit_desc_addname(self, node):
        self.body.append(self.starttag(node, 'span', '', CLASS='descclassname'))
    def depart_desc_addname(self, node):
        self.body.append('</span>')

    def visit_desc_type(self, node):
        pass
    def depart_desc_type(self, node):
        pass

    def visit_desc_returns(self, node):
        self.body.append(' &rarr; ')
    def depart_desc_returns(self, node):
        pass

    def visit_desc_name(self, node):
        self.body.append(self.starttag(node, 'span', '', CLASS='descname'))
    def depart_desc_name(self, node):
        self.body.append('</span>')

    def visit_desc_parameterlist(self, node):
        self.body.append('<span class="paramlistdelim">(</span>')
        self.first_param = 1
        self.param_separator = node.child_text_separator
    def depart_desc_parameterlist(self, node):
        self.body.append('<span class="paramlistdelim">)</span>')

    def visit_desc_parameter(self, node):
        if not self.first_param:
            self.body.append(self.param_separator)
        else:
            self.first_param = 0
        if not node.hasattr('noemph'):
            self.body.append('<em>')
    def depart_desc_parameter(self, node):
        if not node.hasattr('noemph'):
            self.body.append('</em>')

    def visit_desc_optional(self, node):
        self.body.append('<span class="optional">[</span>')
    def depart_desc_optional(self, node):
        self.body.append('<span class="optional">]</span>')

    def visit_desc_annotation(self, node):
        self.body.append(self.starttag(node, 'em', '', CLASS='property'))
    def depart_desc_annotation(self, node):
        self.body.append('</em>')

    def visit_desc_content(self, node):
        self.body.append(self.starttag(node, 'dd', ''))
    def depart_desc_content(self, node):
        self.body.append('</dd>')

    def visit_versionmodified(self, node):
        self.body.append(self.starttag(node, 'div', CLASS=node['type']))
    def depart_versionmodified(self, node):
        self.body.append('</div>\n')

    # overwritten
    def visit_reference(self, node):
        atts = {'class': 'reference'}
        if node.get('internal') or 'refuri' not in node:
            atts['class'] += ' internal'
        else:
            atts['class'] += ' external'
        if 'refuri' in node:
            atts['href'] = node['refuri']
            if self.settings.cloak_email_addresses and \
               atts['href'].startswith('mailto:'):
                atts['href'] = self.cloak_mailto(atts['href'])
                self.in_mailto = 1
        else:
            assert 'refid' in node, \
                   'References must have "refuri" or "refid" attribute.'
            atts['href'] = '#' + node['refid']
        if not isinstance(node.parent, nodes.TextElement):
            assert len(node) == 1 and isinstance(node[0], nodes.image)
            atts['class'] += ' image-reference'
        if 'reftitle' in node:
            atts['title'] = node['reftitle']
        self.body.append(self.starttag(node, 'a', '', **atts))

        if node.get('secnumber'):
            self.body.append(('%s' + self.secnumber_suffix) %
                             '.'.join(map(str, node['secnumber'])))

    # overwritten -- we don't want source comments to show up in the HTML
    def visit_comment(self, node):
        raise nodes.SkipNode

    # overwritten
    def visit_admonition(self, node, name=''):
        self.body.append(self.starttag(
            node, 'div', CLASS=('admonition ' + name)))
        if name:
            node.insert(0, nodes.title(name, admonitionlabels[name]))
        self.set_first_last(node)

    def visit_seealso(self, node):
        self.visit_admonition(node, 'seealso')
    def depart_seealso(self, node):
        self.depart_admonition(node)

    def add_secnumber(self, node):
        if node.get('secnumber'):
            self.body.append('.'.join(map(str, node['secnumber'])) +
                             self.secnumber_suffix)
        elif isinstance(node.parent, nodes.section):
            anchorname = '#' + node.parent['ids'][0]
            if anchorname not in self.builder.secnumbers:
                anchorname = ''  # try first heading which has no anchor
            if self.builder.secnumbers.get(anchorname):
                numbers = self.builder.secnumbers[anchorname]
                self.body.append('.'.join(map(str, numbers)) +
                                 self.secnumber_suffix)

    # overwritten
    def visit_title(self, node):
        BaseTranslator.visit_title(self, node)
        self.add_secnumber(node)

    # overwritten
    def visit_literal_block(self, node):
        if node.rawsource != node.astext():
            # most probably a parsed-literal block -- don't highlight
            return BaseTranslator.visit_literal_block(self, node)
        lang = self.highlightlang
        linenos = node.rawsource.count('\n') >= \
                  self.highlightlinenothreshold - 1
        highlight_args = node.get('highlight_args', {})
        if 'language' in node:
            # code-block directives
            lang = node['language']
            highlight_args['force'] = True
        if 'linenos' in node:
            linenos = node['linenos']
        def warner(msg):
            self.builder.warn(msg, (self.builder.current_docname, node.line))
        highlighted = self.highlighter.highlight_block(
            node.rawsource, lang, warn=warner, linenos=linenos,
            **highlight_args)
        starttag = self.starttag(node, 'div', suffix='',
                                 CLASS='highlight-%s' % lang)
        self.body.append(starttag + highlighted + '</div>\n')
        raise nodes.SkipNode

    def visit_doctest_block(self, node):
        self.visit_literal_block(node)

    # overwritten
    def visit_literal(self, node):
        # special-case roles that map directly to HTML5 inline tags:
        html5_known_roles = ('code', 'kbd', 'samp', 'var')
        classes = node.get('classes', [])
        for cls in classes:
            if cls in html5_known_roles:
                node['classes'] = [c for c in classes if c != cls]
                tag = cls
                break
        else:
            # default to <code> rather than <span class="literal"> for terseness
            tag = 'code'

        # If we are going to wrap <span class="pre"> around the entire contents
        # of this node, hoist the class to this node and emit its contents now.
        if len(node.children) == 1 and isinstance(node.children[0], nodes.Text):
            text = node.children[0].astext()
            tokens = list(self.words_and_spaces.findall(text))
            if len(tokens) == 1 and self.sollbruchstelle.search(tokens[0]):
                self.body.append(self.starttag(node, tag, '', CLASS="pre") +
                                 self.encode(tokens[0]) +
                                 '</%s>' % tag)
                raise nodes.SkipNode

        self.body.append(self.starttag(node, tag, ''))
        self.context.append('</%s>' % tag)
        self.protect_literal_text += 1

    def depart_literal(self, node):
        self.protect_literal_text -= 1
        self.body.append(self.context.pop())

    def visit_emphasis(self, node):
        if self.protect_literal_text: tag = 'var'
        else: tag = 'em'
        self.body.append(self.starttag(node, tag, ''))
        self.context.append('</%s>' % tag)

    def depart_emphasis(self, node):
        self.body.append(self.context.pop())

    def visit_productionlist(self, node):
        self.body.append(self.starttag(node, 'pre'))
        names = []
        for production in node:
            names.append(production['tokenname'])
        maxlen = max(len(name) for name in names)
        lastname = None
        for production in node:
            if production['tokenname']:
                lastname = production['tokenname'].ljust(maxlen)
                self.body.append(self.starttag(production, 'strong', ''))
                self.body.append(lastname + '</strong> ::= ')
            elif lastname is not None:
                self.body.append('%s     ' % (' '*len(lastname)))
            production.walkabout(self)
            self.body.append('\n')
        self.body.append('</pre>\n')
        raise nodes.SkipNode
    def depart_productionlist(self, node):
        pass

    def visit_production(self, node):
        pass
    def depart_production(self, node):
        pass

    def visit_centered(self, node):
        self.body.append(self.starttag(node, 'p', CLASS="centered")
                         + '<strong>')
    def depart_centered(self, node):
        self.body.append('</strong></p>')

    # overwritten
    def should_be_compact_paragraph(self, node):
        """Determine if the <p> tags around paragraph can be omitted."""
        if isinstance(node.parent, addnodes.desc_content):
            # Never compact desc_content items.
            return False
        if isinstance(node.parent, addnodes.versionmodified):
            # Never compact versionmodified nodes.
            return False
        return BaseTranslator.should_be_compact_paragraph(self, node)

    def visit_compact_paragraph(self, node):
        pass
    def depart_compact_paragraph(self, node):
        pass

    def visit_highlightlang(self, node):
        self.highlightlang = node['lang']
        self.highlightlinenothreshold = node['linenothreshold']
    def depart_highlightlang(self, node):
        pass

    def visit_download_reference(self, node):
        if node.hasattr('filename'):
            self.body.append(
                '<a class="reference download internal" href="%s">' %
                posixpath.join(self.builder.dlpath, node['filename']))
            self.context.append('</a>')
        else:
            self.context.append('')
    def depart_download_reference(self, node):
        self.body.append(self.context.pop())

    # overwritten
    def visit_image(self, node):
        olduri = node['uri']
        # rewrite the URI if the environment knows about it
        if olduri in self.builder.images:
            node['uri'] = posixpath.join(self.builder.imgpath,
                                         self.builder.images[olduri])

        if 'scale' in node:
            # Try to figure out image height and width.  Docutils does that too,
            # but it tries the final file name, which does not necessarily exist
            # yet at the time the HTML file is written.
            if PIL and not ('width' in node and 'height' in node):
                try:
                    im = PIL.Image.open(os.path.join(self.builder.srcdir,
                                                     olduri))
                except (IOError, # Source image can't be found or opened
                        UnicodeError):  # PIL doesn't like Unicode paths.
                    pass
                else:
                    if 'width' not in node:
                        node['width'] = str(im.size[0])
                    if 'height' not in node:
                        node['height'] = str(im.size[1])
                    del im
        BaseTranslator.visit_image(self, node)

    def visit_toctree(self, node):
        # this only happens when formatting a toc from env.tocs -- in this
        # case we don't want to include the subtree
        raise nodes.SkipNode

    def visit_index(self, node):
        raise nodes.SkipNode

    def visit_tabular_col_spec(self, node):
        raise nodes.SkipNode

    def visit_glossary(self, node):
        pass
    def depart_glossary(self, node):
        pass

    def visit_acks(self, node):
        pass
    def depart_acks(self, node):
        pass

    def visit_hlist(self, node):
        # The directive processor split up the list into a bunch of
        # 'hlistcol' nodes.  Undo this and produce a single <ul> with
        # appropriate class.  CSS will do the rest.
        ncols = len(node)
        self.body.append(self.starttag(node, 'ul',
                                       CLASS='hlist hlist-%d' % ncols))
        for col in node:
            assert isinstance(col, addnodes.hlistcol)
            assert len(col) == 1
            assert isinstance(col[0], nodes.bullet_list)
            for item in col[0]:
                item.walkabout(self)

        self.body.append('</ul>')
        # content already processed
        raise nodes.SkipNode

    def depart_hlist(self, node):
        raise RuntimeError('depart_hlist should never be called')

    def visit_hlistcol(self, node):
        raise RuntimeError('visit_hlistcol should never be called')

    def depart_hlistcol(self, node):
        raise RuntimeError('depart_hlistcol should never be called')

    def bulk_text_processor(self, text):
        return text

    # overwritten
    def visit_Text(self, node):
        text = node.astext()
        encoded = self.encode(text)
        if self.protect_literal_text:
            # moved here from base class's visit_literal to support
            # more formatting in literal nodes
            for token in self.words_and_spaces.findall(text):
                if token.strip():
                    # protect literal text from line wrapping
                    if self.sollbruchstelle.search(token):
                        self.body.append('<span class="pre">%s</span>'
                                         % self.encode(token))
                    else:
                        self.body.append(self.encode(token))
                elif token in (' ', '\n'):
                    # allow breaks at whitespace
                    self.body.append(token)
                elif '\n' in token:
                    token = token.split('\n')
                    for t in token: assert t == ' '*len(t)
                    crs = '\n' * (len(token)-1)
                    self.body.append(crs + '\u00a0'*len(token[-1]))
                else:
                    # protect runs of multiple spaces; the last one can wrap
                    self.body.append('\u00a0' * (len(token)-1) + ' ')
        else:
            encoded = self.encode(text)
            if self.in_mailto and self.settings.cloak_email_addresses:
                encoded = self.cloak_email(encoded)
            else:
                encoded = self.bulk_text_processor(encoded)
            self.body.append(encoded)

    def visit_note(self, node):
        self.visit_admonition(node, 'note')
    def depart_note(self, node):
        self.depart_admonition(node)

    def visit_warning(self, node):
        self.visit_admonition(node, 'warning')
    def depart_warning(self, node):
        self.depart_admonition(node)

    def visit_attention(self, node):
        self.visit_admonition(node, 'attention')

    def depart_attention(self, node):
        self.depart_admonition()

    def visit_caution(self, node):
        self.visit_admonition(node, 'caution')
    def depart_caution(self, node):
        self.depart_admonition()

    def visit_danger(self, node):
        self.visit_admonition(node, 'danger')
    def depart_danger(self, node):
        self.depart_admonition()

    def visit_error(self, node):
        self.visit_admonition(node, 'error')
    def depart_error(self, node):
        self.depart_admonition()

    def visit_hint(self, node):
        self.visit_admonition(node, 'hint')
    def depart_hint(self, node):
        self.depart_admonition()

    def visit_important(self, node):
        self.visit_admonition(node, 'important')
    def depart_important(self, node):
        self.depart_admonition()

    def visit_tip(self, node):
        self.visit_admonition(node, 'tip')
    def depart_tip(self, node):
        self.depart_admonition()

    # these are only handled specially in the SmartyPantsHTML5Translator
    def visit_literal_emphasis(self, node):
        return self.visit_emphasis(node)
    def depart_literal_emphasis(self, node):
        return self.depart_emphasis(node)

    def visit_abbreviation(self, node):
        attrs = {}
        if node.hasattr('explanation'):
            attrs['title'] = node['explanation']
        self.body.append(self.starttag(node, 'abbr', '', **attrs))
    def depart_abbreviation(self, node):
        self.body.append('</abbr>')

    def visit_termsep(self, node):
        self.body.append('<br>')
        raise nodes.SkipNode

    def depart_title(self, node):
        close_tag = self.context[-1]
        if (self.permalink_text and self.builder.add_permalinks and
            node.parent.hasattr('ids') and node.parent['ids']):
            aname = node.parent['ids'][0]
            # add permalink anchor
            if close_tag.startswith('</h'):
                self.body.append('<a class="headerlink" href="#%s" ' % aname +
                                 'title="%s">%s</a>' % (
                                 _('Permalink to this headline'),
                                 self.permalink_text))
            elif close_tag.startswith('</a></h'):
                self.body.append('</a><a class="headerlink" href="#%s" ' %
                                 aname +
                                 'title="%s">%s' % (
                                 _('Permalink to this headline'),
                                 self.permalink_text))

        BaseTranslator.depart_title(self, node)

    # overwritten to add even/odd classes

    def visit_table(self, node):
        self._table_row_index = 0
        return BaseTranslator.visit_table(self, node)

    def visit_row(self, node):
        self._table_row_index += 1
        if self._table_row_index % 2 == 0:
            node['classes'].append('row-even')
        else:
            node['classes'].append('row-odd')
        self.body.append(self.starttag(node, 'tr', ''))
        node.column = 0

    def visit_field_list(self, node):
        self._fieldlist_row_index = 0
        return BaseTranslator.visit_field_list(self, node)

    def visit_field(self, node):
        self._fieldlist_row_index += 1
        if self._fieldlist_row_index % 2 == 0:
            node['classes'].append('field-even')
        else:
            node['classes'].append('field-odd')
        self.body.append(self.starttag(node, 'tr', '', CLASS='field'))

    def unknown_visit(self, node):
        # An extension may have monkey-patched handlers for this node into
        # SphinxHTMLTranslator (via app.add_node).  Replicate on this class.
        nodename = node.__class__.__name__
        visitor_name = 'visit_' + nodename
        departor_name = 'depart_' + nodename
        visitor = getattr(SphinxHTMLTranslator, visitor_name, None)
        departor = getattr(SphinxHTMLTranslator, departor_name, None)
        if visitor is None:
            raise NotImplementedError('Unknown node: ' + nodename)

        setattr(self.__class__, visitor_name, visitor)
        if departor is not None:
            setattr(self.__class__, departor_name, departor)

        # Setting the attribute on self.__class__, then retrieving it
        # from self, has the magic side-effect of binding self for the
        # method call.
        return getattr(self, visitor_name)(node)

class SmartyPantsHTML5Translator(HTML5Translator):
    """
    Handle ordinary text via smartypants, converting quotes and dashes
    to the correct entities.
    """

    def __init__(self, *args, **kwds):
        self.no_smarty = 0
        HTML5Translator.__init__(self, *args, **kwds)

    def visit_literal(self, node):
        self.no_smarty += 1
        try:
            # this raises SkipNode
            HTML5Translator.visit_literal(self, node)
        finally:
            self.no_smarty -= 1

    def visit_literal_block(self, node):
        self.no_smarty += 1
        try:
            HTML5Translator.visit_literal_block(self, node)
        except nodes.SkipNode:
            # HTML5Translator raises SkipNode for simple literal blocks,
            # but not for parsed literal blocks
            self.no_smarty -= 1
            raise

    def depart_literal_block(self, node):
        HTML5Translator.depart_literal_block(self, node)
        self.no_smarty -= 1

    def visit_literal_emphasis(self, node):
        self.no_smarty += 1
        self.visit_emphasis(node)

    def depart_literal_emphasis(self, node):
        self.depart_emphasis(node)
        self.no_smarty -= 1

    def visit_desc_signature(self, node):
        self.no_smarty += 1
        HTML5Translator.visit_desc_signature(self, node)

    def depart_desc_signature(self, node):
        self.no_smarty -= 1
        HTML5Translator.depart_desc_signature(self, node)

    def visit_productionlist(self, node):
        self.no_smarty += 1
        try:
            HTML5Translator.visit_productionlist(self, node)
        finally:
            self.no_smarty -= 1

    def visit_option(self, node):
        self.no_smarty += 1
        HTML5Translator.visit_option(self, node)
    def depart_option(self, node):
        self.no_smarty -= 1
        HTML5Translator.depart_option(self, node)

    def bulk_text_processor(self, text):
        if self.no_smarty <= 0:
            return sphinx_smarty_pants(text)
        return text


def setup(app):
    # To enable HTML5 output, set html_translator_class to
    # html5_output.HTML5Translator or SmartyPantsHTML5Translator in
    # conf.py.
    pass
