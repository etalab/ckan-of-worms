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
import copy
import json

from ckanofworms import model, texthelpers, urls


alert_levels = ['critical', 'error', 'warning']
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


<%inherit file="/object-admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
##            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Dataset.get_admin_class_url(ctx)}">${_(u"Datasets")}</a></li>
            <li class="active">${dataset.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
    <h1>${dataset.get_title(ctx)}</h1>
    <%self:summary/>
    <%self:view_fields/>

    <div class="text-center">
            <div class="btn-group">
                <a class="btn btn-primary" href="${dataset.get_back_url(ctx)}" target="_blank">
                    <span class="glyphicon glyphicon-wrench"></span>
                    ${_(u'Repair')}
                </a>
                <a class="btn btn-default" href="${dataset.get_front_url(ctx)}" target="_blank">
                    <span class="glyphicon glyphicon-globe"></span>
                    ${_(u'View in Front')}
                </a>
                <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'stats')}">
                    <span class="glyphicon glyphicon-stats"></span>
                    ${_(u'Statistics')}
                </a>
                <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'datasets', dataset.name)}">
                    <span class="glyphicon glyphicon-download-alt"></span>
                    ${_(u'JSON')}
                </a>
                <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'publish')}">
                    <span class="glyphicon glyphicon-export"></span>
                    ${_(u'Publish')}
                </a>
    ##            <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
    ##            <a class="btn btn-danger"  href="${dataset.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
            </div>
    </div>
</%def>


<%def name="title_content()" filter="trim">
${dataset.get_title(ctx)} - ${parent.title_content()}
</%def>

<%def name="summary()" filter="trim">
    <%
    alerts_ranking = dict(
        (level, sum(
            len(author_alerts['error'])
            for author_alerts in level_alerts.itervalues()
            ))
        for level, level_alerts in (dataset.alerts or {}).iteritems()
        if level in alert_levels
        )
%>\
    % if alerts_ranking or dataset.weight is not None and dataset.weight < 3.0:
        <div class="jumbotron card">
            <div class="page-header">
                <a class="btn btn-primary pull-right" href="${dataset.get_back_url(ctx)}" target="_blank">
                    <span class="glyphicon glyphicon-wrench"></span>
                    ${_(u"Repair")}
                </a>
                <h3>${_(u"This dataset has some defects")}</h3>

            </div>
            <ul class="list-inline">
        % if alerts_ranking:
            % for level in alert_levels:
<%
                count = alerts_ranking.get(level)
                if count is None:
                    continue
%>\
                    <li>
                        ${_(u"{}:").format(_(title_by_alert_level[level]), count)}
                        <span class="label ${label_class_by_alert_level[level]}">${count}</span>
                    % if level == 'critical':
                        <span class="glyphicon glyphicon-warning-sign"></span>
                    % endif
                    </li>
            % endfor
        % endif
            </ul>
        % if dataset.weight is not None and dataset.weight < 3.0:
            <p>
                ${_(u"Low search rank:")}
                <span class="label label-default">${_(u"{:3.2f}").format(dataset.weight)}</span>
            </p>
        % endif
                </ul>
                <p>${_(u"Please look at the alerts below and repair this dataset now.")}</p>
        </div>
    % endif
</%def>

<%def name="view_fields()" filter="trim">
    <%
        dataset_alerts = copy.deepcopy(dataset.alerts) if dataset.alerts is not None else {}
    %>
    <form class="form-horizontal form-compact" role="form">
        <!-- Name field -->
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Name")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${dataset.name}</p>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, 'name')}"/>
            </div>
        </div>

        <!-- Title field -->
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Title")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${dataset.title}</p>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, 'title')}"/>
            </div>
        </div>
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'notes')
        value = dataset.notes
%>\
        % if value is not None or alerts:
        <!-- Notes field -->
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Notes")}</label>
            <div class="col-sm-10">
                % if value is not None:
                <ul class="nav nav-tabs">
                    <li class="active"><a data-toggle="tab" href="#notes-view">${_(u"View")}</a></li>
                    <li><a data-toggle="tab" href="#notes-source">${_(u"Source")}</a></li>
                </ul>
                <div class="tab-content">
                    <div class="active tab-pane" id="notes-view">
                        ${texthelpers.htmlify_markdown(value) | n}
                    </div>
                    <div class="tab-pane" id="notes-source">
                        <pre class="break-word">${value}</pre>
                    </div>
                </div>
                % endif
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
    resources_alerts = self.attr.extract_item_alerts(dataset_alerts, 'resources')
%>\
    % if dataset.resources or resources_alerts:
    <div class="form-group">
        <label class="col-sm-2 control-label">${_("Resources")}</label>
        <div class="col-sm-10">
            % if dataset.resources:
                <ul class="list-group">
                % for resource_index, resource in enumerate(dataset.resources or []):
            <%
                resource_alerts = self.attr.extract_item_alerts(resources_alerts, resource_index)
            %>\
                <li class="list-group-item">
            <%
                alerts = self.attr.extract_item_alerts(resource_alerts, 'name')
                value = resource.get('name')
            %>\

                % if value is not None or alerts:
                <div class="form-group">
                    <label class="col-sm-2 control-label">${_("Name")}</label>
                    <div class="col-sm-10">
                        <p class="form-control-static">${value}</p>
                        <%self:field_alerts alerts="${alerts}"/>
                    </div>
                </div>
                % endif
            <%
                alerts = self.attr.extract_item_alerts(resource_alerts, 'description')
                value = resource.get('description')
            %>\
                % if value is not None or alerts:
                <div class="form-group">
                    <label class="col-sm-2 control-label">${_("Description")}</label>
                    <div class="col-sm-10">
                        <pre class="break-word">${value}</pre>
                        <%self:field_alerts alerts="${alerts}"/>
                    </div>
                </div>
                % endif
    <%
                alerts = self.attr.extract_item_alerts(resource_alerts, 'url')
                value = resource.get('url')
    %>\
                % if value is not None or alerts:
                <div class="form-group">
                    <label class="col-sm-2 control-label">${_("URL")}</label>
                    <div class="col-sm-10">
                        <p class="form-control-static">
                            <a href="${value}" target="_blank">${value}</a>
                        </p>
                        <%self:field_alerts alerts="${alerts}"/>
                    </div>
                </div>
                % endif
    <%
                alerts = self.attr.extract_item_alerts(resource_alerts, 'format')
                value = resource.get('format')
    %>\
                % if value is not None or alerts:
                <div class="form-group">
                    <label class="col-sm-2 control-label">${_("Format")}</label>
                    <div class="col-sm-10">
                        <p class="form-control-static">${value}</p>
                        <%self:field_alerts alerts="${alerts}"/>
                    </div>
                </div>
                % endif
    <%
                alerts = self.attr.extract_item_alerts(resource_alerts, 'last_modified')
                value = resource.get('last_modified')
    %>\
                % if value is not None or alerts:
                <div class="form-group">
                    <label class="col-sm-2 control-label">${_("Last modified")}</label>
                    <div class="col-sm-10">
                        <p class="form-control-static">${value}</p>
                        <%self:field_alerts alerts="${alerts}"/>
                    </div>
                </div>
                % endif
    <%
                alerts = self.attr.extract_item_alerts(resource_alerts, 'created')
                value = resource.get('created')
    %>\
                % if value is not None or alerts:
                <div class="form-group">
                    <label class="col-sm-2 control-label">${_("Created")}</label>
                    <div class="col-sm-10">
                        <p class="form-control-static">${value}</p>
                        <%self:field_alerts alerts="${alerts}"/>
                    </div>
                </div>
                % endif
    <%
                remaining_keys = set()
                for level_alerts in resource_alerts.itervalues():
                    for author_alerts in level_alerts.itervalues():
                        remaining_keys.update(author_alerts['error'].iterkeys())
    %>\
                % for key in sorted(remaining_keys):
                    <div class="form-group">
                        <label class="col-sm-2 control-label">${_(key)}</label>
                        <div class="col-sm-10">
                            <pre>${json.dumps(resource.get(key),
                                encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                            <%self:field_alerts alerts="${self.attr.extract_item_alerts(resource_alerts, key)}"/>
                        </div>
                    </div>
                % endfor
                </li>
            % endfor
                </ul>
            % endif
            <%self:field_alerts alerts="${resources_alerts}"/>
        </div>
    </div>

    % endif
<%
    extras_alerts = self.attr.extract_item_alerts(dataset_alerts, 'extras')
%>\
    % if dataset.extras or extras_alerts:
    <div class="form-group">
        <label class="col-sm-2 control-label">${_("Extras")}</label>
        <div class="col-sm-10">
            % if dataset.extras:
                <ul class="list-group">

        % for extra_index, extra in enumerate(dataset.extras or []):
<%
            extra_alerts = self.attr.extract_item_alerts(extras_alerts, extra_index)
%>\
            <li class="list-group-item">
<%
            alerts = self.attr.extract_item_alerts(extra_alerts, 'key')
            value = extra.get('key')
%>\
            % if value is not None or alerts:
                <div class="form-group">
                    <label class="col-sm-2 control-label">${_("Key")}</label>
                    <div class="col-sm-10">
                        <p class="form-control-static">${value}</p>
                        <%self:field_alerts alerts="${alerts}"/>
                    </div>
                </div>
            % endif
<%
            alerts = self.attr.extract_item_alerts(extra_alerts, 'value')
            value = extra.get('value')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Value")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">${value}</p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            remaining_keys = set()
            for level_alerts in extra_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
            <div class="form-group">
                <label class="col-sm-2 control-label">${_(key)}</label>
                <div class="col-sm-10">
                    <pre>${json.dumps(extra.get(key),
                        encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endfor
            </li>
        % endfor
            </ul>
            % endif
            <%self:field_alerts alerts="${extras_alerts}"/>
        </div>
    </div>
    % endif
<%
        # TODO: Replace with groups_id.
        groups_alerts = self.attr.extract_item_alerts(dataset_alerts, 'groups')
%>\
    % if dataset.groups or groups_alerts:
    <div class="form-group">
        <label class="col-sm-2 control-label">${_("Groups")}</label>
        <div class="col-sm-10">
            % if dataset.groups:
                <ul class="list-group">
                % for group_index, group_attributes in enumerate(dataset.groups or []):
<%
            group_alerts = self.attr.extract_item_alerts(groups_alerts, group_index)
%>\
                <li class="list-group-item">
<%
            alerts = self.attr.extract_item_alerts(group_alerts, 'id')
            value = group_attributes.get('id')
            group = model.Group.find_one(value) if value is not None else None
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("ID")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">
                    % if group is None:
                        ${value}
                    % else:
                        <a href="${group.get_admin_url(ctx)}">${group.get_title(ctx)}</a>
                    % endif
                    </p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            remaining_keys = set()
            for level_alerts in group_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
            <div class="form-group">
                <label class="col-sm-2 control-label">${_(key)}</label>
                <div class="col-sm-10">
                    <pre>${json.dumps(group_attributes.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                    <%self:field_alerts alerts="${self.attr.extract_item_alerts(group_alerts, key)}"/>
                </div>
            </div>
            % endfor
            </li>
        % endfor
            </ul>
            % endif
            <%self:field_alerts alerts="${groups_alerts}"/>
        </div>
    </div>
    % endif
<%
        # TODO: Replace list of dicts with a list of strings.
        tags_alerts = self.attr.extract_item_alerts(dataset_alerts, 'tags')
%>\
    % if dataset.tags or tags_alerts:
    <div class="form-group">
        <label class="col-sm-2 control-label">${_("Tags")}</label>
        <div class="col-sm-10">
            % if dataset.tags:
                <ul class="list-group">
        % for tag_index, tag in enumerate(dataset.tags or []):
<%
            tag_alerts = self.attr.extract_item_alerts(tags_alerts, tag_index)
%>\
            <li class="list-group-item">
<%
            alerts = self.attr.extract_item_alerts(tag_alerts, 'name')
            value = tag.get('name')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Name")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">
                        <a href="${model.Dataset.get_admin_class_url(ctx, tag = value)}">${value}</a>
                    </p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            remaining_keys = set()
            for level_alerts in tag_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
            <div class="form-group">
                <label class="col-sm-2 control-label">${_(key)}</label>
                <div class="col-sm-10">
                    <pre>${json.dumps(tag.get(key),
                        encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                    <%self:field_alerts alerts="${self.attr.extract_item_alerts(tag_alerts, key)}"/>
                </div>
            </div>
            % endfor
            </li>
        % endfor
            </ul>
            % endif
        <%self:field_alerts alerts="${tags_alerts}"/>
        </div>
    </div>
    % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'temporal_coverage_from')
        value = dataset.temporal_coverage_from
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Temporal Coverage From")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'temporal_coverage_to')
        value = dataset.temporal_coverage_to
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Temporal Coverage To")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'frequency')
        value = dataset.frequency
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Update frequency")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'territorial_coverage')
        value = u', '.join(
            territory_kind_code_name.rsplit(u'/', 1)[-1]
            for territory_kind_code_name in (
                fragment.strip()
                for fragment in dataset.territorial_coverage.split(u',')
                )
            if territory_kind_code_name
            ) if dataset.territorial_coverage is not None else None
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Territorial Coverage")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'territorial_coverage_granularity')
        value = dataset.territorial_coverage_granularity
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Territorial Coverage Granularity")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'owner_org')
        value = dataset.owner_org
        organization = model.Organization.find_one(value) if value is not None else None
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Organization")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">
                % if organization is None:
                    ${value}
                % else:
                    <a href="${organization.get_admin_url(ctx)}">${organization.get_title(ctx)}</a>
                % endif
                </p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'author')
        value = dataset.author
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Office, Department or Service")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'author_email')
        value = dataset.author_email
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Contact Email")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'maintainer')
        value = dataset.maintainer
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Maintainer")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'maintainer_email')
        value = dataset.maintainer_email
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Maintainer Email")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'supplier_id')
        value = dataset.supplier_id
        organization = model.Organization.find_one(value) if value is not None else None
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Supplier")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">
                % if organization is None:
                    ${value}
                % else:
                    <a href="${organization.get_admin_url(ctx)}">${organization.get_title(ctx)}</a>
                % endif
                </p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'url')
        value = dataset.url
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("URL (in supplier site)")}</label>
            <div class="col-sm-10">
                <p class="break-word form-control-static"><a href="${value}" target="_blank">${value}</a></p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'license_id')
        value = dataset.license_id
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("License")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'weight')
        value = dataset.weight
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Weight")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'metadata_modified')
        value = dataset.metadata_modified
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Metadata Modified")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'metadata_created')
        value = dataset.metadata_created
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Metadata Created")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'revision_timestamp')
        value = dataset.revision_timestamp
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Revision Timestamp")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'timestamp')
        value = dataset.timestamp
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Timestamp")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'revision_id')
        value = dataset.revision_id
%>\
        % if value is not None or alerts:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Revision ID")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${value}</p>
                <%self:field_alerts alerts="${alerts}"/>
            </div>
        </div>
        % endif
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("ID")}</label>
            <div class="col-sm-10">
                <p class="form-control-static">${dataset._id}</p>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, 'id')}"/>
            </div>
        </div>

<%
    related_links_alerts = self.attr.extract_item_alerts(dataset_alerts, 'related')
%>\
 <%
    remaining_keys = set()
    for level_alerts in dataset_alerts.itervalues():
        for author_alerts in level_alerts.itervalues():
            remaining_keys.update(author_alerts['error'].iterkeys())
%>\
    % for key in sorted(remaining_keys):
    <div class="form-group">
        <label class="col-sm-2 control-label">${_(key)}</label>
        <div class="col-sm-10">
            <pre>${json.dumps(getattr(dataset, key, None),
                encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
            <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, key)}"/>
        </div>
    </div>
    % endfor

    % if dataset.related or related_links_alerts:
    <fieldset>
        <legend>${u"Community Resources"}</legend>
        % if dataset.related:
        <div class="form-group">
            <label class="col-sm-2 control-label">${_("Related")}</label>
            <div class="col-sm-10">
                <ul class="list-group">
        % for related_link_index, related_link in enumerate(dataset.related or []):
<%
            related_link_alerts = self.attr.extract_item_alerts(related_links_alerts, related_link_index)
%>\
            <li class="list-group-item">
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'title')
            value = related_link.get('title')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Title")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">${value}</p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'description')
            value = related_link.get('description')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Description")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">${value}</p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'url')
            value = related_link.get('url')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("URL")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">
                        <a href="${value}" target="_blank">${value}</a>
                    </p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'image_url')
            value = related_link.get('image_url')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Image")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">
                        <img class="img-responsive" src="${value}">
                    </p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'type')
            value = related_link.get('type')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Type")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">${value}</p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'owner_id')
            value = related_link.get('owner_id')
            account = model.Account.find_one(value) if value is not None else None
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Owner")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">
                    % if account is None:
                        ${value}
                    % else:
                        <a href="${account.get_admin_url(ctx)}">${account.get_title(ctx)}</a>
                    % endif
                    </p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'created')
            value = related_link.get('created')
%>\
            % if value is not None or alerts:
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Created")}</label>
                <div class="col-sm-10">
                    <p class="form-control-static">${value}</p>
                    <%self:field_alerts alerts="${alerts}"/>
                </div>
            </div>
            % endif
<%
            remaining_keys = set()
            for level_alerts in related_link_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
            <div class="form-group">
                <label class="col-sm-2 control-label">${_("Type")}</label>
                <div class="col-sm-10">
                    <pre>${json.dumps(related_link.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                    <%self:field_alerts alerts="${self.attr.extract_item_alerts(related_link_alerts, key)}"/>
                </div>
            </div>
            % endfor
            </li>
        % endfor
            </ul>
            <%self:field_alerts alerts="${related_links_alerts}"/>
        </div>
        % endif
        </fieldset>
    % endif
    </form>
</%def>

