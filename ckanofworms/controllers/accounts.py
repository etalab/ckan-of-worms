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


"""Controllers for accounts"""


import collections
import datetime
import json
import logging
import re
import uuid

import pymongo
import requests
import webob
import webob.multidict

from .. import conf, contexts, conv, model, paginations, templates, urls, wsgihelpers


inputs_to_account_data = conv.struct(
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
    account = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Deletion forbidden"),
            message = ctx._("You can not delete an account."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'POST':
        account.delete(ctx, safe = True)
        return wsgihelpers.redirect(ctx, location = model.Account.get_admin_class_url(ctx))
    return templates.render(ctx, '/accounts/admin-delete.mako', account = account)


@wsgihelpers.wsgify
def admin_edit(req):
    ctx = contexts.Ctx(req)
    account = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not edit an account."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'GET':
        errors = None
        inputs = dict(
            admin = u'1' if account.admin else None,
            email = account.email,
            )
    else:
        assert req.method == 'POST'
        inputs = extract_account_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_account_data(inputs, state = ctx)
        if errors is None:
            if model.Account.find(
                    dict(
                        _id = {'$ne': account._id},
                        email = data['email'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(email = ctx._('An account with the same email already exists.'))
        if errors is None:
            if account.errors:
                del account.errors
            account.set_attributes(**data)
            account.save(ctx, safe = True)

            # View account.
            return wsgihelpers.redirect(ctx, location = account.get_admin_url(ctx))
    return templates.render(ctx, '/accounts/admin-edit.mako', account = account, errors = errors, inputs = inputs)


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
                term = conv.input_to_ckan_name,
                ),
            ),
        conv.rename_item('page', 'page_number'),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Account search error: {}').format(errors))

    criteria = {}
    if data['term'] is not None:
        criteria['name'] = re.compile(re.escape(data['term']))
    cursor = model.Account.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'name':
        cursor.sort([('name', pymongo.ASCENDING)])
    elif data['sort'] == 'created':
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('name', pymongo.ASCENDING)])
    accounts = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/accounts/admin-index.mako', accounts = accounts, data = data, errors = errors,
        inputs = inputs, pager = pager)


@wsgihelpers.wsgify
def admin_view(req):
    ctx = contexts.Ctx(req)
    account = ctx.node

    model.is_admin(ctx, check = True)

    return templates.render(ctx, '/accounts/admin-view.mako', account = account)


@wsgihelpers.wsgify
def api1_alert(req):
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
        # "critical", "debug", "error", "info" & "warning" arguments are handled below.
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
            critical = conv.json_to_errors,
            debug = conv.json_to_errors,
            error = conv.json_to_errors,
            info = conv.json_to_errors,
            warning = conv.json_to_errors,
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            critical = conv.pipe(
                conv.make_input_to_json(),
                conv.json_to_errors,
                ),
            debug = conv.pipe(
                conv.make_input_to_json(),
                conv.json_to_errors,
                ),
            error = conv.pipe(
                conv.make_input_to_json(),
                conv.json_to_errors,
                ),
            info = conv.pipe(
                conv.make_input_to_json(),
                conv.json_to_errors,
                ),
            warning = conv.pipe(
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
                    message = ctx._('Non-admin API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    account = ctx.node
    if account.draft_id != data['draft_id']:
        # The modified account is not based on the latest version of the account.
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 409,  # Conflict
                    message = ctx._('Wrong version: {}, expected: {}').format(data['draft_id'], account.draft_id),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    alerts = account.alerts or {}
    now_str = datetime.datetime.utcnow().isoformat(' ')
    for level in ('critical', 'debug', 'error', 'info', 'warning'):
        level_data = data[level]
        if level_data is None:
            level_alerts = alerts.get(level)
            if level_alerts is not None:
                level_alerts.pop(data['author'], None)
                if not level_alerts:
                    del alerts[level]
        else:
            alerts.setdefault(level, {})[data['author']] = dict(
                error = level_data,
                timestamp = now_str,
                )
    if alerts:
        account.alerts = alerts
    elif account.alerts is not None:
        del account.alerts
    account.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(account, state = ctx),
            ).iteritems())),
        headers = headers,
        )


@wsgihelpers.wsgify
def api1_delete(req):
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'DELETE', req.method

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
                        message = ctx._(u'Invalid JSON in request DELETE body'),
                        ).iteritems())),
                    method = req.script_name,
                    params = req.body,
                    url = req.url.decode('utf-8'),
                    ).iteritems())),
                headers = headers,
                )
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)

    data, errors = conv.struct(
        dict(
            # Shared secret between client and server
            api_key = conv.pipe(
                conv.test_isinstance(basestring),
                conv.input_to_token,
                conv.not_none,
                ),
            # For asynchronous calls
            context = conv.test_isinstance(basestring),
            ),
        )(inputs, state = ctx)
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
                    message = ctx._('Non-admin API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    deleted_value = conv.check(conv.method('turn_to_json'))(ctx.node, state = ctx)
    ctx.node.delete(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = deleted_value,
            ).iteritems())),
        headers = headers,
        )


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

    cursor = model.Account.get_collection().find(None, [])
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = [
                account_attributes['_id']
                for account_attributes in cursor
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
                conv.ckan_user_to_account_attributes,
                conv.not_none,
                ),
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.make_input_to_json(),
                conv.ckan_user_to_account_attributes,
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
                    message = ctx._('Non-admin API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    account_attributes = data['value']
    existing_account = model.Account.find_one(account_attributes['_id'], as_class = collections.OrderedDict)
    account = model.Account(**account_attributes)
    if existing_account is not None:
        # Keep existing attributes that are not part of this CKAN object.
        if existing_account.admin:
            account.admin = existing_account.admin
        if existing_account.api_key:
            account.api_key = existing_account.api_key
    account.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(account, state = ctx),
            ).iteritems())),
        headers = headers,
        )


def extract_account_inputs_from_params(ctx, params = None):
    if params is None:
        params = webob.multidict.MultiDict()
    return dict(
        admin = params.get('admin'),
        email = params.get('email'),
        )


@wsgihelpers.wsgify
def login(req):
    """Authorization request"""
    ctx = contexts.Ctx(req)

    assert req.method == 'POST'
    params = req.POST
    inputs = dict(
        assertion = params.get('assertion'),
        )
    data, errors = conv.struct(
        dict(
            assertion = conv.pipe(
                conv.cleanup_line,
                conv.not_none,
                ),
            ),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.bad_request(ctx, explanation = ctx._(u'Login Error: {0}').format(errors))

    response = requests.post('https://verifier.login.persona.org/verify',
        data = dict(
            audience = urls.get_full_url(ctx),
            assertion = data['assertion'],
            ),
        verify = True,
        )
    if not response.ok:
        return wsgihelpers.internal_error(ctx,
            dump = response.text,
            explanation = ctx._(u'Error while verifying authentication assertion'),
            )
    verification_data = json.loads(response.content)
    # Check if the assertion was valid.
    if verification_data['status'] != 'okay':
        return wsgihelpers.internal_error(ctx,
            dump = response.text,
            explanation = ctx._(u'Error while verifying authentication assertion'),
            )

    user = model.Account.find_one(
        dict(
            email = verification_data['email'],
            ),
        as_class = collections.OrderedDict,
        )
    if user is None:
        user = model.Account()
        user._id = unicode(uuid.uuid4())
        user.api_key = unicode(uuid.uuid4())
        user.email = verification_data['email']
        user.save(ctx, safe = True)
    ctx.user = user

    session = ctx.session
    if session is None:
        ctx.session = session = model.Session()
        session.token = unicode(uuid.uuid4())
    session.expiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 4)
    session.user_id = user._id
    session.save(ctx, safe = True)

    if req.cookies.get(conf['cookie']) != session.token:
        req.response.set_cookie(conf['cookie'], session.token, httponly = True, secure = req.scheme == 'https')
    return 'Login succeeded.'


@wsgihelpers.wsgify
def logout(req):
    ctx = contexts.Ctx(req)

    assert req.method == 'POST'

    session = ctx.session
    if session is not None:
        session.expiration = datetime.datetime.utcnow() + datetime.timedelta(hours = 4)
        if session.user_id is not None:
            del session.user_id
        session.save(ctx, safe = True)
        if req.cookies.get(conf['cookie']) != session.token:
            req.response.set_cookie(conf['cookie'], session.token, httponly = True, secure = req.scheme == 'https')
    return 'Logout succeeded.'

#    session = ctx.session
#    if session is not None:
#        session.delete(ctx, safe = True)
#        ctx.session = None
#        if req.cookies.get(conf['cookie']) is not None:
#            req.req.response.delete_cookie(conf['cookie'])
#    return 'Logout succeeded.'


def route_admin(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    account, error = conv.pipe(
        conv.input_to_ckan_name,
        conv.not_none,
        model.Account.make_id_or_name_to_instance(),
        )(req.urlvars.get('id_or_name'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Account Error: {}').format(error))(
            environ, start_response)

    ctx.node = account

    router = urls.make_router(
        ('GET', '^/?$', admin_view),
        (('GET', 'POST'), '^/delete/?$', admin_delete),
        (('GET', 'POST'), '^/edit/?$', admin_edit),
        )
    return router(environ, start_response)


def route_admin_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', admin_index),
        (None, '^/(?P<id_or_name>[^/]+)(?=/|$)', route_admin),
        )
    return router(environ, start_response)


def route_api1(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    account, error = conv.pipe(
        conv.input_to_ckan_name,
        conv.not_none,
        model.Account.make_id_or_name_to_instance(),
        )(req.urlvars.get('id_or_name'), state = ctx)
    if error is not None:
        params = req.GET
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = params.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Account Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            )(environ, start_response)

    ctx.node = account

    router = urls.make_router(
        ('DELETE', '^/?$', api1_delete),
        ('GET', '^/?$', api1_get),
        ('POST', '^/alert/?$', api1_alert),
        )
    return router(environ, start_response)


def route_api1_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', api1_index),
        ('POST', '^/ckan/?$', api1_set_ckan),
        (None, '^/(?P<id_or_name>[^/]+)(?=/|$)', route_api1),
        )
    return router(environ, start_response)
