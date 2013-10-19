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
import math

from ckanofworms import conf, model


changefreq_by_frequency = {
    u"annuelle": u'yearly',
    u"aucune": u'never',
    u"bimensuelle": u'weekly',
    u"bimestrielle": u'monthly',
    u"hebdomadaire": u'weekly',
    u"mensuelle": u'monthly',
    u"ponctuelle": None,
    u"quinquennale": u'yearly',
    u"quotidienne": u'daily',
    u"semestrielle": u'monthly',
    u"temps réel": None,
    u"triennale": u'yearly',
    u"trimestrielle": u'monthly',
    }
weights_by_group_id = {}
weights_by_organization_id = {}
%>


<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>${conf['weckan_url'] | n, x}</loc>
        <priority>1.0</priority>
    </url>
    % for dataset in model.Dataset.find(None, ['frequency', 'groups.id', 'name', 'owner_org', 'timestamp', 'weight']):
    <url>
        <loc>${dataset.get_front_url(ctx) | n, x}</loc>
        % if dataset.timestamp is not None:
        <lastmod>${dataset.timestamp.replace(u' ', u'T') | n, x}</lastmod>
        % endif
<%
        changefreq = changefreq_by_frequency.get(dataset.frequency)
%>\
        % if changefreq is not None:
        <changefreq>${changefreq | n, x}</changefreq>
        % endif
<%
        weight = dataset.weight
%>\
        % if weight is not None:
<%
            priority = math.atan(weight) * 2 / math.pi
            for group in (dataset.groups or []):
                weights_by_group_id.setdefault(group['id'], []).append(weight)
            if dataset.owner_org is not None:
                weights_by_organization_id.setdefault(dataset.owner_org, []).append(weight)
%>\
        <priority>${unicode(priority) | n, x}</priority>
        % endif
    </url>
    % endfor
    % for group in model.Group.find(None, ['created', 'name']):
    <url>
        <loc>${group.get_front_url(ctx) | n, x}</loc>
        % if group.created is not None:
        <lastmod>${group.created | n, x}</lastmod>
        % endif
<%
        weights = weights_by_group_id.get(group._id)
        priority = math.atan(sum(weights)) * 2 / math.pi if weights is not None else 0.0
%>\
        <priority>${unicode(priority) | n, x}</priority>
    </url>
    % endfor
    % for organization in model.Organization.find(None, ['created', 'name']):
    <url>
        <loc>${organization.get_front_url(ctx) | n, x}</loc>
        % if organization.created is not None:
        <lastmod>${organization.created | n, x}</lastmod>
        % endif
<%
        weights = weights_by_organization_id.get(organization._id)
        priority = math.atan(sum(weights)) * 2 / math.pi if weights is not None else 0.0
%>\
        <priority>${unicode(priority) | n, x}</priority>
    </url>
    % endfor
</urlset>
