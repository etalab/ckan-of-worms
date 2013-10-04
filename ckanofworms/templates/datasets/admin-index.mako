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
            <li class="active">${_(u'Datasets')}</li>
</%def>


<%def name="container_content()" filter="trim">
        <%self:search_form/>
    % if pager.item_count == 0:
        <h2>${_(u"No dataset found")}</h2>
    % else:
        % if pager.page_count > 1:
            % if pager.page_size == 1:
        <h2>${_(u"Dataset {0} of {1}").format(pager.first_item_number, pager.item_count)}</h2>
            % else:
        <h2>${_(u"Datasets {0} - {1} of {2}").format(pager.first_item_number, pager.last_item_number, pager.item_count)}</h2>
            % endif
        % elif pager.item_count == 1:
        <h2>${_(u"Single dataset")}</h2>
        % else:
        <h2>${_(u"{} datasets").format(pager.item_count)}</h2>
        % endif
        <%self:pagination/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
            % if data['sort'] == 'name':
                    <th>${_(u"Title")} <span class="glyphicon glyphicon-sort-by-attributes"></span></th>
            % else:
                    <th><a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'name'))}">${_(u"Title")}</a></th>
            % endif
            % if data['sort'] == 'timestamp':
                    <th>${_(u"Last Modification")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
            % else:
                    <th><a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'timestamp'))}">${_(u"Last Modification")}</a></th>
            % endif
            % if data['sort'] == 'metadata_created':
                    <th>${_(u"Creation")} <span class="glyphicon glyphicon-sort-by-attributes-alt"></span></th>
            % else:
                    <th><a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs, page = None,
                            sort = 'metadata_created'))}">${_(u"Creation")}</a></th>
            % endif
                </tr>
            </thead>
            <tbody>
        % for dataset in datasets:
                <tr>
                    <td><a href="${dataset.get_admin_url(ctx)}">${dataset.title}</a></td>
                    <td>${dataset.timestamp or ''}</td>
                    <td>${dataset.metadata_created or ''}</td>
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
                        <a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = max(pager.page_number - 1, 1)))}">&larr;</a>
                    </li>
        % for page_number in range(max(pager.page_number - 5, 1), pager.page_number):
                    <li>
                        <a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = page_number))}">${page_number}</a>
                    </li>
        % endfor
                    <li class="active">
                        <a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = pager.page_number))}">${pager.page_number}</a>
                    </li>
        % for page_number in range(pager.page_number + 1, min(pager.page_number + 5, pager.last_page_number) + 1):
                    <li>
                        <a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = page_number))}">${page_number}</a>
                    </li>
        % endfor
                    <li class="next${' disabled' if pager.page_number >= pager.last_page_number else ''}">
                        <a href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs,
                                page = min(pager.page_number + 1, pager.last_page_number)))}">&rarr;</a>
                    </li>
                </ul>
            </div>
    % endif
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Dataset.get_admin_class_url(ctx)}" method="get" role="form">
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
<%
    error = errors.get('tag') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="tag">${_("Tag")}</label>
                <input class="form-control typeahead" id="tag" name="tag" type="text" value="${inputs['tag'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
<%
    error = errors.get('group') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="group">${_("Group")}</label>
                <input class="form-control typeahead" id="group" name="group" type="text" value="${
                        inputs['group'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
<%
    error = errors.get('organization') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="organization">${_("Organization")}</label>
                <input class="form-control typeahead" id="organization" name="organization" type="text" value="${
                        inputs['organization'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
<%
    error = errors.get('supplier') if errors is not None else None
%>\
            <div class="form-group${' has-error' if error else ''}">
                <label for="supplier">${_("Supplier")}</label>
                <input class="form-control typeahead" id="supplier" name="supplier" type="text" value="${
                        inputs['supplier'] or ''}">
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
<%
    error = errors.get('related') if errors is not None else None
%>\
            <div class="checkbox${' has-error' if error else ''}">
                <label>
                    <input${' checked' if inputs['related'] else ''} id="related" name="related" type="checkbox" value="1">
                    ${_(u'Related only')}
                </label>
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
<%
    error = errors.get('bad') if errors is not None else None
%>\
            <div class="checkbox${' has-error' if error else ''}">
                <label>
                    <input${' checked' if inputs['bad'] else ''} id="bad" name="bad" type="checkbox" value="1">
                    ${_(u'Errors only')}
                </label>
    % if error:
                <span class="help-block">${error}</span>
    % endif
            </div>
            <button class="btn btn-primary" type="submit"><span class="glyphicon glyphicon-search"></span> ${_('Search')}</button>
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_('Datasets')} - ${parent.title_content()}
</%def>

