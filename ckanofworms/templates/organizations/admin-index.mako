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
from ckanofworms import model, urls
%>


<%inherit file="/object-admin-index.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li class="active">${_(u'Organizations')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <%self:search_form/>
    % if pager.item_count == 0:
        <h2>${_(u"No organization found")}</h2>
    % else:
        % if pager.page_count > 1:
            % if pager.page_size == 1:
        <h2>${_(u"Organization {0} of {1}").format(pager.first_item_number, pager.item_count)}</h2>
            % else:
        <h2>${_(u"Organizations {0} - {1} of {2}").format(pager.first_item_number, pager.last_item_number, pager.item_count)}</h2>
            % endif
        % elif pager.item_count == 1:
        <h2>${_(u"Single organization")}</h2>
        % else:
        <h2>${_(u"{} organizations").format(pager.item_count)}</h2>
        % endif
        <%self:pagination object_class="${model.Organization}" pager="${pager}"/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
        % if data['sort'] == 'name':
                    <th>${_(u"Title")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
        % else:
                    <th><a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                            page = None, sort = 'name'))}">${_(u"Title")}</a></th>
        % endif
                    <th>${_(u"Produced Datasets")}</th>
                    <th>${_(u"Supplied Datasets")}</th>
                    <th>${_(u"Datasets")}</th>
        % if data['sort'] == 'created':
                    <th>${_(u"Creation")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
        % else:
                    <th><a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                            page = None, sort = 'created'))}">${_(u"Creation")}</a></th>
        % endif
                    <th>${_(u"Logo")}</th>
                </tr>
            </thead>
            <tbody>
        % for organization in organizations:
                <tr>
                    <td><a href="${organization.get_admin_url(ctx)}">${organization.title or ''}</a></td>
                    <td>${model.Dataset.find({'owner_org': organization._id}).count() or u''}</td>
                    <td>${model.Dataset.find({'supplier_id': organization._id}).count() or u''}</td>
                    <td>${organization.created or ''}</td>
                    <td>
            % if organization.image_url is not None:
                        <img class="img-responsive" style="max-width: 100px" src="${organization.image_url}">
            % endif
                    </td>
                </tr>
        % endfor
            </tbody>
        </table>
        <%self:pagination object_class="${model.Organization}" pager="${pager}"/>
    % endif
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Organization.get_admin_class_url(ctx)}" method="get" role="form">
            <input name="sort" type="hidden" value="${inputs['sort'] or ''}">
<%
    error = errors.get('term') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="term">${_("Term")}</label>
                <input class="form-control" id="term" name="term" type="text" value="${inputs['term'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
            <button class="btn btn-primary" type="submit"><span class="glyphicon glyphicon-search"></span> ${_('Search')}</button>
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_('Organizations')} - ${parent.title_content()}
</%def>

