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

from ckanofworms import conv, model, urls
%>


<%inherit file="/object-admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Group.get_admin_class_url(ctx)}">${_(u"Groups")}</a></li>
            <li class="active">${group.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${group.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${model.Dataset.get_admin_class_url(ctx, group = group.title)}">${_(u'Datasets')}</a>
##            <a class="btn btn-default" href="${group.get_admin_url(ctx, 'stats')}">${_(u'Statistics')}</a>
            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'groups', group.name)}">${_(u'JSON')}</a>
##            <a class="btn btn-default" href="${group.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
##            <a class="btn btn-danger"  href="${group.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${group.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
<%
    group_alerts = copy.deepcopy(group.alerts) if group.alerts is not None else {}
%>\
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
            <div class="col-sm-10">${group.name}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(group_alerts, 'name')}"/>
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
            <div class="col-sm-10">${group.title}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(group_alerts, 'title')}"/>
<%
        alerts = self.attr.extract_item_alerts(group_alerts, 'description')
        value = group.description
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
            <pre class="break-word col-sm-10">${value}</pre>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(group_alerts, 'image_url')
        value = group.image_url
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Image"))}</b></div>
            <div class="break-word col-sm-10"><img class="img-responsive" src="${value}"></div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(group_alerts, 'created')
        value = group.created
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(group_alerts, 'revision_id')
        value = group.revision_id
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
            <div class="col-sm-10">${group._id}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(group_alerts, 'id')}"/>
<%
    remaining_keys = set()
    for level_alerts in group_alerts.itervalues():
        for author_alerts in level_alerts.itervalues():
            remaining_keys.update(author_alerts['error'].iterkeys())
%>\
    % for key in sorted(remaining_keys):
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
            <pre class="col-sm-10">${json.dumps(getattr(group, key, None),
                    encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(group_alerts, key)}"/>
    % endfor
</%def>

