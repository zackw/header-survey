# -*- coding: utf-8 -*-

# Copyright 2014 Zack Weinberg <zackw@panix.com> and other contributors.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# There is NO WARRANTY.

# Report generation.

import configparser
import os.path
import textwrap
import pprint

from docutils import nodes
from docutils.statemachine import ViewList
from sphinx.util.compat import Directive
from sphinx.util.nodes import nested_parse_with_titles
from sphinx.ext.autodoc import AutodocReporter

class ReportFromConfig(Directive):
    """Generate some sort of report from a configuration file, and inject
       it at the current location.  Takes one argument, the name of the
       config file to read.  Subclasses must override generate_report()."""

    required_arguments = 1

    def run(self):
        self.state.document.settings.record_dependencies.add(__file__)

        src, srcline = self.state_machine.get_source_and_line()
        cfgfile = os.path.normpath(os.path.join(os.path.dirname(src),
                                                self.arguments[0]))
        self.state.document.settings.record_dependencies.add(cfgfile)

        parser = configparser.RawConfigParser()
        reporter = self.state.document.reporter
        try:
            parser.read_file(open(cfgfile, encoding="utf-8"))
            return self.generate_report(parser, reporter)

        except Exception as e:
            return [reporter.error(e, source=src, line=srcline)]

    def generate_report(self, parser, reporter):
        raise NotImplementedError

class KnownErrorsReport(ReportFromConfig):
    """Generate a report describing all known errors."""

    def generate_report(self, parser, reporter):
        result = []

        for tag in parser.sections():
            headers = parser.get(tag, "header", fallback="").split()
            desc = parser.get(tag, "desc", fallback="")

            if desc == "":
                result.append(reporter.warning("error '{}' has no description"
                                               .format(tag),
                                               source=errs_file))
                continue

            text = [".. describe:: " + tag,
                    ""]

            n = len(headers)
            if n == 0:
                text.append("   *May affect any header.*")
            elif n == 1:
                text.append("   *Known to affect* :file:`{}`."
                            .format(headers[0]))
            elif n == 2:
                text.append("   *Known to affect* :file:`{}` *and* :file:`{}`."
                            .format(headers[0], headers[1]))
            else:
                text.append("   *Known to affect* "
                            + ", ".join(":file:`"+f+"`" for f in headers[:-1])
                            + ", *and* :file:`"+headers[-1]+"`.")

            text.append("")

            for l in desc.split("\n"):
                l = l.strip()
                if l and l[0] == '|':
                    l = l[1:]
                if not l:
                    text.append(l)
                else:
                    text.append("   "+l)

            node = nodes.paragraph()
            self.state.nested_parse(ViewList(text), 0, node)
            result.extend(node.children)

        return result


class HeaderReport:
    required_arguments = 1
    def run(self):
        pass

def setup(app):
    app.add_directive("known-errors-report", KnownErrorsReport)
    app.add_directive("header-report", HeaderReport)
