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


"""Controllers for related links"""


import collections
import logging

import webob
import webob.multidict

from .. import contexts, conv, model, paginations, templates, urls, wsgihelpers


inputs_to_related_link_data = conv.struct(
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
    related_link = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Deletion forbidden"),
            message = ctx._("You can not delete a related link."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'POST':
        related_link.delete(ctx, safe = True)
        return wsgihelpers.redirect(ctx, location = model.RelatedLink.get_admin_class_url(ctx))
    return templates.render(ctx, '/related-links/admin-delete.mako', related_link = related_link)


@wsgihelpers.wsgify
def admin_edit(req):
    ctx = contexts.Ctx(req)
    related_link = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not edit a related link."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'GET':
        errors = None
        inputs = dict(
            admin = u'1' if related_link.admin else None,
            email = related_link.email,
            )
    else:
        assert req.method == 'POST'
        inputs = extract_related_link_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_related_link_data(inputs, state = ctx)
        if errors is None:
            if model.RelatedLink.find(
                    dict(
                        _id = {'$ne': related_link._id},
                        email = data['email'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(email = ctx._('A related link with the same email already exists.'))
        if errors is None:
            related_link.set_attributes(**data)
            related_link.save(ctx, safe = True)

            # View related link.
            return wsgihelpers.redirect(ctx, location = related_link.get_admin_url(ctx))
    return templates.render(ctx, '/related-links/admin-edit.mako', errors = errors, inputs = inputs,
        related_link = related_link)


@wsgihelpers.wsgify
def admin_index(req):
    ctx = contexts.Ctx(req)
    model.is_admin(ctx, check = True)

    assert req.method == 'GET'
    page_number, error = conv.pipe(
        conv.input_to_int,
        conv.test_greater_or_equal(1),
        conv.default(1),
        )(req.params.get('page'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Page number error: {}').format(error))

    cursor = model.RelatedLink.find(as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = page_number)
    related_links = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/related-links/admin-index.mako', pager = pager, related_links = related_links)


@wsgihelpers.wsgify
def admin_view(req):
    ctx = contexts.Ctx(req)
    related_link = ctx.node

    model.is_admin(ctx, check = True)

    return templates.render(ctx, '/related-links/admin-view.mako', related_link = related_link)


@wsgihelpers.wsgify
def api1_set(req):
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
                conv.json_to_related_link_attributes,
                conv.not_none,
                ),
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.make_input_to_json(),
                conv.json_to_related_link_attributes,
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
                    code = 404,  # Not Found
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    related_link_attributes = data['value']
    related_link = model.RelatedLink.find_one(related_link_attributes['_id'], as_class = collections.OrderedDict)
    if related_link is not None and related_link.draft_id != related_link_attributes.get('draft_id'):
        # The modified related link is not based on the latest version of the related link.
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 409,  # Conflict
                    message = ctx._('Wrong version: {}, expected: {}').format(related_link_attributes.get('draft_id'),
                        related_link.draft_id),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                value = conv.check(conv.method('turn_to_json'))(related_link, state = ctx),
                ).iteritems())),
            headers = headers,
            )
    related_link = model.RelatedLink(**related_link_attributes)
    related_link.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(related_link, state = ctx),
            ).iteritems())),
        headers = headers,
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
                conv.ckan_package_to_related_link_attributes,
                conv.not_none,
                ),
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.make_input_to_json(),
                conv.ckan_package_to_related_link_attributes,
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
                    code = 404,  # Not Found
                    message = ctx._('Unknown API Key: {}').format(api_key),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    related_link_attributes = data['value']
    related_link = model.RelatedLink(**related_link_attributes)
#    related_link = model.RelatedLink.find_one(related_link_attributes['_id'], as_class = collections.OrderedDict)
#    if related_link is None:
#        related_link = model.RelatedLink(**related_link_attributes)
#    else:
#        related_link = model.RelatedLink(_id = related_link._id, **related_link_attributes)
    related_link.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(related_link, state = ctx),
            ).iteritems())),
        headers = headers,
        )


def extract_related_link_inputs_from_params(ctx, params = None):
    if params is None:
        params = webob.multidict.MultiDict()
    return dict(
        admin = params.get('admin'),
        email = params.get('email'),
        )


def route_admin(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    related_link, error = conv.pipe(
        conv.input_to_token,
        conv.not_none,
        model.RelatedLink.make_id_to_instance(),
        )(req.urlvars.get('id'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Related Link Error: {}').format(error))(
            environ, start_response)

    ctx.node = related_link

    router = urls.make_router(
        ('GET', '^/?$', admin_view),
        (('GET', 'POST'), '^/delete/?$', admin_delete),
        (('GET', 'POST'), '^/edit/?$', admin_edit),
        )
    return router(environ, start_response)


def route_admin_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', admin_index),
        (None, '^/(?P<id>[^/]+)(?=/|$)', route_admin),
        )
    return router(environ, start_response)


#def route_api1(environ, start_response):
#    req = webob.Request(environ)
#    ctx = contexts.Ctx(req)

#    related_link, error = conv.pipe(
#        conv.input_to_token,
#        conv.not_none,
#        model.RelatedLink.make_name_to_instance(),
#        )(req.urlvars.get('name'), state = ctx)
#    if error is not None:
#        return wsgihelpers.not_found(ctx, explanation = ctx._('Related Link Error: {}').format(error))(
#            environ, start_response)

#    ctx.node = related_link

#    router = urls.make_router(
##        ('GET', '^/?$', api1_get),
##        (('GET', 'POST'), '^/delete/?$', api1_delete),
##        (('GET', 'POST'), '^/edit/?$', api1_update),
#        )
#    return router(environ, start_response)


def route_api1_class(environ, start_response):
    router = urls.make_router(
#        ('GET', '^/?$', api1_index),
        ('POST', '^/?$', api1_set),
        ('POST', '^/ckan/?$', api1_set_ckan),
#        (None, '^/(?P<name>[^/]+)(?=/|$)', route_api1),
        )
    return router(environ, start_response)
