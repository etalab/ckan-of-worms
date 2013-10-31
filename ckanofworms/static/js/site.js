/*
 * CKAN-of-Worms -- A logger for errors found in CKAN datasets
 * By: Emmanuel Raviart <emmanuel@raviart.com>
 *
 * Copyright (C) 2013 Etalab
 * http://github.com/etalab/ckan-of-worms
 *
 * This file is part of CKAN-of-Worms.
 *
 * CKAN-of-Worms is free software; you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * CKAN-of-Worms is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */


$(function() {
    $('.typeahead#group').typeahead({
        engine: Hogan,
        name: 'group',
        remote: '/api/1/groups/typeahead?q=%QUERY',
        template: [
            '<p><strong>{{title}}</strong></p>',
            '<p>{{name}}</p>',
        ].join('')
    });
    $('.typeahead#organization').typeahead({
        engine: Hogan,
        name: 'organization',
        remote: '/api/1/organizations/typeahead?q=%QUERY',
        template: [
            '<p><strong>{{title}}</strong></p>',
            '<p>{{name}}</p>',
        ].join('')
    });
    $('.typeahead#related_owner').typeahead({
        engine: Hogan,
        name: 'related_owner',
        remote: '/api/1/accounts/typeahead?q=%QUERY',
        template: [
            '<p><strong>{{fullname}}</strong> <code>&lt;{{email}}&gt;</code></p>',
            '<p>{{name}}</p>',
        ].join('')
    });
    $('.typeahead#supplier').typeahead({
        engine: Hogan,
        name: 'supplier',
        remote: '/api/1/organizations/typeahead?q=%QUERY',
        template: [
            '<p><strong>{{title}}</strong></p>',
            '<p>{{name}}</p>',
        ].join('')
    });
    $('.typeahead#tag').typeahead({
        name: 'tag',
        remote: '/api/1/tags/typeahead?q=%QUERY'
    });
});

