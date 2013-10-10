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


"""Conversion functions"""


from biryani1.baseconv import *
from biryani1.bsonconv import *
from biryani1.datetimeconv import *
from biryani1.objectconv import *
from biryani1.jsonconv import *
from biryani1.states import default_state, State
from ckantoolbox.ckanconv import *

from . import texthelpers


ckan_group_to_attributes = pipe(
    make_ckan_json_to_group(drop_none_values = 'missing'),
    rename_item('id', '_id'),
    )


ckan_organization_to_attributes = pipe(
    make_ckan_json_to_organization(drop_none_values = 'missing'),
    rename_item('id', '_id'),
    )


def ckan_package_to_dataset_attributes(value, state = None):
    if value is None:
        return None, None
    if state is None:
        state = default_state

    value, error = test_isinstance(dict)(value, state = state)
    if error is not None:
        return value, error

    package = value.copy()
    related = package.pop('related', UnboundLocalError)
    dataset_attributes, errors = pipe(
        make_ckan_json_to_package(drop_none_values = 'missing'),
        rename_item('id', '_id'),
        )(package, state = state)

    if related is not UnboundLocalError:
        related, error = pipe(
            test_isinstance(list),
            uniform_sequence(
                make_ckan_json_to_related(drop_none_values = 'missing'),
                drop_none_items = True,
                ),
            empty_to_none,
            )(related, state = state)
        if error is not None:
            if errors is None:
                errors = {}
            errors['related'] = error
        dataset_attributes['related'] = related

    return dataset_attributes, errors


ckan_user_to_account_attributes = pipe(
    make_ckan_json_to_user(drop_none_values = 'missing'),
    rename_item('id', '_id'),
    )


def input_to_name(value, state = None):
    return texthelpers.namify(value) or None, None


input_to_token = cleanup_line


json_to_dataset_attributes = pipe(
    test_isinstance(dict),
    struct(
        dict(
            id = pipe(
                input_to_token,
                not_none,
                ),
            ),
        default = noop,  # TODO
        ),
    rename_item('id', '_id'),
    )


json_to_related_link_attributes = pipe(
    test_isinstance(dict),
    struct(
        dict(
            id = pipe(
                input_to_token,
                not_none,
                ),
            ),
        default = noop,  # TODO
        ),
    rename_item('id', '_id'),
    )


def json_to_errors(value, state = None):
    if value is None:
        return value, None
    if state is None:
        state = default_state
    if isinstance(value, dict):
        return uniform_mapping(
            pipe(
                test_isinstance(basestring),
                not_none,
                ),
            json_to_errors,
            )(value, state = state)
    if isinstance(value, list):
        return value, state._(u"Errors can't contain a list")
    return value, None


def method(method_name, *args, **kwargs):
    def method_converter(value, state = None):
        if value is None:
            return value, None
        return getattr(value, method_name)(state or default_state, *args, **kwargs)
    return method_converter
