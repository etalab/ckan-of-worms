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


<%doc>
    Site template inherited by each page
</%doc>


<%!
import urlparse

from ckanofworms import conf, model, urls
%>


<%def name="body_content()" filter="trim">
    <%self:breadcrumb/>
    <section class="default">
        <div class="container">
            <%self:container_content/>
        </div>
    </section>
    <%self:footer/>
</%def>


<%def name="brand()" filter="trim">
${conf['realm']}
</%def>


<%def name="breadcrumb()" filter="trim">
    <section class="breadcrumb">
        <div class="container">
            <ul class="breadcrumb">
                <%self:breadcrumb_content/>
            </ul>
        </div>
    </section>
</%def>


<%def name="breadcrumb_content()" filter="trim">
    <li>
        <a href="${urls.get_url(ctx)}" title="${_('Home')}">
            <span class="glyphicon glyphicon-home"></span>
        </a>
    </li>
</%def>


<%def name="container_content()" filter="trim">
</%def>


<%def name="css()" filter="trim">
    % for url in conf['assets']['site-css'].urls():
    <link href="${url}" media="screen" rel="stylesheet">
    % endfor
</%def>


<%def name="error_alert()" filter="trim">
    % if errors:
                <div class="alert alert-block alert-error">
                    <h4 class="alert-heading">${_('Error!')}</h4>
        % if '' in errors:
<%
            error = unicode(errors[''])
%>\
            % if u'\n' in error:
                    <pre class="break-word">${error}</error>
            % else:
                    ${error}
            % endif
        % else:
                    ${_(u"Please, correct the informations below.")}
        % endif
                </div>
    % endif
</%def>


<%def name="feeds()" filter="trim">
    <link href="${urls.get_url(ctx, 'api', '1', 'datasets', format = 'atom')}" rel="alternate" title="${
            _(u'{} - Datasets Atom feed').format(conf['realm'])}" type="application/atom+xml">
    <link href="${urls.get_url(ctx, 'api', '1', 'organizations', format = 'atom')}" rel="alternate" title="${
            _(u'{} - Organizations Atom feed').format(conf['realm'])}" type="application/atom+xml">
</%def>


<%def name="footer()" filter="trim">
<section class="footer">
    <div class="container">
        <footer class="row">

            <section class="col-xs-6 col-sm-3 col-md-2 col-lg-2">
                <h5>${_('The Open Data')}</h5>
                <ul>
                    <li><a href="//wiki.data.gouv.fr/wiki/FAQ">${_('How it works ?')}</a></li>
                    <li><a href="${urls.ckan_url(ctx, 'organization')}">${_('Publishers')}</a></li>
                    <li>
                        <a href="//wiki.data.gouv.fr/wiki/Licence_Ouverte_/_Open_Licence">
                            ${_('Open Licence')}
                        </a>
                    </li>
                    <li><a href="${urls.ckan_url(ctx, 'metrics')}">${_('Metrics')}</a></li>
                    <li><a href="http://www.etalab.gouv.fr/">Etalab</a></li>
                    <li><a href="//wiki.data.gouv.fr/wiki/Cr%C3%A9dits">${_('Credits')}</a></li>
                </ul>
            </section>
            <section class="col-xs-6 col-sm-3 col-md-2 col-lg-2">
                <h5>${_('Topics')}</h5>
                <ul>
                    % for topic in main_topics:
                    <li>
                        <a href="${ topic['url'].format(lang=lang) }">
                        ${ topic['title'] }
                        </a>
                    </li>
                    % endfor
                </ul>
            </section>

            <section class="col-xs-6 col-sm-3 col-md-2 col-lg-2">
                <h5>${_('Network')}</h5>
                <ul>
                    <li><a href="http://www.gouvernement.fr/">Gouvernement.fr </a></li>
                    <li><a href="http://www.france.fr/">France.fr</a></li>
                    <li><a href="http://www.legifrance.gouv.fr/">Legifrance.gouv.fr </a></li>
                    <li><a href="http://www.service-public.fr/">Service-public.fr</a></li>
                    <li><a href="http://opendatafrance.net/">Opendata France</a></li>
                </ul>
            </section>

            <section class="col-xs-6 col-sm-3 col-md-4 col-lg-4">
                <h5>${_('Contact')}</h5>
                <ul>
                    <li><a href="https://twitter.com/Etalab">Twitter</a></li>
                    <li><a href="https://github.com/etalab">GitHub</a></li>
                    <li><a href="mailto:info@data.gouv.fr">info@data.gouv.fr</a></li>
                </ul>
            </section>

            <section class="col-xs-9 col-xs-offset-3 col-sm-offset-0 col-sm-2 col-md-2 col-lg-2">
                <img class="logo" src="${urls.static('img/etalab-logo.png')}"></img>
                <p>&copy; 2013 ETALAB, Inc.</p>
            </section>

            <p class="bottom-right"><a href="#">${_('Back to top')}</a></p>

        </footer>
    </div>
</section>
</%def>


<%def name="footer_service()" filter="trim">
</%def>


<%def name="hidden_fields()" filter="trim">
</%def>


<%def name="ie_scripts()" filter="trim">
    <!--[if lt IE 9]>
    % for url in conf['assets']['site-ie-js'].urls():
        <script src="${url}"></script>
    % endfor
    <![endif]-->
</%def>


<%def name="metas()" filter="trim">
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    ## Make sure Internet Explorer can't use Compatibility Mode, as this will break Persona.
    <meta http-equiv="X-UA-Compatible" content="IE=Edge">
    <meta name="domain" content="${conf['domain']}" />
    <link rel="home" href="${conf['weckan_url']}" />
    <link rel="wiki" href="${conf['wiki_url']}" />
    <link rel="wiki-api" href="${conf['wiki_api_url']}" />
</%def>


<%def name="scripts()" filter="trim">
    % for url in conf['assets']['site-js'].urls():
    <script src="${url}"></script>
    % endfor
    ## You must include this on every page which uses navigator.id functions. Because Persona is still in development,
    ## you should not self-host the include.js file.
    <script src="https://login.persona.org/include.js"></script>
    <script>
<%
    user = model.get_user(ctx)
%>\
var currentUser = ${user.email if user is not None else None | n, js};


navigator.id.watch({
    loggedInUser: currentUser,
    onlogin: function (assertion) {
        $.ajax({
            type: 'POST',
            url: '/login',
            data: {
                assertion: assertion
            },
            success: function(res, status, xhr) {
                window.location.reload();
            },
            error: function(xhr, status, err) {
                navigator.id.logout();
                alert(${_(u"Login failure: ") | n, js} + err);
            }
        });
    },
    onlogout: function () {
        $.ajax({
            type: 'POST',
            url: '/logout',
            success: function(res, status, xhr) {
                window.location.reload();
            },
            error: function(xhr, status, err) {
                alert(${_(u"Logout failure: ") | n, js} + err);
            }
        });
    }
});


$(function () {
    $('.dropdown-toggle').dropdown();

    $('.sign-in').click(function() {
        navigator.id.request();
    });

    $('.sign-out').click(function() {
        navigator.id.logout();
    });
});
    </script>
</%def>


<%def name="title_content()" filter="trim">
<%self:brand/>
</%def>


<%def name="topbar()" filter="trim">
<section class="header">
    <div class="container">
        <nav class="navbar navbar-default navbar-static-top" role="navigation">
            <header class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse"
                        data-target=".navbar-collapse, .subnav-collapse, .sidebg-collapse">
                    <span class="sr-only">${_('Toggle navigation')}</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="${urls.ckan_url(ctx)}">
                    <%self:brand/>
                    <span class="label label-warning">pre-alpha</span>
                </a>
                <p class="navbar-text pull-right">${_('Open platform for french public data')}</p>
            </header>
        </nav>
    </div>
</section>

<section class="topmenu collapse navbar-collapse">
    <div class="container">
        <nav class="navbar navbar-default navbar-static-top" role="navigation">
            <ul class="nav navbar-nav links">
                <li>
                    <a href="${urls.ckan_url(ctx)}" title="${_('Home')}">
                        <span class="glyphicon glyphicon-home"></span>
                    </a>
                </li>
                <li><a href="//wiki.data.gouv.fr/wiki/FAQ">${_('How it works ?')}</a></li>
                <li><a href="${urls.ckan_url(ctx, 'organization')}">${_('Publishers')}</a></li>
                <li>
                    <a href="//wiki.data.gouv.fr/wiki/Licence_Ouverte_/_Open_Licence">
                        ${_('Open Licence')}
                    </a>
                </li>
                <li><a href="${urls.ckan_url(ctx, 'metrics')}">${_('Metrics')}</a></li>
                <li><a href="http://www.etalab.gouv.fr/">Etalab</a></li>
            </ul>

            <ul class="nav navbar-nav navbar-right">
                <%self:topbar_dropdown_admin/>
                <%self:topbar_user/>
                <%self:topbar_lang/>
            </ul>
        </nav>
    </div>
</section>
</%def>


<%def name="topbar_dropdown_admin()" filter="trim">
    % if model.is_admin(ctx):
        <li class="dropdown">
            <a class="dropdown-toggle" data-toggle="dropdown" href="#">${_('Administration')} <b class="caret"></b></a>
            <ul class="dropdown-menu">
                <li><a href="${model.Account.get_admin_class_url(ctx)}">${_('Accounts')}</a></li>
                <li><a href="${model.Dataset.get_admin_class_url(ctx)}">${_('Datasets')}</a></li>
                <li><a href="${model.Group.get_admin_class_url(ctx)}">${_('Groups')}</a></li>
                <li><a href="${model.Organization.get_admin_class_url(ctx)}">${_('Organizations')}</a></li>
            </ul>
        </li>
    % endif
</%def>


<%def name="topbar_user()" filter="trim">
            <ul class="nav navbar-nav navbar-right">
<%
    user = model.get_user(ctx)
%>\
    % if user is None:
                <li><a class="sign-in" href="#" title="${_(u'Sign in with Persona')}">${_(u'Sign in')}</a></li>
    % else:
##                <li class="active"><a href="${user.get_url(ctx)}"><span class="glyphicon glyphicon-user"></span> ${
##                        user.email}</a></li>
                <li class="active"><a href=""><span class="glyphicon glyphicon-user"></span> ${user.get_title(ctx)}</a></li>
                <li><a class="sign-out" href="#" title="${_(u'Sign out from Persona')}">${_(u'Sign out')}</a></li>
    % endif
            </ul>
</%def>


<%def name="topbar_lang()" filter="trim">
    <li class="dropdown language">
        <button class="btn btn-link dropdown-toggle" data-toggle="dropdown">
            <img src="${urls.static('img/flags', '{0}.png'.format(lang))}" alt="${_('Current locale flag')}" />
        </button>
        <!-- <ul class="dropdown-menu"> -->
            <!-- {% for code, name in languages.items() %}
            <li>
                <a href="{{ url(code) }}{{ current_base_location|safe }}">
                    <img src="/img/flags/{{code}}.png" alt="{{name}} flag" />
                    {{name}}
                </a>
            </li>
            {% endfor %} -->
        <!-- </ul> -->
    </li>
</%def>

<%def name="subnav()" filter="trim">
<nav class="navbar navbar-static-top navbar-subnav">
    <div class="container">
        <div class="cover-marianne"></div>
        <div class="search_bar">

            <form class="navbar-form" role="search" action="${urls.ckan_url(ctx, 'search')}">
                <div class="form-group col-sm-4 col-md-4 col-lg-3 col-xs-12">
                    <div class="input-group">
                        <div class="input-group-btn">
                            <button class="btn" type="submit"><i class="glyphicon glyphicon-search"></i></button>
                        </div>
                        <input id="search-input" name="q" type="search" class="form-control"
                            autocomplete="off" placeholder="${_('Search')}">
                    </div>
                </div>

                <div class="form-group col-sm-3 col-md-2 col-lg-3 col-xs-12 collapse subnav-collapse">
                    <div id="where-group" class="input-group">
                        <span class="input-group-addon">
                            <span class="glyphicon glyphicon-globe"></span>
                        </span>
                        <input id="where-input" type="search" class="form-control"
                            autocomplete="off" placeholder="${_('Where')}">
                        <input id="ext_territory" name="ext_territory" type="hidden" />
                    </div>
                </div>
            </form>


            <div class="form-group col-sm-3 col-md-2 col-lg-3 col-xs-12">
                <button class="dropdown-toggle btn-block btn-light" data-toggle="dropdown">
                    ${_('Topics')}
                    <span class="glyphicon glyphicon-chevron-down pull-right hidden-sm"></span>
                </button>
                <ul class="dropdown-menu" role="menu" aria-labelledby="topics">
                    % for topic in main_topics:
                    <li role="presentation">
                        <a role="menuitem" tabindex="-1" href="${ topic['url'].format(lang=lang) }">
                        ${ topic['title'] }
                        </a>
                    </li>
                    % endfor
                </ul>
            </div>

            <div class="col-sm-2 col-md-4 col-lg-3 col-xs-12 collapse subnav-collapse">
                <a class="btn btn-primary btn-dark btn-block hidden-sm btn-md icon-left"
                    title="${('Publish a dataset !')}"
                    href="${urls.ckan_url(ctx, 'dataset/new')}">
                    <span class="glyphicon glyphicon-plus"></span>
                    ${('Publish a dataset !')}
                </a>
                <a class="btn btn-primary btn-dark btn-block hidden-xs hidden-md hidden-lg"
                    title="${('Publish a dataset !')}"
                    href="${urls.ckan_url(ctx, 'dataset/new')}">
                    <span class="glyphicon glyphicon-plus"></span>
                    ${('Publish !')}
                </a>
            </div>

        </div>
    </div>
</nav>
</%def>


<%def name="trackers()" filter="trim">
</%def>


<!DOCTYPE html>
<html lang="${lang}">
<head>
    <%self:metas/>
    <title>${self.title_content()}</title>
    <%self:css/>
    <%self:feeds/>
    <%self:ie_scripts/>
</head>
<body>
    <%self:topbar/>
    <%self:subnav/>
    <%self:body_content/>
    <%self:scripts/>
    <%self:trackers/>
</body>
</html>

