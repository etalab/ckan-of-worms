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


<%inherit file="/site.mako"/>


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
        <%self:pagination/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
                    <th>${_(u"ID")}</th>
                    <th>${_(u"Name")}</th>
        % if data['sort'] == 'name':
                    <th>${_(u"Title")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
        % else:
                    <th><a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                            page = None, sort = 'name'))}">${_(u"Title")}</a></th>
        % endif
        % if data['sort'] == 'created':
                    <th>${_(u"Creation")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
        % else:
                    <th><a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                            page = None, sort = 'created'))}">${_(u"Creation")}</a></th>
        % endif
                </tr>
            </thead>
            <tbody>
        % for organization in organizations:
                <tr>
                    <td><a href="${organization.get_admin_url(ctx)}">${organization._id}</a></td>
                    <td>${organization.name or ''}</td>
                    <td>${organization.title or ''}</td>
                    <td>${organization.created or ''}</td>
                </tr>
        % endfor
            </tbody>
        </table>
        <%self:pagination/>
    % endif
</%def>


<%def name="pagination()" filter="trim">
    % if pager.page_count > 1:
            <div class="text-center">
                <ul class="pagination">
                    <li class="prev${' disabled' if pager.page_number <= 1 else ''}">
                        <a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = max(pager.page_number - 1, 1)))}">&larr;</a>
                    </li>
        % for page_number in range(max(pager.page_number - 5, 1), pager.page_number):
                    <li>
                        <a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = page_number))}">${page_number}</a>
                    </li>
        % endfor
                    <li class="active">
                        <a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = pager.page_number))}">${pager.page_number}</a>
                    </li>
        % for page_number in range(pager.page_number + 1, min(pager.page_number + 5, pager.last_page_number) + 1):
                    <li>
                        <a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = page_number))}">${page_number}</a>
                    </li>
        % endfor
                    <li class="next${' disabled' if pager.page_number >= pager.last_page_number else ''}">
                        <a href="${model.Organization.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = min(pager.page_number + 1, pager.last_page_number)))}">&rarr;</a>
                    </li>
                </ul>
            </div>
    % endif
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Organization.get_admin_class_url(ctx)}" method="get" role="form">
            <input name="sort" type="hidden" value="${inputs['sort'] or ''}">
<%
    error = errors.get('term') if errors is not None else None
%>\
            <div class="form-group${' error' if error else ''}">
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

