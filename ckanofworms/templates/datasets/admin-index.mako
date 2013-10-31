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
from ckanofworms import model, texthelpers, urls


alert_levels = ['critical', 'error', 'warning', 'info', 'debug']
label_class_by_alert_level = dict(
    critical = 'label-danger',
    debug = 'label-info',
    error = 'label-danger',
    info = 'label-info',
    warning = 'label-warning',
    )
N_ = lambda message: message
title_by_alert_level = dict(
    critical = N_(u"Critical"),
    debug = N_(u"Debug"),
    error = N_(u"Error"),
    info = N_(u"Info"),
    warning = N_(u"Warning"),
    )
%>


<%inherit file="/object-admin-index.mako"/>


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
        <%self:pagination object_class="${model.Dataset}" pager="${pager}"/>
        <table class="table table-bordered table-condensed table-striped">
            <thead>
                <tr>
                    <th>${_(u"Organization")}</th>
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
                    <th>${_(u"Alerts")}</th>
                </tr>
            </thead>
            <tbody>
        % for dataset in datasets:
                <tr>
                    <td>
<%
            organization = dataset.get_organization(ctx)
%>\
            % if organization is None:
                        <img alt="" src="${urls.get_url(ctx, 'images', 'placeholder-organization.png')
                                }" class="img-responsive" width="80">
            % else:
                        <img alt="${organization.title}" src="${organization.image_url \
                                or urls.get_url(ctx, 'images', 'placeholder-organization.png')
                                }" class="img-responsive" width="80">
            % endif
                    </td>
                    <td>
                        <h4><a href="${dataset.get_admin_url(ctx)}">${dataset.title}</a></h4>
<%
            notes_text = texthelpers.textify_markdown(dataset.notes)
%>\
            % if notes_text:
                        ${texthelpers.truncate(notes_text, length = 180, whole_word = True)}
            % endif
            % if dataset.frequency is not None or dataset.temporal_coverage_from is not None \
                    or dataset.temporal_coverage_to is not None or dataset.territorial_coverage is not None \
                    or dataset.territorial_coverage_granularity is not None or dataset.weight is not None:
                        <ul class="list-inline">
                % if dataset.weight is not None:
                            <li>
                                <a href class="btn btn-default btn-xs" data-placement="left" data-toggle="tooltip" title="${
                                        _(u"Search ranking")}">
                    % if dataset.weight < 3:
                                    <span class="glyphicon glyphicon-star text-danger"></span>
                    % else:
                                    <span class="glyphicon glyphicon-star"></span>
                    % endif
                                </a>
                                <span class="badge">${_(u'{:3.2f}').format(dataset.weight)}</span>
                            </li>
                % endif
                % if dataset.temporal_coverage_from is not None or dataset.temporal_coverage_to is not None:
                            <li>
                                <a href class="btn btn-default btn-xs" data-placement="left" data-toggle="tooltip" title="${
                                        _(u"Temporal coverage")}">
                                    <span class="glyphicon glyphicon-calendar"></span>
                                </a>
                                ${_(u"{0} to {1}").format(dataset.temporal_coverage_from or _(u"…"),
                                    dataset.temporal_coverage_to or _(u"…"))}
                            </li>
                % endif
                % if dataset.frequency is not None:
                            <li>
                                <a href class="btn btn-default btn-xs" data-placement="left" data-toggle="tooltip" title="${
                                        _(u"Update frequency")}">
                                    <span class="glyphicon glyphicon-time"></span>
                                </a>
                                ${dataset.frequency}
                            </li>
                % endif
                % if dataset.territorial_coverage is not None:
                            <li>
                                <a href class="btn btn-default btn-xs" data-placement="left" data-toggle="tooltip" title="${
                                        _(u"Territorial coverage")}">
                                    <span class="glyphicon glyphicon-globe"></span>
                                </a>
                                ${dataset.territorial_coverage}
                            </li>
                % endif
                % if dataset.territorial_coverage_granularity is not None:
                            <li>
                                <a href class="btn btn-default btn-xs" data-placement="left" data-toggle="tooltip" title="${
                                        _(u"Territorial coverage granularity")}">
                                    <span class="glyphicon glyphicon-screenshot"></span>
                                </a>
                                ${dataset.territorial_coverage_granularity}
                            </li>
                % endif
                        </ul>
            % endif
                    </td>
                    <td>${dataset.timestamp or ''}</td>
                    <td>${dataset.metadata_created or ''}</td>
                    <td>
<%
            alerts_ranking = dict(
                (level, sum(
                    len(author_alerts['error'])
                    for author_alerts in level_alerts.itervalues()
                    ))
                for level, level_alerts in (dataset.alerts or {}).iteritems()
                )
%>\
            % if alerts_ranking:
                <ul class="list-unstyled">
                % for level in alert_levels:
<%
                    count = alerts_ranking.get(level)
                    if count is None:
                        continue
%>\
                    <li>
                        <a href="${dataset.get_admin_url(ctx)}"><span class="label ${label_class_by_alert_level[level]
                                }">${_(u"{}: {}").format(title_by_alert_level[level], count)}\
                    % if level == 'critical':
 <span class="glyphicon glyphicon-warning-sign"></span>\
                    % endif
</span></a>
                    </li>
                % endfor
                </ul>
            % endif
                    </td>
                </tr>
        % endfor
            </tbody>
        </table>
        <%self:pagination object_class="${model.Dataset}" pager="${pager}"/>
    % endif
</%def>


<%def name="search_form()" filter="trim">
        <form action="${model.Dataset.get_admin_class_url(ctx)}" method="get" role="form">
    % if data['advanced_search']:
            <input name="advanced_search" type="hidden" value="1">
    % endif
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
    input_value = inputs['tag']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="tag">${_("Tag")}</label>
                <input class="form-control typeahead" id="tag" name="tag" type="text" value="${input_value or ''}">
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
<%
    error = errors.get('group') if errors is not None else None
    input_value = inputs['group']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="group">${_("Group")}</label>
                <input class="form-control typeahead" id="group" name="group" placeholder="${
                        _(u"Enter a group name...")}" type="text" value="${input_value or ''}">
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
<%
    error = errors.get('organization') if errors is not None else None
    input_value = inputs['organization']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="organization">${_("Organization")}</label>
                <input class="form-control typeahead" id="organization" name="organization" placeholder="${
                        _(u"Enter an organization name...")}" type="text" value="${input_value or ''}">
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
<%
    error = errors.get('supplier') if errors is not None else None
    input_value = inputs['supplier']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="supplier">${_("Supplier")}</label>
                <input class="form-control typeahead" id="supplier" name="supplier"placeholder="${
                        _(u"Enter an organization name...")}"  type="text" value="${input_value or ''}">
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
<%
    error = errors.get('related_owner') if errors is not None else None
    input_value = inputs['related_owner']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="related_owner">${_("Related Owner")}</label>
                <input class="form-control typeahead" id="related_owner" name="related_owner" placeholder="${
                        _(u"Enter an account name...")}" type="text" value="${input_value or ''}">
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
<%
    error = errors.get('alerts') if errors is not None else None
    input_value = inputs['alerts']
    options = [
        ('debug', _(u"All")),
        ('info', _(u"Info or above")),
        ('warning', _(u"Warning or above")),
        ('error', _(u"Error or above")),
        ('critical', _(u"Critical")),
        ]
    value = data['alerts']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="form-group${' has-error' if error else ''}">
                <label for="alerts">${_("Alert Level")}</label>
                <select class="form-control" id="alerts" name="alerts">
                    <option value=""></option>
        % for option_value, option_title in options:
                    <option${' selected' if option_value == value else ''} value="${option_value}">${option_title
                        }</option>
        % endfor
                </select>
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
<%
    error = errors.get('related') if errors is not None else None
    input_value = inputs['related']
%>\
    % if data['advanced_search'] or error or input_value:
            <div class="checkbox${' has-error' if error else ''}">
                <label>
                    <input${' checked' if input_value else ''} id="related" name="related" type="checkbox" value="1">
                    ${_(u'Related only')}
                </label>
        % if error:
                <span class="help-block">${error}</span>
        % endif
            </div>
    % endif
            <button class="btn btn-primary" type="submit"><span class="glyphicon glyphicon-search"></span> ${
                _('Search')}</button>
            <a href="${urls.get_url(ctx, 'api', '1', 'datasets', **urls.relative_query(inputs,
                    advanced_search = None, format = 'atom', page = None, sort = None))}">${_('News Feed')}</a>
    % if data['advanced_search']:
            <a class="pull-right" href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = None))}">${_('Simplified Search')}</a>
    % else:
            <a class="pull-right" href="${model.Dataset.get_admin_class_url(ctx, **urls.relative_query(inputs,
                    advanced_search = 1))}">${_('Advanced Search')}</a>
    % endif
        </form>
</%def>


<%def name="title_content()" filter="trim">
${_('Datasets')} - ${parent.title_content()}
</%def>

