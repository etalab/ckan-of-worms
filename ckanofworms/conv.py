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


from biryani1 import strings
from biryani1.baseconv import *
from biryani1.bsonconv import *
from biryani1.datetimeconv import *
from biryani1.objectconv import *
from biryani1.jsonconv import *
from biryani1.states import default_state, State
from ckantoolbox.ckanconv import *


ckan_group_to_attributes = pipe(
    make_ckan_json_to_group(drop_none_values = True),
    rename_item('id', '_id'),
    )


ckan_organization_to_attributes = pipe(
    make_ckan_json_to_organization(drop_none_values = True),
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
    related = package.pop('related', None)
    dataset_attributes, errors = pipe(
        make_ckan_json_to_package(drop_none_values = True),
        rename_item('id', '_id'),
        )(package, state = state)

    related, error = pipe(
        test_isinstance(list),
        uniform_sequence(
            ckan_related_to_related_link_attributes,
            drop_none_items = True,
            ),
        empty_to_none,
        )(related, state = state)
    if error is not None:
        if errors is None:
            errors = {}
        errors['related'] = error
    if related is not None:
        dataset_attributes['related'] = related

    return dataset_attributes, errors


ckan_related_to_related_link_attributes = make_ckan_json_to_related(drop_none_values = True)


ckan_user_to_account_attributes = pipe(
    make_ckan_json_to_user(drop_none_values = True),
    rename_item('id', '_id'),
    )


def input_to_name(value, state = None):
    return namify(value) or None, None


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


def method(method_name, *args, **kwargs):
    def method_converter(value, state = None):
        if value is None:
            return value, None
        return getattr(value, method_name)(state or default_state, *args, **kwargs)
    return method_converter


def namify(s, encoding = 'utf-8'):
    """Convert a string to a CKAN name."""
    if s is None:
        return None
    if isinstance(s, str):
        s = s.decode(encoding)
    assert isinstance(s, unicode), str((s,))
    simplified = u''.join([namify_char(unicode_char) for unicode_char in s])
    while u'--' in simplified:
        simplified = simplified.replace(u'--', u'-')
    simplified = simplified.strip(u'-')
    return simplified


def namify_char(unicode_char):
    """Convert an unicode character to a subset of lowercase ASCII characters or an empty string.

    The result can be composed of several characters (for example, 'œ' becomes 'oe').
    """
    chars = strings.unicode_char_to_ascii(unicode_char)
    if chars:
        chars = chars.lower()
        split_chars = []
        for char in chars:
            if char not in '-_0123456789abcdefghijklmnopqrstuvwxyz':
                char = '-'
            split_chars.append(char)
        chars = ''.join(split_chars)
    return chars
