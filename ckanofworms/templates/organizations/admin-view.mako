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
%>


<%inherit file="/object-admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
##            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Organization.get_admin_class_url(ctx)}">${_(u"Organizations")}</a></li>
            <li class="active">${organization.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${organization.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
<%
    produced_dataset_count = model.Dataset.find({'owner_org': organization._id}).count()
    supplied_dataset_count = model.Dataset.find({'supplier_id': organization._id}).count()
%>\
            <a class="btn btn-default" href="${model.Dataset.get_admin_class_url(ctx, organization = organization.title)}">${ungettext(
                u'{} Produced Dataset', u'{} Produced Datasets', produced_dataset_count).format(produced_dataset_count)}</a>
            <a class="btn btn-default" href="${model.Dataset.get_admin_class_url(ctx, supplier = organization.title)}">${ungettext(
                u'{} Supplied Dataset', u'{} Supplied Datasets', supplied_dataset_count).format(supplied_dataset_count)}</a>
##            <a class="btn btn-default" href="${organization.get_admin_url(ctx, 'stats')}">${_(u'Statistics')}</a>
            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'organizations', organization.name)}">${_(u'JSON')}</a>
##            <a class="btn btn-default" href="${organization.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
##            <a class="btn btn-danger"  href="${organization.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${organization.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
<%
    organization_alerts = copy.deepcopy(organization.alerts) if organization.alerts is not None else {}
%>\
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
            <div class="col-sm-10">${organization.name}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(organization_alerts, 'name')}"/>
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
            <div class="col-sm-10">${organization.title}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(organization_alerts, 'title')}"/>
<%
        alerts = self.attr.extract_item_alerts(organization_alerts, 'description')
        value = organization.description
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
            % if value is not None:
            <div class="col-sm-10">
                <ul class="nav nav-tabs">
                    <li class="active"><a data-toggle="tab" href="#description-view">${_(u"View")}</a></li>
                    <li><a data-toggle="tab" href="#description-source">${_(u"Source")}</a></li>
                </ul>
                <div class="tab-content">
                    <div class="active tab-pane" id="description-view">
                        ${texthelpers.htmlify_markdown(value) | n}
                    </div>
                    <div class="tab-pane" id="description-source">
                        <pre class="break-word">${value}</pre>
                    </div>
                </div>
            </div>
            % endif
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(organization_alerts, 'image_url')
        value = organization.image_url
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Image"))}</b></div>
            <div class="break-word col-sm-10"><img class="img-responsive" src="${value}"></div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(organization_alerts, 'created')
        value = organization.created
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(organization_alerts, 'revision_id')
        value = organization.revision_id
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
            <div class="col-sm-10">${organization._id}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(organization_alerts, 'id')}"/>
<%
    remaining_keys = set()
    for level_alerts in organization_alerts.itervalues():
        for author_alerts in level_alerts.itervalues():
            remaining_keys.update(author_alerts['error'].iterkeys())
%>\
    % for key in sorted(remaining_keys):
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
            <pre class="col-sm-10">${json.dumps(getattr(organization, key, None),
                    encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(organization_alerts, key)}"/>
    % endfor
</%def>

