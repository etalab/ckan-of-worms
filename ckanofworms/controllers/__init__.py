# -*- coding: utf-8 -*-


# CKAN-of-Worms -- A logger for errors found in CKAN datasets
# By: Emmanuel Raviart <emmanuel@raviart.com>
#
# Copyright (C) 2013 Etalab
# http://github.com/etalab/ckan-of-worms
#
# This file is part of CKAN-of-Worms.
#
# CKAN-of-Worms is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# CKAN-of-Worms is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Root controllers"""


import collections
import logging

from .. import contexts, conv, model, templates, urls, wsgihelpers
from . import accounts, datasets, groups, organizations, sessions, tags


log = logging.getLogger(__name__)
router = None


@wsgihelpers.wsgify
def api1_metrics(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'GET', req.method
    params = req.GET
    inputs = dict(
        callback = params.get('callback'),
        context = params.get('context'),
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                callback = conv.pipe(
                    conv.test_isinstance(basestring),
                    conv.cleanup_line,
                    ),
                context = conv.test_isinstance(basestring),
                ),
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            dict(
                apiVersion = '1.0',
                context = inputs['context'],
                error = dict(
                    code = 400,  # Bad Request
                    errors = [
                        dict(
                            location = key,
                            message = error,
                            )
                        for key, error in sorted(errors.iteritems())
                        ],
                    # message will be automatically defined.
                    ),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ),
            headers = headers,
            jsonp = inputs['callback'],
            )

    accounts_cursor = model.Account.get_collection().find(None, [])
    datasets_cursor = model.Dataset.get_collection().find(None, ['name', 'organization.name', 'related', 'resources',
        'weight'])
    organizations_cursor = model.Organization.get_collection().find(None, ['name', 'public_service'])
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = collections.OrderedDict((
                (u'accounts_count', accounts_cursor.count()),
                (u'datasets', collections.OrderedDict(
                    (
                        dataset_attributes['name'],
                        dict(
                            organization_name = (dataset_attributes.get('organization') or {}).get('name'),
                            related_count = len(dataset_attributes.get('related') or []),
                            resources = [
                                dict(
                                    format = resource.get('format'),
                                    )
                                for resource in (dataset_attributes.get('resources') or [])
                                ],
                            weight = dataset_attributes['weight'],
                            ),
                        )
                    for dataset_attributes in datasets_cursor
                    )),
                (u'organizations', collections.OrderedDict(
                    (
                        organization_attributes['name'],
                        dict(
                            public_service = bool(organization_attributes.get('public_service')),
                            ),
                        )
                    for organization_attributes in organizations_cursor
                    )),
                )),
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


@wsgihelpers.wsgify
def index(req):
    ctx = contexts.Ctx(req)
    return templates.render(ctx, '/index.mako')


def make_router():
    """Return a WSGI application that searches requests to controllers """
    global router
    router = urls.make_router(
        ('GET', '^/?$', index),

        (None, '^/admin/accounts(?=/|$)', accounts.route_admin_class),
        (None, '^/admin/datasets(?=/|$)', datasets.route_admin_class),
        (None, '^/admin/groups(?=/|$)', groups.route_admin_class),
        (None, '^/admin/organizations(?=/|$)', organizations.route_admin_class),
        (None, '^/admin/sessions(?=/|$)', sessions.route_admin_class),
        (None, '^/api/1/accounts(?=/|$)', accounts.route_api1_class),
        (None, '^/api/1/datasets(?=/|$)', datasets.route_api1_class),
        (None, '^/api/1/groups(?=/|$)', groups.route_api1_class),
        ('GET', '^/api/1/metrics/?$', api1_metrics),
        (None, '^/api/1/organizations(?=/|$)', organizations.route_api1_class),
        (None, '^/api/1/tags(?=/|$)', tags.route_api1_class),
        ('POST', '^/login/?$', accounts.login),
        ('POST', '^/logout/?$', accounts.logout),
        ('GET', '^/sitemap/?$', sitemap),
        )
    return router


@wsgihelpers.wsgify
def sitemap(req):
    ctx = contexts.Ctx(req)
    req.response.content_type = 'application/xml'
    return templates.render(ctx, '/sitemap.mako')
