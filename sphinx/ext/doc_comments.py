# -*- coding: utf-8 -*-

# Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# There is NO WARRANTY.

import os.path

from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.ext.autodoc import AutodocReporter
from sphinx.ext.todo import Todo

# This is what :file:`...` does internally, when there is no
# special-case markup in the `...`.  We don't want its special-case
# behavior, since we are processing a raw file name; also, we have no
# inliner with which to call role implementations.
def make_file_node(text):
    retnode = nodes.literal(role='file', classes=['file'])
    retnode.append(nodes.Text(text, text))
    return retnode

def synthetic_todo(text, lineno, state, state_machine):
    dv = Todo('todo', [], {}, ViewList([text], source="<synthetic>"),
              lineno, 0, text, state, state_machine)
    return dv.run()

class ExtractDocCommentDirective(Directive):
    """Extract a documentation comment from a file (specified as the
       single mandatory argument), and embed it in the current
       documentation tree.  It is assumed that the file uses #-comments
       (i.e. comment lines begin with # in column 1, and extend to the
       end of the line; no assumptions are made about # elsewhere in the
       line).  The documentation comment consists of all comment lines
       that begin with *two* # characters followed by one or more spaces;
       it is parsed as reStructuredText as usual.
       """

    required_arguments = 1

    def run(self):
        self.state.document.settings.record_dependencies.add(__file__)

        src, srcline = self.state_machine.get_source_and_line()
        doc_file = os.path.normpath(os.path.join(os.path.dirname(src),
                                                 self.arguments[0]))
        self.state.document.settings.record_dependencies.add(doc_file)
        doc_text  = ViewList()
        try:
            with open(doc_file, "r", encoding="utf-8") as f:
                last_lineno = 0
                for lineno, line in enumerate(f):
                    line = line.strip()
                    if line == "##":
                        line = ""
                    elif line.startswith("## "):
                        line = line[3:]
                    else:
                        continue

                    # Inject a blank line (i.e. paragraph separator) if we
                    # have advanced by more than one line since the last
                    # doc-comment line.
                    if last_lineno < lineno-1:
                        doc_text.append("", source=doc_file, offset=lineno-1)

                    doc_text.append(line, source=doc_file, offset=lineno)
                    last_lineno = lineno

        except EnvironmentError as e:
            raise self.error(e.filename + ": " + e.strerror) from e

        doc_section = nodes.section()
        doc_section.document = self.state.document

        # report line numbers within the nested parse correctly
        old_reporter = self.state.memo.reporter
        self.state.memo.reporter = AutodocReporter(doc_text,
                                                   self.state.memo.reporter)

        nested_parse_with_titles(self.state, doc_text, doc_section)
        self.state.memo.reporter = old_reporter

        if len(doc_section) == 1 and isinstance(doc_section[0], nodes.section):
            doc_section = doc_section[0]

        # Munge the title to end with ", :file:`(this file)`".
        # If there was no title, synthesize one from the name of the file.
        # If there was no doc comment at all, insert a todo.
        if len(doc_section) > 0 and isinstance(doc_section[0], nodes.title):
            doc_title = doc_section[0]
            doc_title.append(nodes.Text(", ", ", "))
        else:
            doc_title = nodes.title()
            doc_section.insert(0, doc_title)

        if len(doc_section) == 1:
            doc_section.extend(synthetic_todo("Undocumented",
                                              srcline,
                                              self.state,
                                              self.state_machine))

        base = os.path.basename(self.arguments[0])
        doc_title.append(make_file_node(base))
        doc_section['ids'].append(nodes.make_id("cf-" +
                                                os.path.splitext(base)[0]))
        return [doc_section]
        #return doc_section.children

def setup(app):
    app.add_directive('extract-doc-comment', ExtractDocCommentDirective)
