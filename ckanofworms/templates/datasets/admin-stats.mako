## -*- coding: utf-8 -*-


## CKAN-of-Worms -- A logger for errors found in CKAN datasets
## By: Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2013 Etalab
## http://github.com/etalab/ckan-of-worms
##
## This file is part of CKAN-of-Worms.
##
## CKAN-of-Worms is free software; you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## CKAN-of-Worms is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


<%!
import urllib
import urlparse

from ckanofworms import conf, model, urls
%>


<%inherit file="/site.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Dataset.get_admin_class_url(ctx)}">${_(u"Datasets")}</a></li>
            <li><a href="${dataset.get_admin_url(ctx)}">${dataset.get_title(ctx)}</a></li>
            <li class="active">${_(u'Statistics')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${dataset.get_title(ctx)} - ${_(u"Statistics")}</h2>
        <%self:stats/>
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${dataset.get_admin_url(ctx)}">${_(u'View')}</a>
        </div>
</%def>


<%def name="stats()" filter="trim">
    % if conf['piwik.site_id'] is not None and conf['piwik.url'] is not None:
        <div>
            <iframe width="100%" height="350" src="${
                    urlparse.urljoin(conf['piwik.url'], u'index.php?{}'.format(
                        urllib.urlencode((
                            ('action', 'iframe'),
                            ('actionToWidgetize', 'getEvolutionGraph'),
                            ('columns[]', 'nb_visits'),
                            ('date', 'today'),
                            ('disableLink', '1'),
                            ('idSite', str(conf['piwik.site_id'])),
                            ('module', 'Widgetize'),
                            ('moduleToWidgetize', 'VisitsSummary'),
                            ('period', 'day'),
                            ('segment', ','.join(
                                'pageUrl=={}'.format(page_url)
                                for page_url in (
                                    urlparse.urljoin(conf['ckan_url'], 'dataset/{}'.format(dataset.name)),
                                    urlparse.urljoin(conf['weckan_url'], 'fr/dataset/{}'.format(dataset.name)),
                                    )
                                )),
                            ('widget', '1'),
                            )),
                        )).replace('%2C', ',').replace('%3D%3D', '==').replace('%5B', '[').replace('%5D', ']')
                    }" scrolling="no" frameborder="0" marginheight="0" marginwidth="0">
            </iframe>
        </div>
    % endif
</%def>


<%def name="title_content()" filter="trim">
${_(u"Statistics")} - ${dataset.get_title(ctx)} - ${parent.title_content()}
</%def>
