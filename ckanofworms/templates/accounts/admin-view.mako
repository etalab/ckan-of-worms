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
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Account.get_admin_class_url(ctx)}">${_(u"Accounts")}</a></li>
            <li class="active">${account.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${account.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
##            <a class="btn btn-default" href="${account.get_admin_url(ctx, 'stats')}">${_(u'Statistics')}</a>
            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'accounts', account.name)}">${_(u'JSON')}</a>
            <a class="btn btn-default" href="${account.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
            <a class="btn btn-danger"  href="${account.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${account.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
<%
    account_alerts = copy.deepcopy(account.alerts) if account.alerts is not None else {}
%>\
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'fullname')
        value = account.fullname
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Full Name"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'name')
        value = account.name
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'email')
        value = account.email
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Email"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'email_hash')
        value = account.email_hash
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Email Hash"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'about')
        value = account.about
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("About"))}</b></div>
            % if value is not None:
            <div class="col-sm-10">
                <ul class="nav nav-tabs">
                    <li class="active"><a data-toggle="tab" href="#about-view">${_(u"View")}</a></li>
                    <li><a data-toggle="tab" href="#about-source">${_(u"Source")}</a></li>
                </ul>
                <div class="tab-content">
                    <div class="active tab-pane" id="about-view">
                        ${texthelpers.htmlify_markdown(value) | n}
                    </div>
                    <div class="tab-pane" id="about-source">
                        <pre class="break-word">${value}</pre>
                    </div>
                </div>
            </div>
            % endif
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'admin')
        value = account.admin
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Admin"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'sysadmin')
        value = account.sysadmin
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Sysadmin"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'api_key')
        value = account.api_key
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("API Key"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
<%
        alerts = self.attr.extract_item_alerts(account_alerts, 'created')
        value = account.created
%>\
        % if value is not None or alerts:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_alerts alerts="${alerts}"/>
        % endif
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("ID"))}</b></div>
            <div class="col-sm-10">${account._id}</div>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(account_alerts, 'id')}"/>
<%
    remaining_keys = set()
    for level_alerts in account_alerts.itervalues():
        for author_alerts in level_alerts.itervalues():
            remaining_keys.update(author_alerts['error'].iterkeys())
%>\
    % for key in sorted(remaining_keys):
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
            <pre class="col-sm-10">${json.dumps(getattr(account, key, None),
                    encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
        </div>
        <%self:field_alerts alerts="${self.attr.extract_item_alerts(account_alerts, key)}"/>
    % endfor
</%def>

