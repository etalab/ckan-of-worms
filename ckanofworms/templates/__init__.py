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


"""Mako templates rendering"""


import email.header
import json
import os

from os.path import join, dirname, abspath

import mako.lookup
import markupsafe

from .. import conf


custom_lookups = {}  # custom TemplateLookups, inited by function load_environment
default_lookup = None  # default TemplateLookup, inited by function load_environment
dirs = None  # Sequence of templates directories, inited by function load_environment
js = lambda x: json.dumps(x, encoding = 'utf-8', ensure_ascii = False)

DEFAULT_STATIC = abspath(join(dirname(__file__), '..', 'static'))
MAIN_TOPICS = None


def format_topic(topic):
    home_url = conf['weckan_url'].replace('http://', '//')
    topic['url'] = '{0}/{{lang}}/groups/{1}'.format(home_url, topic['name'])
    return topic


def main_topics():
    global MAIN_TOPICS
    if not MAIN_TOPICS:
        static_root = conf.get('static_files_dir', DEFAULT_STATIC)
        topics_file = join(static_root, 'bower', 'etalab-assets', 'data', 'main_topics.json')
        with open(topics_file) as f:
            MAIN_TOPICS = map(format_topic, json.load(f))
    return MAIN_TOPICS


def get_default_lookup():
    global default_lookup
    if default_lookup is None:
        default_lookup = mako.lookup.TemplateLookup(
            default_filters = ['h'],
            directories = dirs,
#            error_handler = handle_mako_error,
            input_encoding = 'utf-8',
            module_directory = os.path.join(conf['cache_dir'], 'templates'),
            strict_undefined = False,
            )
    return default_lookup


def get_lookup(custom_name):
    if custom_name is None or conf['customs_dir'] is None:
        return get_default_lookup()
    custom_templates_dir = os.path.join(conf['customs_dir'], custom_name, 'templates')
    if os.path.exists(custom_templates_dir):
        if custom_name not in custom_lookups:
            custom_lookups[custom_name] = mako.lookup.TemplateLookup(
                default_filters = ['h'],
                directories = [custom_templates_dir] + dirs,
#                error_handler = handle_mako_error,
                input_encoding = 'utf-8',
                module_directory = os.path.join(conf['cache_dir'], 'templates-{}'.format(custom_name)),
                strict_undefined = False,
                )
        return custom_lookups[custom_name]
    if custom_name in custom_lookups:
        del custom_lookups[custom_name]
    return get_default_lookup()


def qp(s, encoding = 'utf-8'):
    assert isinstance(s, unicode)
    quoted_words = []
    for word in s.split(' '):
        try:
            word = str(word)
        except UnicodeEncodeError:
            word = str(email.header.Header(word.encode(encoding), encoding))
        quoted_words.append(word)
    return u' '.join(quoted_words)


def render(ctx, template_path, custom_name = None, **kw):
    assert template_path.startswith('/')
    return get_lookup(custom_name).get_template(template_path).render_unicode(
        _ = ctx.translator.ugettext,
        ctx = ctx,
        js = js,
        markupsafe = markupsafe,
        N_ = lambda message: message,
        ngettext = ctx.translator.ngettext,
        qp = qp,
        req = ctx.req,
        lang = ctx.lang[0][:2],
        main_topics = main_topics(),
        **kw).strip()


def render_def(ctx, template_path, def_name, custom_name = None, **kw):
    assert template_path.startswith('/')
    return get_lookup(custom_name).get_template(template_path).get_def(def_name).render_unicode(
        _ = ctx.translator.ugettext,
        ctx = ctx,
        js = js,
        markupsafe = markupsafe,
        N_ = lambda message: message,
        ngettext = ctx.translator.ngettext,
        qp = qp,
        req = ctx.req,
        lang = ctx.lang[0][:2],
        main_topics = main_topics(),
        **kw).strip()
