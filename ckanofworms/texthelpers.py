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


"""Helpers to handle strings"""


import bleach
from ckantoolbox.texthelpers import namify
import markdown


bleach_allowed_attributes = dict(
    a = ['href', 'title'],
    acronym = ['title'],
    abbr = ['title'],
    img = ['alt', 'src', 'title'],
    )
bleach_allowed_styles = []
bleach_allowed_tags = [
    'a',
    'abbr',
    'acronym',
    'b',
    'blockquote',
    'code',
    'em',
    'i',
    'img',
    'li',
    'ol',
    'p',
    'strong',
    'ul',
    ]


def htmlify_markdown(text):
    if not text:
        return u''
    return bleach.clean(markdown.markdown(text), attributes = bleach_allowed_attributes, styles = bleach_allowed_styles,
        tags = bleach_allowed_tags)


def textify_markdown(text):
    if not text:
        return u''
    return bleach.clean(markdown.markdown(text), attributes = {}, styles = [], tags = [], strip = True)


def truncate(text, length = 30, indicator = u'…', whole_word = False):
    """Truncate ``text`` to a maximum number of characters.

    Code taken from webhelpers.

    ``length``
        The maximum length of ``text`` before replacement
    ``indicator``
        If ``text`` exceeds the ``length``, this string will replace
        the end of the string
    ``whole_word``
        If true, shorten the string further to avoid breaking a word in the
        middle.  A word is defined as any string not containing whitespace.
        If the entire text before the break is a single word, it will have to
        be broken.

    Example::

        >>> truncate('Once upon a time in a world far far away', 14)
        'Once upon a...'

    """
    if not text:
        return u''
    if len(text) <= length:
        return text
    short_length = length - len(indicator)
    if whole_word:
        # Go back to end of previous word.
        i = short_length
        while i >= 0 and not text[i].isspace():
            i -= 1
        while i >= 0 and text[i].isspace():
            i -= 1
        if i > 0:
            return text[:i + 1] + indicator
        # Entire text before break is one word.
    return text[:short_length] + indicator
