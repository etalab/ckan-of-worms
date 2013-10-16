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
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Dataset.get_admin_class_url(ctx)}">${_(u"Datasets")}</a></li>
            <li class="active">${dataset.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${dataset.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
            <a class="btn btn-primary" href="${dataset.get_back_url(ctx)}" target="_blank">${_(u'Repair')}</a>
            <a class="btn btn-default" href="${dataset.get_front_url(ctx)}" target="_blank">${_(u'View in Front')}</a>
            <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'stats')}">${_(u'Statistics')}</a>
            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'datasets', dataset.name)}">${_(u'JSON')}</a>
            <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'publish')}">${_(u'Publish')}</a>
##            <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
##            <a class="btn btn-danger"  href="${dataset.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${dataset.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
<%
    dataset_alerts = copy.deepcopy(dataset.alerts) if dataset.alerts is not None else {}
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
        <div class="jumbotron">
            <div class="container">
                <h1>${_(u"This dataset has some defects")}</h1>
                <ul class="list-unstyled">
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
        % if dataset.weight is not None and dataset.weight < 3.0:
                    <li>
                        ${_(u"Low search rank:")}
                        <span class="label label-default">${_(u"{:3.2f}").format(dataset.weight)}</span>
                    </li>
        % endif
                </ul>
                <p>${_(u"Please look at the alerts below and repair this dataset now.")}</p>
                <p><a class="btn btn-primary btn-lg" href="${dataset.get_back_url(ctx)}">${_(u"Repair")}</a></p>
            </div>
        </div>
    % endif
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
            <div class="col-sm-10">${dataset.name}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, 'name')}"/>
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
            <div class="col-sm-10">${dataset.title}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, 'title')}"/>
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'notes')
        value = dataset.notes
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Notes"))}</b></div>
            % if value is not None:
            <div class="col-sm-10">
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
            </div>
            % endif
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
    resources_alerts = self.attr.extract_item_alerts(dataset_alerts, 'resources')
%>\
    % if dataset.resources or resources_alerts:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Resources"))}</b></div>
            <ul class="col-sm-10 list-group">
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
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(resource_alerts, 'description')
            value = resource.get('description')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
                    <pre class="break-word col-sm-10">${value}</pre>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(resource_alerts, 'url')
            value = resource.get('url')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("URL"))}</b></div>
                    <div class="break-word col-sm-10"><a href="${value}">${value}</a></div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(resource_alerts, 'format')
            value = resource.get('format')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Format"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(resource_alerts, 'last_modified')
            value = resource.get('last_modified')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Last Modified"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(resource_alerts, 'created')
            value = resource.get('created')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            remaining_keys = set()
            for level_alerts in resource_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(resource.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(resource_alerts, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_alerts alerts="${resources_alerts}"/>
    % endif
<%
    extras_alerts = self.attr.extract_item_alerts(dataset_alerts, 'extras')
%>\
    % if dataset.extras or extras_alerts:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Extras"))}</b></div>
            <ul class="col-sm-10 list-group">
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
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Key"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(extra_alerts, 'value')
            value = extra.get('value')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Value"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            remaining_keys = set()
            for level_alerts in extra_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(extra.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(extra_alerts, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_alerts alerts="${extras_alerts}"/>
    % endif
<%
        # TODO: Replace with groups_id.
        groups_alerts = self.attr.extract_item_alerts(dataset_alerts, 'groups')
%>\
    % if dataset.groups or groups_alerts:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Groups"))}</b></div>
            <ul class="col-sm-10 list-group">
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
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("ID"))}</b></div>
                    <div class="col-sm-10">
                    % if group is None:
                        ${value}
                    % else:
                        <a href="${group.get_admin_url(ctx)}">${group.get_title(ctx)}</a>
                    % endif
                    </div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            remaining_keys = set()
            for level_alerts in group_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(group_attributes.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(group_alerts, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_alerts alerts="${groups_alerts}"/>
    % endif
<%
        # TODO: Replace list of dicts with a list of strings.
        tags_alerts = self.attr.extract_item_alerts(dataset_alerts, 'tags')
%>\
    % if dataset.tags or tags_alerts:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Tags"))}</b></div>
            <ul class="col-sm-10 list-group">
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
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
                    <div class="col-sm-10">
                        <a href="${model.Dataset.get_admin_class_url(ctx, tag = value)}">${value}</a>
                    </div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            remaining_keys = set()
            for level_alerts in tag_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(tag.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(tag_alerts, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_alerts alerts="${tags_alerts}"/>
    % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'temporal_coverage_from')
        value = dataset.temporal_coverage_from
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Temporal Coverage From"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'temporal_coverage_to')
        value = dataset.temporal_coverage_to
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Temporal Coverage To"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'frequency')
        value = dataset.frequency
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Update Frequency"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'territorial_coverage')
        value = dataset.territorial_coverage
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Territorial Coverage"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'territorial_coverage_granularity')
        value = dataset.territorial_coverage_granularity
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Territorial Coverage Granularity"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'owner_org')
        value = dataset.owner_org
        organization = model.Organization.find_one(value) if value is not None else None
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Organization"))}</b></div>
            <div class="col-sm-10">
            % if organization is None:
                ${value}
            % else:
                <a href="${organization.get_admin_url(ctx)}">${organization.get_title(ctx)}</a>
            % endif
            </div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'author')
        value = dataset.author
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Office, Department or Service"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'author_email')
        value = dataset.author_email
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Contact Email"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'maintainer')
        value = dataset.maintainer
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Maintainer"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'maintainer_email')
        value = dataset.maintainer_email
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Maintainer Email"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'supplier_id')
        value = dataset.supplier_id
        organization = model.Organization.find_one(value) if value is not None else None
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Supplier"))}</b></div>
            <div class="col-sm-10">
            % if organization is None:
                ${value}
            % else:
                <a href="${organization.get_admin_url(ctx)}">${organization.get_title(ctx)}</a>
            % endif
            </div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
            alerts = self.attr.extract_item_alerts(dataset_alerts, 'url')
            value = dataset.get('url')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("URL (in supplier site)"))}</b></div>
                    <div class="break-word col-sm-10"><a href="${value}">${value}</a></div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'license_id')
        value = dataset.license_id
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("License"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'weight')
        value = dataset.weight
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Weight"))}</b></div>
            <div class="col-sm-10">${_(u'{:3.2f}').format(value)}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'metadata_modified')
        value = dataset.metadata_modified
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Metadata Modified"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'metadata_created')
        value = dataset.metadata_created
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Metadata Created"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'revision_timestamp')
        value = dataset.revision_timestamp
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Revision Timestamp"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'timestamp')
        value = dataset.timestamp
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Timestamp"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(dataset_alerts, 'revision_id')
        value = dataset.revision_id
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Revision ID"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("ID"))}</b></div>
            <div class="col-sm-10">${dataset._id}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, 'id')}"/>
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
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
            <pre class="col-sm-10">${json.dumps(getattr(dataset, key, None),
                    encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(dataset_alerts, key)}"/>
    % endfor
   % if dataset.related or related_links_alerts:
        <h3>${u"Community Resources"}</h3>
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Related"))}</b></div>
            <ul class="col-sm-10 list-group">
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
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'description')
            value = related_link.get('description')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
                    <pre class="break-word col-sm-10">${value}</pre>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'url')
            value = related_link.get('url')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("URL"))}</b></div>
                    <div class="break-word col-sm-10"><a href="${value}">${value}</a></div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'image_url')
            value = related_link.get('image_url')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Image"))}</b></div>
                    <div class="break-word col-sm-10"><img class="img-responsive" src="${value}"></div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'type')
            value = related_link.get('type')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Type"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'owner_id')
            value = related_link.get('owner_id')
            account = model.Account.find_one(value) if value is not None else None
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Owner"))}</b></div>
                    <div class="col-sm-10">
                    % if account is None:
                        ${value}
                    % else:
                        <a href="${account.get_admin_url(ctx)}">${account.get_title(ctx)}</a>
                    % endif
                    </div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            alerts = self.attr.extract_item_alerts(related_link_alerts, 'created')
            value = related_link.get('created')
%>\
            % if value is not None or alerts:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_alerts alerts="${alerts}"/>
            % endif
<%
            remaining_keys = set()
            for level_alerts in related_link_alerts.itervalues():
                for author_alerts in level_alerts.itervalues():
                    remaining_keys.update(author_alerts['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(related_link.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_alerts alerts="${self.attr.extract_item_alerts(related_link_alerts, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_alerts alerts="${related_links_alerts}"/>
    % endif
</%def>

