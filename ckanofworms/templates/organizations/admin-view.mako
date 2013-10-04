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
            <li><a href="${model.Organization.get_admin_class_url(ctx)}">${_(u"Organizations")}</a></li>
            <li class="active">${organization.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${organization.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${model.Dataset.get_admin_class_url(ctx, organization = organization.title)}">${_(u'Produced Datasets')}</a>
            <a class="btn btn-default" href="${model.Dataset.get_admin_class_url(ctx, supplier = organization.title)}">${_(u'Supplied Datasets')}</a>
##            <a class="btn btn-default" href="${organization.get_admin_url(ctx, 'stats')}">${_(u'Statistics')}</a>
            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'organizations', organization._id)}">${_(u'JSON')}</a>
##            <a class="btn btn-default" href="${organization.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
##            <a class="btn btn-danger"  href="${organization.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${organization.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
<%
    organization_errors = copy.deepcopy(organization.errors) if organization.errors is not None else {}
%>\
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
            <div class="col-sm-10">${organization.name}</div>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(organization_errors, 'name')}"/>
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
            <div class="col-sm-10">${organization.title}</div>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(organization_errors, 'title')}"/>
<%
        errors = self.attr.extract_item_errors(organization_errors, 'description')
        value = organization.description
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
            <pre class="break-word col-sm-10">${value}</pre>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(organization_errors, 'image_url')
        value = organization.image_url
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Image"))}</b></div>
            <div class="break-word col-sm-10"><img src="${value}"></div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(organization_errors, 'created')
        value = organization.created
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(organization_errors, 'revision_id')
        value = organization.revision_id
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Revision ID"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("ID"))}</b></div>
            <div class="col-sm-10">${organization._id}</div>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(organization_errors, 'id')}"/>
<%
    remaining_keys = set()
    for author, author_errors in organization_errors.iteritems():
        remaining_keys.update(author_errors['error'].iterkeys())
%>\
    % for key in sorted(remaining_keys):
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
            <pre class="col-sm-10">${json.dumps(getattr(organization, key, None),
                    encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(organization_errors, key)}"/>
    % endfor
</%def>

