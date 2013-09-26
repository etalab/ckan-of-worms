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
import json

from ckanofworms import conv, model, urls
%>


<%inherit file="/site.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Account.get_admin_class_url(ctx)}">${_(u"Accounts")}</a></li>
            <li class="active">${account.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${account.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${account.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
            <a class="btn btn-danger"  href="${account.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${account.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
        <div class="field">
            <b class="field-label">${_('{0}:').format(_("ID"))}</b>
            <span class="field-value">${account._id}</span>
        </div>
    % if account.email:
        <div class="field">
            <b class="field-label">${_('{0}:').format(_("Email"))}</b>
            <span class="field-value">${account.email}</span>
        </div>
    % endif
    % if account.admin:
        <div class="field">
            <b class="field-label">${_('{0}:').format(_("Profile"))}</b>
            <span class="field-value">${_(u'Administrator')}</span>
        </div>
    % endif
    % if account.api_key:
        <div class="field">
            <b class="field-label">${_('{0}:').format(_("API Key"))}</b>
            <span class="field-value">${account.api_key}</span>
        </div>
    % endif
        <div class="field">
            <b class="field-label">${_('{0}:').format(_("JSON"))}</b>
            <pre class="break-word field-value offset1">${json.dumps(
                conv.check(conv.method('turn_to_json'))(account, state = ctx),
                encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
        </div>
</%def>

