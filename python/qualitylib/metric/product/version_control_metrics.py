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

from qualitylib.domain import LowerIsBetterMetric
from qualitylib.metric.metric_source_mixin import SubversionMetricMixin
from qualitylib.metric.quality_attributes import CODE_QUALITY


class UnmergedBranches(SubversionMetricMixin, LowerIsBetterMetric):
    # pylint: disable=too-many-public-methods
    ''' Metric for measuring the number of unmerged branches. '''

    name = 'Ongemergde branches'
    norm_template = 'Geen branches die ongemergde code hebben.'
    perfect_template = 'Geen van de %(nr_branches)d branches van %(name)s ' \
        'heeft revisies die niet met de trunk zijn gemerged.'
    template = '%(value)d van de %(nr_branches)d branches van %(name)s ' \
        'hebben revisies die niet met de trunk zijn gemerged.'
    quality_attribute = CODE_QUALITY
    target_value = 0
    low_target_value = 1

    @classmethod
    def can_be_measured(cls, product, project):
        ''' Unmerged branches can only be measured for trunk versions of 
            products that are under version control. '''
        return super(UnmergedBranches, cls).can_be_measured(product, project) \
            and product.svn_path() and not product.product_version()

    def value(self):
        return len(self.__unmerged_branches())

    def url(self):
        return self.__branch_and_nr_revs_urls(self.__unmerged_branches())

    def url_label(self):
        return 'Niet gemergde branches'

    @staticmethod
    def comment_url_label():
        return 'Genegeerde branches'

    def comment_urls(self):
        return self.__branch_urls(self.__branches_to_ignore())

    def _get_template(self):
        # pylint: disable=protected-access
        return self.perfect_template if self._is_perfect() else \
            super(UnmergedBranches, self)._get_template()

    def _parameters(self):
        # pylint: disable=protected-access
        parameters = super(UnmergedBranches, self)._parameters()
        parameters['nr_branches'] = len(self.__branches())
        return parameters

    def __branch_and_nr_revs_urls(self, branches_and_revisions):
        ''' Return a list of branch urls. '''
        urls = dict()
        svn_path_base, svn_path_postfix = self.__svn_path().split('/trunk/')
        for branch, nr_revisions in branches_and_revisions.items():
            label = '%s: %d ongemergde revisie(s)' % (branch, nr_revisions) 
            urls[label] = svn_path_base + '/branches/' + branch + '/' + \
                          svn_path_postfix
        return urls

    def __branch_urls(self, branches):
        ''' Return a list of branch urls. '''
        urls = dict()
        svn_path_base, svn_path_postfix = self.__svn_path().split('/trunk/')
        for branch in branches:
            urls[branch] = svn_path_base + '/branches/' + branch + '/' + \
                           svn_path_postfix
        return urls

    def __branches(self):
        ''' Return a list of branches for the product. '''
        return self._subversion.branches(self.__svn_path())

    def __unmerged_branches(self):
        ''' Return a dictionary of unmerged branch names and the number of 
            unmerged revisions for each branch. '''
        unmerged_branches = \
            self._subversion.unmerged_branches(self.__svn_path())
        branches_to_ignore = self.__branches_to_ignore()
        for branch in unmerged_branches.copy():
            if branch in branches_to_ignore:
                del unmerged_branches[branch]
        return unmerged_branches

    def __svn_path(self):
        ''' Return the Subversion path for the product. '''
        svn_path = self._subject.svn_path()
        # This metric only makes sense for trunk versions:
        assert '/trunk/' in svn_path
        return svn_path

    def __branches_to_ignore(self):
        ''' Return the branches to ignore for the measured product. '''
        metric_options = self._subject.metric_options(self.__class__)
        if metric_options:
            return metric_options.get('branches_to_ignore', [])
        else:
            return []
