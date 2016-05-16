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
    """ Base class for formatters that format the report as a GraphVix dot file. """

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
    """ Format the report as GraphViz dot file. This is used for generating a
        dependency graph. """

    def _nodes(self, report):
        """ Return the subgraphs representing the products in the report. """
        products_by_name = dict()
        for product in report.products():
            products_by_name.setdefault(product.name(), set()).add(product)
        subgraphs = []
        node_template = '"{label}" [label="{branch_version}" ' \
                        'style="filled" fillcolor="{color}" URL="{url}" ' \
                        'target="_top"]'
        subgraph_template = '  subgraph "cluster-{name}" {{\n    label="{name}"; ' \
                            'fillcolor="lightgrey"; style="filled"\n    {ns};' \
                            '\n  }};'
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


class MetricClassesFormatter(DotFormatter):
    """ Format the metrics and metric sources as a graph. """

    def prefix(self, report):
        return super(MetricClassesFormatter, self).prefix(report) + ' rankdir=LR; size="10,20!";'

    def _nodes(self, report):
        nodes = []
        project = report.project()
        nodes.extend(self.__metric_source_nodes(report, project))
        nodes.extend(self.__metric_nodes(report, project))
        return nodes

    def _edges(self, report):
        edges = []
        edge_template = '"{src}" -> "{metric}";'
        for metric_class in report.metric_classes():
            for metric_source_class in metric_class.metric_source_classes:
                edges.append(edge_template.format(src=metric_source_class.metric_source_name,
                                                  metric=metric_class.name))
        return edges

    def __metric_source_nodes(self, report, project):
        """ Return a list of metric source nodes. """
        nodes = []
        node_template = '"{name}" [style="filled" fillcolor="{color}"{url}];'
        for metric_source_class in self.__metric_source_classes(report):
            name = metric_source_class.metric_source_name
            metric_sources = project.metric_source(metric_source_class)
            metric_sources = metric_sources if isinstance(metric_sources, type([])) else [metric_sources]
            for metric_source in metric_sources:
                url = ' URL="{}" target="_top"'.format(metric_source.url()) if metric_source else ''
                color = self.__color(project, metric_source_class)
                nodes.append(node_template.format(name=name, color=color, url=url))
        return nodes

    def __metric_nodes(self, report, project):
        """ Return a list of metric class nodes. """
        nodes = []
        node_template = '"{name}" [style="filled" fillcolor="{color}"];'
        for metric_class in report.metric_classes():
            name = metric_class.name
            color = self.__color(project, *metric_class.metric_source_classes)
            nodes.append(node_template.format(name=name, color=color))
        return nodes

    @staticmethod
    def __metric_source_classes(report):
        """ Return a set of all metric source classes. """
        metric_source_classes = set()
        for metric_class in report.metric_classes():
            metric_source_classes.update(set(metric_class.metric_source_classes))
        return metric_source_classes

    @classmethod
    def __color(cls, project, *metric_source_classes):
        """ Return a color to represent whether all metric sources are available in the project. """
        return 'green' if cls.__available(project, *metric_source_classes) else 'red'

    @staticmethod
    def __available(project, *metric_source_classes):
        """ Return whether the project has all of the metric source classes. """
        for metric_source_class in metric_source_classes:
            if not project.metric_source(metric_source_class):
                return False
        return True
