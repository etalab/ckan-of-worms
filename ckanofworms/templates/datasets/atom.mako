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
from ckanofworms import conf, model, texthelpers, urls
%>


<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
    <title>${conf['realm']}</title>
    <id>${urls.get_full_url(ctx, 'api', '1', 'datasets', **urls.relative_query(inputs))}</id>
    <link href="${model.Dataset.get_admin_class_full_url(ctx) if data['target'] is None \
            else model.Dataset.get_class_back_url(ctx) if data['target'] == 'back' \
            else model.Dataset.get_class_front_url(ctx)}"/>
    <link href="${urls.get_full_url(ctx, 'api', '1', 'datasets', **urls.relative_query(inputs))}" rel="self"/>
##    <author>
##        <name>${_('CKAN-of-Worms contributors')}</name>
##        <email>${conf['wenoit.email']}</email>
##        <uri>${conf['wenoit.url']}</uri>
##    </author>
##    % for tag in (tags or []):
##          <category term="${tag}"/>
##    % endfor
    <generator uri="http://github.com/etalab/ckan-of-worms">CKAN-of-Worms</generator>
    <rights>
        This feed is licensed under the Open Licence ${'<http://www.data.gouv.fr/Licence-Ouverte-Open-Licence>'}.
    </rights>
<%
    datasets = list(cursor)
    timestamp = max(
        dataset.timestamp
        for dataset in datasets
        )
%>\
    <updated>${timestamp.replace(u' ', u'Z')}</updated>
    % for dataset in datasets:
    <entry>
        <title>${dataset.title}</title>
        <id>${dataset.get_admin_full_url(ctx)}</id>
        <link href="${dataset.get_admin_full_url(ctx) if data['target'] is None \
                else dataset.get_back_url(ctx) if data['target'] == 'back' \
                else dataset.get_front_url(ctx)}"/>
<%
        organization = dataset.get_organization(ctx)
%>\
        % if organization is not None:
        <author>
            <name>${organization.title}</name>
            <uri>${organization.get_admin_full_url(ctx) if data['target'] is None \
                    else organization.get_back_url(ctx) if data['target'] == 'back' \
                    else organization.get_front_url(ctx)}</uri>
        </author>
        % endif
        % for tag in (dataset.tags or []):
        <category term="${tag['name']}"/>
        % endfor
        <updated>${dataset.timestamp.replace(u' ', u'Z')}</updated>
        % if dataset.notes:
        <summary type="html">
            ${texthelpers.htmlify_markdown(dataset.notes)}
        </summary>
        % endif
    </entry>
    % endfor
</feed>
