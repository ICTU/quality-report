'''
Copyright 2012-2014 Ministerie van Sociale Zaken en Werkgelegenheid

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

from qualitylib.formatting import base_formatter, html_formatter


class DotFormatter(base_formatter.Formatter):
    ''' Format the report as GraphViz dot file. This is used for generating a
        dependency graph. '''

    sep = '\n'

    def prefix(self, report):
        ''' Return the graph prefix. '''
        return 'digraph { ranksep="2.5"; concentrate="true";'

    def body(self, report):
        ''' Return the dependencies between the products in the project in dot
            format. '''
        graph = []
        graph.extend(self.__product_subgraphs(report))
        graph.extend(self.__product_edges(report))
        return self.sep.join(graph)

    def metric(self, metric):
        ''' Return a dot formatted version of the metric. '''
        return ''  # pragma: no cover

    @staticmethod
    def postfix():
        ''' Return the graph postfix. '''
        return '}\n'

    @staticmethod
    def __product_subgraphs(report):
        ''' Return the subgraphs representing the products in the report. '''
        products_by_name = dict()
        for product in report.products():
            products_by_name.setdefault(product.name(), set()).add(product)
        subgraphs = []
        node_template = '"%(label)s" [label="%(branch_version)s" ' \
                        'style="filled" fillcolor="%(color)s" URL="%(url)s" ' \
                        'target="_top"]'
        subgraph_template = '  subgraph "cluster-%s" {\n    label="%s"; ' \
                            'fillcolor="lightgrey"; style="filled"\n    %s;' \
                            '\n  };'
        for name, products in products_by_name.items():
            nodes = []
            for product in products:
                url = html_formatter.HTMLFormatter.product_url(product)
                color = report.get_product_section(product).color()
                parameters = dict(label=product.product_label(), 
                                  branch_version=product.branch_version_label(),
                                  color=color, url=url)
                nodes.append(node_template % parameters)
            node_string = ';\n    '.join(nodes)
            subgraphs.append(subgraph_template % (name, name, node_string))
        return subgraphs

    @staticmethod
    def __product_edges(report):
        ''' Return the edges representing the dependencies between products in
            the report. '''
        edges = []
        for product in report.products():
            dependencies = product.dependencies(recursive=False)
            for dependency_name, dependency_version in dependencies:
                edges.append('  "%s" -> "%s:%s";' % (product.product_label(),
                             dependency_name, dependency_version or 'trunk'))
        return edges
