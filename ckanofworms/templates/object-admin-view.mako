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
def extract_item_alerts(container_alerts, key):
    item_alerts = {}
    for level, level_alerts in container_alerts.iteritems():
        for author, author_alerts in level_alerts.iteritems():
            error = author_alerts['error'].pop(unicode(key), None)
            if error:
                item_alerts.setdefault(level, {})[author] = dict(
                    error = error,
                    timestamp = author_alerts['timestamp'],
                    )
    return item_alerts
%>


<%inherit file="/site.mako"/>


<%def name="field_alerts(alerts)" filter="trim">
    % for level in ('critical', 'error', 'warning', 'info', 'debug'):
<%
        level_alerts = alerts.get(level) or {}
        level_class_suffix = dict(
            critical = 'danger',
            debug = 'info',
            error = 'danger',
            info = 'info',
            warning = 'warning',
            )[level]
%>\
        % for author, author_alerts in sorted(level_alerts.iteritems()):
            % if author_alerts['error']:
        <div class="row">
            <div class="alert alert-${level_class_suffix} col-sm-offset-2 col-sm-10">
                % if level == 'critical':
                <span class="glyphicon glyphicon-warning-sign"></span>
                % endif
                ${author_alerts['error']}
                <small>${
                markupsafe.Markup(_(u"(signaled by <em>{0}</em>, {1})")).format(author,
                    author_alerts['timestamp'].split(' ')[0])
                }</small>
            </div>
        </div>
            % endif
        % endfor
    % endfor
</%def>

