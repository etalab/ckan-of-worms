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
import collections

from ckanofworms import model, urls, conf
%>


<%inherit file="site.mako"/>


<%def name="section_class()" filter="trim">animated</%def>
<%def name="before_container()" filter="trim">
<div class="animation"></div>
</%def>

<%def name="breadcrumb()" filter="trim">
</%def>


<%def name="container_content()" filter="trim">
##        <div class="page-header">
##            <h1><%self:brand/></h1>
##        </div>
        <%self:jumbotron/>
</%def>


<%def name="jumbotron()" filter="trim">
<%
    user = model.get_user(ctx)
%>\
    <div class="jumbotron">
        <h2>${_(u"Welcome to CKAN-of-Worms")}</h2>
        <p>${_(u"A logger for errors found in CKAN datasets")}</p>
    % if user is None:
        <a class="btn btn-large btn-primary sign-in" href="#"
            title="${_(u'Sign in with Persona')}">${_('Sign In')}</a>
    % endif
    </div>
</%def>

<%def name="scripts()" filter="trim">
${parent.scripts()}
 % for url in conf['assets']['animation-js'].urls():
 <script src="${url}"></script>
 % endfor
</%def>
