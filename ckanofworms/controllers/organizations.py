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


"""Controllers for organizations"""


import collections
import datetime
import logging
import re

import pymongo
import webob
import webob.multidict

from .. import contexts, conv, model, paginations, templates, urls, wsgihelpers


inputs_to_organization_data = conv.struct(
    dict(
        admin = conv.pipe(
            conv.guess_bool,
            conv.default(False),
            ),
        email = conv.pipe(
            conv.input_to_email,
            conv.not_none,
            ),
        ),
    default = 'drop',
    )
log = logging.getLogger(__name__)


@wsgihelpers.wsgify
def admin_delete(req):
    ctx = contexts.Ctx(req)
    organization = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Deletion forbidden"),
            message = ctx._("You can not delete an organization."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'POST':
        organization.delete(ctx, safe = True)
        return wsgihelpers.redirect(ctx, location = model.Organization.get_admin_class_url(ctx))
    return templates.render(ctx, '/organizations/admin-delete.mako', organization = organization)


@wsgihelpers.wsgify
def admin_edit(req):
    ctx = contexts.Ctx(req)
    organization = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not edit an organization."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'GET':
        errors = None
        inputs = dict(
            admin = u'1' if organization.admin else None,
            email = organization.email,
            )
    else:
        assert req.method == 'POST'
        inputs = extract_organization_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_organization_data(inputs, state = ctx)
        if errors is None:
            if model.Organization.find(
                    dict(
                        _id = {'$ne': organization._id},
                        email = data['email'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(email = ctx._('An organization with the same email already exists.'))
        if errors is None:
            organization.set_attributes(**data)
            organization.save(ctx, safe = True)

            # View organization.
            return wsgihelpers.redirect(ctx, location = organization.get_admin_url(ctx))
    return templates.render(ctx, '/organizations/admin-edit.mako', errors = errors, inputs = inputs,
        organization = organization)


@wsgihelpers.wsgify
def admin_index(req):
    ctx = contexts.Ctx(req)
    model.is_admin(ctx, check = True)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        page = params.get('page'),
        sort = params.get('sort'),
        term = params.get('term'),
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                page = conv.pipe(
                    conv.input_to_int,
                    conv.test_greater_or_equal(1),
                    conv.default(1),
                    ),
                sort = conv.pipe(
                    conv.cleanup_line,
                    conv.test_in(['created', 'name']),
                    ),
                term = conv.input_to_name,
                ),
            ),
        conv.rename_item('page', 'page_number'),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Organization search error: {}').format(errors))

    criteria = {}
    if data['term'] is not None:
        criteria['name'] = re.compile(re.escape(data['term']))
    cursor = model.Organization.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'name':
        cursor.sort([('name', pymongo.ASCENDING)])
    elif data['sort'] == 'created':
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('name', pymongo.ASCENDING)])
    organizations = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/organizations/admin-index.mako', data = data, errors = errors, inputs = inputs,
        organizations = organizations, pager = pager)


@wsgihelpers.wsgify
def admin_view(req):
    ctx = contexts.Ctx(req)
    organization = ctx.node

    model.is_admin(ctx, check = True)

    return templates.render(ctx, '/organizations/admin-view.mako', organization = organization)


@wsgihelpers.wsgify
def api1_get(req):
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

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(ctx.node, state = ctx),
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


@wsgihelpers.wsgify
def api1_index(req):
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

    cursor = model.Organization.get_collection().find(None, [])
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = [
                organization_attributes['_id']
                for organization_attributes in cursor
                ],
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


@wsgihelpers.wsgify
def api1_set_ckan(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'POST', req.method

    inputs_converters = dict(
        # Shared secret between client and server
        api_key = conv.pipe(
            conv.test_isinstance(basestring),
            conv.input_to_token,
            conv.not_none,
            ),
        # For asynchronous calls
        context = conv.test_isinstance(basestring),
        # URL path of the form to fill out
        # "value" is handled below.
        )

    content_type = req.content_type
    if content_type is not None:
        content_type = content_type.split(';', 1)[0].strip()
    if content_type == 'application/json':
        inputs, error = conv.pipe(
            conv.make_input_to_json(),
            conv.test_isinstance(dict),
            )(req.body, state = ctx)
        if error is not None:
            return wsgihelpers.respond_json(ctx,
                collections.OrderedDict(sorted(dict(
                    apiVersion = '1.0',
                    error = collections.OrderedDict(sorted(dict(
                        code = 400,  # Bad Request
                        errors = [error],
                        message = ctx._(u'Invalid JSON in request POST body'),
                        ).iteritems())),
                    method = req.script_name,
                    params = req.body,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                headers = headers,
                )
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.ckan_organization_to_attributes,
                conv.not_none,
                ),
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.make_input_to_json(),
                conv.ckan_organization_to_attributes,
                conv.not_none,
                ),
            ))

    data, errors = conv.struct(inputs_converters)(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = inputs.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 400,  # Bad Request
                    errors = [errors],
                    message = ctx._(u'Bad parameters in request'),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    api_key = data['api_key']
    account = model.Account.find_one(
        dict(
            api_key = api_key,
            ),
        as_class = collections.OrderedDict,
        )
    if account is None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 401,  # Unauthorized
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )
    if not account.admin:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 403,  # Forbidden
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    organization_attributes = data['value']
    organization = model.Organization(**organization_attributes)
#    organization = model.Organization.find_one(organization_attributes['_id'], as_class = collections.OrderedDict)
#    if organization is None:
#        organization = model.Organization(**organization_attributes)
#    else:
#        organization = model.Organization(_id = organization._id, **organization_attributes)
    organization.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(organization, state = ctx),
            ).iteritems())),
        headers = headers,
        )


@wsgihelpers.wsgify
def api1_set_errors(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'POST', req.method

    inputs_converters = dict(
        # Shared secret between client and server
        api_key = conv.pipe(
            conv.test_isinstance(basestring),
            conv.input_to_token,
            conv.not_none,
            ),
        author = conv.pipe(
            conv.test_isinstance(basestring),
            conv.cleanup_line,
            conv.not_none,
            ),
        # For asynchronous calls
        context = conv.test_isinstance(basestring),
        draft_id = conv.pipe(
            conv.test_isinstance(basestring),
            conv.input_to_token,
            conv.not_none,
            ),
        # "value" is handled below.
        )

    content_type = req.content_type
    if content_type is not None:
        content_type = content_type.split(';', 1)[0].strip()
    if content_type == 'application/json':
        inputs, error = conv.pipe(
            conv.make_input_to_json(),
            conv.test_isinstance(dict),
            )(req.body, state = ctx)
        if error is not None:
            return wsgihelpers.respond_json(ctx,
                collections.OrderedDict(sorted(dict(
                    apiVersion = '1.0',
                    error = collections.OrderedDict(sorted(dict(
                        code = 400,  # Bad Request
                        errors = [error],
                        message = ctx._(u'Invalid JSON in request POST body'),
                        ).iteritems())),
                    method = req.script_name,
                    params = req.body,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                headers = headers,
                )
        inputs_converters.update(dict(
            value = conv.json_to_errors,
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.make_input_to_json(),
                conv.json_to_errors,
                ),
            ))

    data, errors = conv.struct(inputs_converters)(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = inputs.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 400,  # Bad Request
                    errors = [errors],
                    message = ctx._(u'Bad parameters in request'),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    api_key = data['api_key']
    account = model.Account.find_one(
        dict(
            api_key = api_key,
            ),
        as_class = collections.OrderedDict,
        )
    if account is None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 401,  # Unauthorized
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )
    if not account.admin:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 403,  # Forbidden
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    organization = ctx.node
    if organization.draft_id != data['draft_id']:
        # The modified organization is not based on the latest version of the organization.
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 409,  # Conflict
                    message = ctx._('Wrong version: {}, expected: {}').format(data['draft_id'], organization.draft_id),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    errors = organization.errors or {}
    if data['value'] is None:
        errors.pop(data['author'], None)
    else:
        errors[data['author']] = dict(
            error = data['value'],
            timestamp = datetime.datetime.utcnow().isoformat(' '),
            )
    if errors:
        organization.errors = errors
    elif organization.errors is not None:
        del organization.errors
    organization.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(organization, state = ctx),
            ).iteritems())),
        headers = headers,
        )


@wsgihelpers.wsgify
def api1_typeahead(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        q = params.get('q'),
        )
    data, errors = conv.struct(
        dict(
            q = conv.cleanup_line,
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Organization search error: {}').format(errors))

    criteria = {}
    if data['q'] is not None:
        criteria['title'] = re.compile(re.escape(data['q']))
    cursor = model.Organization.get_collection().find(criteria, ['title'])
    return wsgihelpers.respond_json(ctx,
        [
            organization_attributes['title']
            for organization_attributes in cursor.limit(10)
            ],
        headers = headers,
        )


def extract_organization_inputs_from_params(ctx, params = None):
    if params is None:
        params = webob.multidict.MultiDict()
    return dict(
        admin = params.get('admin'),
        email = params.get('email'),
        )


def route_admin(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    organization, error = conv.pipe(
        conv.input_to_token,
        conv.not_none,
        model.Organization.make_id_to_instance(),
        )(req.urlvars.get('id'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Organization Error: {}').format(error))(
            environ, start_response)

    ctx.node = organization

    router = urls.make_router(
        ('GET', '^/?$', admin_view),
#        (('GET', 'POST'), '^/delete/?$', admin_delete),
#        (('GET', 'POST'), '^/edit/?$', admin_edit),
        )
    return router(environ, start_response)


def route_admin_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', admin_index),
        (None, '^/(?P<id>[^/]+)(?=/|$)', route_admin),
        )
    return router(environ, start_response)


def route_api1(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    organization, error = conv.pipe(
        conv.input_to_token,
        conv.not_none,
        model.Organization.make_id_to_instance(),
        )(req.urlvars.get('id'), state = ctx)
    if error is not None:
        params = req.GET
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = params.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Organization Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            )(environ, start_response)

    ctx.node = organization

    router = urls.make_router(
        ('GET', '^/?$', api1_get),
        ('POST', '^/errors/?$', api1_set_errors),
        )
    return router(environ, start_response)


def route_api1_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', api1_index),
        ('POST', '^/ckan/?$', api1_set_ckan),
        ('GET', '^/typeahead/?$', api1_typeahead),
        (None, '^/(?P<id>[^/]+)(?=/|$)', route_api1),
        )
    return router(environ, start_response)
