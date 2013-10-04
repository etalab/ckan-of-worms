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
def extract_item_errors(container_errors, key):
    item_errors = {}
    for author, author_errors in container_errors.iteritems():
        error = author_errors['error'].pop(unicode(key), None)
        if error:
            item_errors[author] = dict(
                error = error,
                timestamp = author_errors['timestamp']
                )
    return item_errors
%>


<%inherit file="/site.mako"/>


<%def name="field_error(errors)" filter="trim">
    % for author, author_errors in sorted(errors.iteritems()):
        % if author_errors['error']:
        <div class="row">
            <div class="alert alert-danger col-sm-offset-2 col-sm-10">${author_errors['error']} <small>${
                markupsafe.Markup(_(u"(signaled by <em>{0}</em>, {1})")).format(author,
                    author_errors['timestamp'].split('T')[0])
                }</small></div>
        </div>
        % endif
    % endfor
</%def>

