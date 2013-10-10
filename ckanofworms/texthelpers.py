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


from biryani1 import strings
import bleach
import markdown


def namify(text, encoding = 'utf-8'):
    """Convert a string to a CKAN name."""
    if text is None:
        return None
    if isinstance(text, str):
        text = text.decode(encoding)
    assert isinstance(text, unicode), str((text,))
    simplified = u''.join(namify_char(unicode_char) for unicode_char in text)
    # CKAN accepts names with duplicate "-" or "_" and/or ending with "-" or "_".
    #while u'--' in simplified:
    #    simplified = simplified.replace(u'--', u'-')
    #while u'__' in simplified:
    #    simplified = simplified.replace(u'__', u'_')
    #simplified = simplified.strip(u'-_')
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
            return text[:i+1] + indicator
        # Entire text before break is one word.
    return text[:short_length] + indicator
