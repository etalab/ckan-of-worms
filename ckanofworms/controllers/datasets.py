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


"""Controllers for datasets"""


import collections
import datetime
import logging
import re

import pymongo
import webob
import webob.multidict

from .. import contexts, conv, model, paginations, templates, urls, wsgihelpers


inputs_to_dataset_data = conv.struct(
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
N_ = lambda message: message


@wsgihelpers.wsgify
def admin_delete(req):
    ctx = contexts.Ctx(req)
    dataset = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Deletion forbidden"),
            message = ctx._("You can not delete a dataset."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'POST':
        dataset.delete(ctx, safe = True)
        return wsgihelpers.redirect(ctx, location = model.Dataset.get_admin_class_url(ctx))
    return templates.render(ctx, '/datasets/admin-delete.mako', dataset = dataset)


@wsgihelpers.wsgify
def admin_edit(req):
    ctx = contexts.Ctx(req)
    dataset = ctx.node

    if not model.is_admin(ctx):
        return wsgihelpers.forbidden(ctx,
            explanation = ctx._("Edition forbidden"),
            message = ctx._("You can not edit a dataset."),
            title = ctx._('Operation denied'),
            )

    if req.method == 'GET':
        errors = None
        inputs = dict(
            admin = u'1' if dataset.admin else None,
            email = dataset.email,
            )
    else:
        assert req.method == 'POST'
        inputs = extract_dataset_inputs_from_params(ctx, req.POST)
        data, errors = inputs_to_dataset_data(inputs, state = ctx)
        if errors is None:
            if model.Dataset.find(
                    dict(
                        _id = {'$ne': dataset._id},
                        email = data['email'],
                        ),
                    as_class = collections.OrderedDict,
                    ).count() > 0:
                errors = dict(email = ctx._('A dataset with the same email already exists.'))
        if errors is None:
            if dataset.alerts:
                del dataset.alerts
            dataset.set_attributes(**data)
            dataset.compute_weight()
            dataset.compute_timestamp()
            dataset.save(ctx, safe = True)

            # View dataset.
            return wsgihelpers.redirect(ctx, location = dataset.get_admin_url(ctx))
    return templates.render(ctx, '/datasets/admin-edit.mako', dataset = dataset, errors = errors, inputs = inputs)


@wsgihelpers.wsgify
def admin_index(req):
    ctx = contexts.Ctx(req)
#    model.is_admin(ctx, check = True)

    assert req.method == 'GET'
    params = req.GET
    inputs = dict(
        advanced_search = params.get('advanced_search'),
        alerts = params.get('alerts'),
        group = params.get('group'),
        organization = params.get('organization'),
        page = params.get('page'),
        related = params.get('related'),
        sort = params.get('sort'),
        supplier = params.get('supplier'),
        tag = params.get('tag'),
        term = params.get('term'),
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                advanced_search = conv.guess_bool,
                alerts = conv.pipe(
                    conv.input_to_slug,
                    conv.test_in(['critical', 'debug', 'error', 'info', 'warning']),
                    ),
                group = conv.pipe(
                    conv.cleanup_line,
                    model.Group.make_title_to_instance(),
                    ),
                organization = conv.pipe(
                    conv.cleanup_line,
                    model.Organization.make_title_to_instance(),
                    ),
                page = conv.pipe(
                    conv.input_to_int,
                    conv.test_greater_or_equal(1),
                    conv.default(1),
                    ),
                related = conv.guess_bool,
                sort = conv.pipe(
                    conv.cleanup_line,
                    conv.test_in(['metadata_created', 'name', 'timestamp']),
                    ),
                supplier = conv.pipe(
                    conv.cleanup_line,
                    model.Organization.make_title_to_instance(),
                    ),
                tag = conv.input_to_ckan_tag_name,
                term = conv.input_to_ckan_name,
                ),
            ),
        conv.rename_item('page', 'page_number'),
        )(inputs, state = ctx)
    if errors is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Dataset search error: {}').format(errors))

    criteria = {}
    if data['alerts'] == 'debug':
        criteria['alerts'] = {'$exists': True}
    elif data['alerts'] == 'info':
        criteria['$or'] = [
            {'alerts.critical': {'$exists': True}},
            {'alerts.error': {'$exists': True}},
            {'alerts.info': {'$exists': True}},
            {'alerts.warning': {'$exists': True}},
            ]
    elif data['alerts'] == 'warning':
        criteria['$or'] = [
            {'alerts.critical': {'$exists': True}},
            {'alerts.error': {'$exists': True}},
            {'alerts.warning': {'$exists': True}},
            ]
    elif data['alerts'] == 'error':
        criteria['$or'] = [
            {'alerts.critical': {'$exists': True}},
            {'alerts.error': {'$exists': True}},
            ]
    elif data['alerts'] == 'critical':
        criteria['alerts.critical'] = {'$exists': True}
    if data['group'] is not None:
        criteria['groups.id'] = data['group']._id
    if data['organization'] is not None:
        criteria['owner_org'] = data['organization']._id
    if data['supplier'] is not None:
        criteria['supplier_id'] = data['supplier']._id
    if data['related'] is not None:
        criteria['related'] = {'$exists': data['related']}
    if data['tag'] is not None:
        criteria['tags.name'] = re.compile(re.escape(data['tag']))
    if data['term'] is not None:
        criteria['name'] = re.compile(re.escape(data['term']))
    cursor = model.Dataset.find(criteria, as_class = collections.OrderedDict)
    pager = paginations.Pager(item_count = cursor.count(), page_number = data['page_number'])
    if data['sort'] == 'name':
        cursor.sort([('name', pymongo.ASCENDING)])
    elif data['sort'] in ('metadata_created', 'timestamp'):
        cursor.sort([(data['sort'], pymongo.DESCENDING), ('name', pymongo.ASCENDING)])
    datasets = cursor.skip(pager.first_item_index or 0).limit(pager.page_size)
    return templates.render(ctx, '/datasets/admin-index.mako', data = data, datasets = datasets, errors = errors,
        inputs = inputs, pager = pager)


@wsgihelpers.wsgify
def admin_publish(req):
    ctx = contexts.Ctx(req)
    dataset = ctx.node

    model.is_admin(ctx, check = True)

    bson = dataset.to_bson()
    dataset.after_upsert(ctx, bson, bson)

    return wsgihelpers.redirect(ctx, location = dataset.get_admin_url(ctx))


@wsgihelpers.wsgify
def admin_stats(req):
    ctx = contexts.Ctx(req)
    dataset = ctx.node

#    model.is_admin(ctx, check = True)

    return templates.render(ctx, '/datasets/admin-stats.mako', dataset = dataset)


@wsgihelpers.wsgify
def admin_view(req):
    ctx = contexts.Ctx(req)
    dataset = ctx.node

#    model.is_admin(ctx, check = True)

    return templates.render(ctx, '/datasets/admin-view.mako', dataset = dataset)


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

    dataset = ctx.node
    if dataset.draft_id != data['draft_id']:
        # The modified dataset is not based on the latest version of the dataset.
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 409,  # Conflict
                    message = ctx._('Wrong version: {}, expected: {}').format(data['draft_id'], dataset.draft_id),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    alerts = dataset.alerts or {}
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
        dataset.alerts = alerts
    elif dataset.alerts is not None:
        del dataset.alerts
    # Don't update weight, because it doesn't depend from alerts (yet).
    # dataset.compute_weight()
    # Don't update timestamp, because it doesn't depend from alerts.
    # dataset.compute_timestamp()
    dataset.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(dataset, state = ctx),
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

    dataset = ctx.node
    deleted_value = conv.check(conv.method('turn_to_json'))(dataset, state = ctx)
    dataset.delete(ctx, safe = True)

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
def api1_delete_related(req):
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

    related_id, error = conv.pipe(
        conv.input_to_token,
        conv.not_none,
        )(req.urlvars.get('id'), state = ctx)
    if error is None:
        dataset = model.Dataset.find_one({'related.id': related_id}, as_class = collections.OrderedDict)
        if dataset is None:
            error = ctx._(u'No dataset containing a related link with ID {0}').format(related_id)
        else:
            for related_index, related_link in enumerate(dataset.related or []):
                if related_id == related_link['id']:
                    del dataset.related[related_index]
                    if not dataset.related:
                        del dataset.related
                    break
            else:
                error = ctx._(u'No related link with ID {0}').format(related_id)
    if error is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Related Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    if dataset.alerts:
        del dataset.alerts
    dataset.compute_weight()
    dataset.compute_timestamp()
    dataset.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = related_link,
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
        related = params.get('related'),
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                callback = conv.pipe(
                    conv.test_isinstance(basestring),
                    conv.cleanup_line,
                    ),
                context = conv.test_isinstance(basestring),
                related = conv.guess_bool,
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

    criteria = {}
    if data['related'] is not None:
        criteria['related'] = {'$exists': data['related']}
    cursor = model.Dataset.get_collection().find(criteria, [])
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = [
                dataset_attributes['_id']
                for dataset_attributes in cursor
                ],
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


@wsgihelpers.wsgify
def api1_ranking(req):
    """Return a JSON object describing the various scores of a datasets (alerts, weights)."""
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

    dataset = ctx.node
    ranking = dict(
        id = dataset._id,
        name = dataset.name,
        title = dataset.title,
        weight = dataset.weight,
        )
    for level, level_alerts in (dataset.alerts or {}).iteritems():
        ranking[level] = sum(
            len(author_alerts['error'])
            for author_alerts in level_alerts.itervalues()
            )

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = ranking,
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


@wsgihelpers.wsgify
def api1_related(req):
    """Controller created for Epita application"""
    ctx = contexts.Ctx(req)
    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

    assert req.method == 'GET', req.method
    params = req.GET
    inputs = dict(
        callback = params.get('callback'),
        context = params.get('context'),
        territory = params.getall('territory')
        )
    data, errors = conv.pipe(
        conv.struct(
            dict(
                callback = conv.pipe(
                    conv.test_isinstance(basestring),
                    conv.cleanup_line,
                    ),
                context = conv.test_isinstance(basestring),
                territory = conv.uniform_sequence(
                    conv.pipe(
                        conv.test_isinstance(basestring),
                        conv.cleanup_line,
                        conv.test(lambda s: s.count(u'/') == 1, error = N_(u'Territory must have the form "kind/code"'))
                        ),
                    drop_none_items = True,
                    ),
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

    criteria = dict(
        related = {'$exists': True},
        )
    if data['territory']:
        criteria['territorial_coverage'] = {'$in': data['territory']}
    cursor = model.Dataset.find(criteria, as_class = collections.OrderedDict)
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = [
                conv.check(conv.method('turn_to_json'))(dataset, state = ctx)
                for dataset in cursor
                ],
            ).iteritems())),
        headers = headers,
        jsonp = data['callback'],
        )


#@wsgihelpers.wsgify
#def api1_set(req):
#    ctx = contexts.Ctx(req)
#    headers = wsgihelpers.handle_cross_origin_resource_sharing(ctx)

#    assert req.method == 'POST', req.method

#    inputs_converters = dict(
#        # Shared secret between client and server
#        api_key = conv.pipe(
#            conv.test_isinstance(basestring),
#            conv.input_to_token,
#            conv.not_none,
#            ),
#        # For asynchronous calls
#        context = conv.test_isinstance(basestring),
#        )

#    content_type = req.content_type
#    if content_type is not None:
#        content_type = content_type.split(';', 1)[0].strip()
#    if content_type == 'application/json':
#        inputs, error = conv.pipe(
#            conv.make_input_to_json(),
#            conv.test_isinstance(dict),
#            )(req.body, state = ctx)
#        if error is not None:
#            return wsgihelpers.respond_json(ctx,
#                collections.OrderedDict(sorted(dict(
#                    apiVersion = '1.0',
#                    error = collections.OrderedDict(sorted(dict(
#                        code = 400,  # Bad Request
#                        errors = [error],
#                        message = ctx._(u'Invalid JSON in request POST body'),
#                        ).iteritems())),
#                    method = req.script_name,
#                    params = req.body,
#                    url = req.url.decode('utf-8'),
#                    ).iteritems())),
#                headers = headers,
#                )
#        inputs_converters.update(dict(
#            value = conv.pipe(
#                conv.json_to_dataset_attributes,
#                conv.not_none,
#                ),
#            ))
#    else:
#        # URL-encoded POST.
#        inputs = dict(req.POST)
#        inputs_converters.update(dict(
#            value = conv.pipe(
#                conv.make_input_to_json(),
#                conv.json_to_dataset_attributes,
#                conv.not_none,
#                ),
#            ))

#    data, errors = conv.struct(inputs_converters)(inputs, state = ctx)
#    if errors is not None:
#        return wsgihelpers.respond_json(ctx,
#            collections.OrderedDict(sorted(dict(
#                apiVersion = '1.0',
#                context = inputs.get('context'),
#                error = collections.OrderedDict(sorted(dict(
#                    code = 400,  # Bad Request
#                    errors = [errors],
#                    message = ctx._(u'Bad parameters in request'),
#                    ).iteritems())),
#                method = req.script_name,
#                params = inputs,
#                url = req.url.decode('utf-8'),
#                ).iteritems())),
#            headers = headers,
#            )

#    api_key = data['api_key']
#    account = model.Account.find_one(
#        dict(
#            api_key = api_key,
#            ),
#        as_class = collections.OrderedDict,
#        )
#    if account is None:
#        return wsgihelpers.respond_json(ctx,
#            collections.OrderedDict(sorted(dict(
#                apiVersion = '1.0',
#                context = data['context'],
#                error = collections.OrderedDict(sorted(dict(
#                    code = 401,  # Unauthorized
#                    message = ctx._('Unknown API Key: {}').format(api_key),
#                    ).iteritems())),
#                method = req.script_name,
#                params = inputs,
#                url = req.url.decode('utf-8'),
#                ).iteritems())),
#            headers = headers,
#            )
#    # TODO: Handle account rights.

#    dataset_attributes = data['value']
#    dataset = model.Dataset.find_one(dataset_attributes['_id'], as_class = collections.OrderedDict)
#    if dataset is not None and dataset.draft_id != dataset_attributes.get('draft_id'):
#        # The modified dataset is not based on the latest version of the dataset.
#        return wsgihelpers.respond_json(ctx,
#            collections.OrderedDict(sorted(dict(
#                apiVersion = '1.0',
#                context = data['context'],
#                error = collections.OrderedDict(sorted(dict(
#                    code = 409,  # Conflict
#                    message = ctx._('Wrong version: {}, expected: {}').format(dataset_attributes.get('draft_id'),
#                        dataset.draft_id),
#                    ).iteritems())),
#                method = req.script_name,
#                params = inputs,
#                url = req.url.decode('utf-8'),
#                value = conv.check(conv.method('turn_to_json'))(dataset, state = ctx),
#                ).iteritems())),
#            headers = headers,
#            )
#    dataset = model.Dataset(**dataset_attributes)
#    if dataset.alerts:
#        del dataset.alerts
#    dataset.compute_weight()
#    dataset.compute_timestamp()
#    dataset.save(ctx, safe = True)

#    return wsgihelpers.respond_json(ctx,
#        collections.OrderedDict(sorted(dict(
#            apiVersion = '1.0',
#            context = data['context'],
#            method = req.script_name,
#            params = inputs,
#            url = req.url.decode('utf-8'),
#            value = conv.check(conv.method('turn_to_json'))(dataset, state = ctx),
#            ).iteritems())),
#        headers = headers,
#        )


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
                conv.ckan_package_to_dataset_attributes,
                conv.not_none,
                ),
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.make_input_to_json(),
                conv.ckan_package_to_dataset_attributes,
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

    dataset_attributes = data['value']
    # Retrieve existing dataset when it exists, to ensure that its related links are not lost.
    existing_dataset = model.Dataset.find_one(dataset_attributes['_id'], as_class = collections.OrderedDict)
    dataset = model.Dataset(**dataset_attributes)
    if existing_dataset is not None and existing_dataset.related is not None:
        # Keep existing attributes that are not part of this CKAN object.
        dataset.related = existing_dataset.related
    dataset.compute_weight()
    dataset.compute_timestamp()
    dataset.save(ctx, safe = True)

    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = conv.check(conv.method('turn_to_json'))(dataset, state = ctx),
            ).iteritems())),
        headers = headers,
        )


@wsgihelpers.wsgify
def api1_set_ckan_related(req):
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
                conv.make_ckan_json_to_related(drop_none_values = True),
                conv.not_none,
                ),
            ))
    else:
        # URL-encoded POST.
        inputs = dict(req.POST)
        inputs_converters.update(dict(
            value = conv.pipe(
                conv.make_input_to_json(),
                conv.make_ckan_json_to_related(drop_none_values = True),
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

    related = data['value']
    dataset, error = conv.pipe(
        conv.input_to_ckan_name,
        conv.not_none,
        model.Dataset.make_id_or_name_to_instance(),
        )(related.get('dataset_id'), state = ctx)
    if error is not None:
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = data['context'],
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Dataset Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                params = inputs,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            headers = headers,
            )

    related.pop('dataset_id')
    if dataset.related is None:
        dataset.related = []
    for related_index, related_link in enumerate(dataset.related):
        if related['id'] == related_link['id']:
            dataset.related[related_index] = related
            break
    else:
        dataset.related.append(related)

    if dataset.alerts:
        del dataset.alerts
    dataset.compute_weight()
    dataset.compute_timestamp()
    dataset.save(ctx, safe = True)

    related['dataset_id'] = dataset._id
    return wsgihelpers.respond_json(ctx,
        collections.OrderedDict(sorted(dict(
            apiVersion = '1.0',
            context = data['context'],
            method = req.script_name,
            params = inputs,
            url = req.url.decode('utf-8'),
            value = related,
            ).iteritems())),
        headers = headers,
        )


def extract_dataset_inputs_from_params(ctx, params = None):
    if params is None:
        params = webob.multidict.MultiDict()
    return dict(
        admin = params.get('admin'),
        email = params.get('email'),
        )


def route_admin(environ, start_response):
    req = webob.Request(environ)
    ctx = contexts.Ctx(req)

    dataset, error = conv.pipe(
        conv.input_to_ckan_name,
        conv.not_none,
        model.Dataset.make_id_or_name_to_instance(),
        )(req.urlvars.get('id_or_name'), state = ctx)
    if error is not None:
        return wsgihelpers.not_found(ctx, explanation = ctx._('Dataset Error: {}').format(error))(
            environ, start_response)

    ctx.node = dataset

    router = urls.make_router(
        ('GET', '^/?$', admin_view),
#        (('GET', 'POST'), '^/delete/?$', admin_delete),
#        (('GET', 'POST'), '^/edit/?$', admin_edit),
        ('GET', '^/publish/?$', admin_publish),
        ('GET', '^/stats/?$', admin_stats),
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

    dataset, error = conv.pipe(
        conv.input_to_ckan_name,
        conv.not_none,
        model.Dataset.make_id_or_name_to_instance(),
        )(req.urlvars.get('id_or_name'), state = ctx)
    if error is not None:
        params = req.GET
        return wsgihelpers.respond_json(ctx,
            collections.OrderedDict(sorted(dict(
                apiVersion = '1.0',
                context = params.get('context'),
                error = collections.OrderedDict(sorted(dict(
                    code = 404,  # Not Found
                    message = ctx._('Dataset Error: {}').format(error),
                    ).iteritems())),
                method = req.script_name,
                url = req.url.decode('utf-8'),
                ).iteritems())),
            )(environ, start_response)

    ctx.node = dataset

    router = urls.make_router(
        ('DELETE', '^/?$', api1_delete),
        ('GET', '^/?$', api1_get),
        ('POST', '^/alert/?$', api1_alert),
        ('GET', '^/ranking/?$', api1_ranking),
        )
    return router(environ, start_response)


def route_api1_class(environ, start_response):
    router = urls.make_router(
        ('GET', '^/?$', api1_index),
#        ('POST', '^/?$', api1_set),
        ('POST', '^/ckan/?$', api1_set_ckan),
        ('POST', '^/ckan/related/?$', api1_set_ckan_related),
        ('GET', '^/related/?$', api1_related),
        ('DELETE', '^/related/(?P<id>[^/]+)/?$', api1_delete_related),
        (None, '^/(?P<id_or_name>[^/]+)(?=/|$)', route_api1),
        )
    return router(environ, start_response)
