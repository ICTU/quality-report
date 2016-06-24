"""
Copyright 2012-2016 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
from __future__ import absolute_import


from . import base_formatter, html_formatter


class DotFormatter(base_formatter.Formatter):
    """ Base class for formatters that format the report as a GraphViz dot file. """

    sep = '\n'

    def prefix(self, report):
        """ Return the graph prefix. """
        return 'digraph { ranksep="2.5"; concentrate="true";'

    def body(self, report):
        """ Return the nodes and edges in dot format. """
        graph = []
        graph.extend(self._nodes(report))
        graph.extend(self._edges(report))
        return self.sep.join(graph)

    def _nodes(self, report):
        """ Override to return a list of graph nodes. """
        raise NotImplementedError  # pragma: no cover

    def _edges(self, report):
        """ Override to return a list of graph edges. """
        raise NotImplementedError  # pragma: no cover

    def metric(self, metric):
        """ Return a dot formatted version of the metric. """
        return ''  # pragma: no cover

    @staticmethod
    def postfix():
        """ Return the graph postfix. """
        return '}\n'


class DependencyFormatter(DotFormatter):
    """ Format the report as GraphViz dot file. This is used for generating a dependency graph. """

    def _nodes(self, report):
        """ Return the subgraphs representing the products in the report. """
        products_by_name = dict()
        for product in report.products():
            products_by_name.setdefault(product.name(), set()).add(product)
        subgraphs = []
        node_template = '"{label}" [label="{branch_version}" style="filled" fillcolor="{color}" URL="{url}" ' \
                        'target="_top"]'
        subgraph_template = '  subgraph "cluster-{name}" {{\n' \
                            '    label="{name}"; fillcolor="lightgrey"; style="filled"\n' \
                            '    {ns};\n' \
                            '  }};'
        for name, products in products_by_name.items():
            nodes = []
            for product in products:
                url = html_formatter.HTMLFormatter.product_url(product)
                color = report.get_product_section(product).color()
                nodes.append(node_template.format(label=product.product_label(),
                                                  branch_version=product.branch_version_label(),
                                                  color=color, url=url))
            node_string = ';\n    '.join(nodes)
            subgraphs.append(subgraph_template.format(name=name, ns=node_string))
        return subgraphs

    def _edges(self, report):
        """ Return the edges representing the dependencies between products in the report. """
        edges = []
        edge_template = '  "{prod}" -> "{dep}:{ver}";'
        for product in report.products():
            dependencies = product.dependencies(recursive=False)
            for dependency_name, dependency_version in dependencies:
                edges.append(edge_template.format(prod=product.product_label(), dep=dependency_name,
                                                  ver=dependency_version or 'trunk'))
        return edges
