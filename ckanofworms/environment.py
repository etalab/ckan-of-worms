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


"""Environment configuration"""


import logging
import os
import socket
import sys

from biryani1 import strings
import fedmsg
import pkg_resources
import pymongo
import webassets
import webassets.loaders

import ckanofworms
from . import conv, model, templates


app_dir = os.path.dirname(os.path.abspath(__file__))
hostname = socket.gethostname().split('.')[0]


def configure_assets(debug = False, static_dir = None):
    """Configure WebAssets."""
    assets = webassets.Environment(static_dir, '/')
    assets.auto_build = debug
    assets.debug = debug

    # Load bundle from yaml file.
    assets_loader = webassets.loaders.YAMLLoader(pkg_resources.resource_stream(__name__, 'assets.yaml'))
    bundles = assets_loader.load_bundles()
    for name, bundle in bundles.items():
        assets.register(name, bundle)

    return assets


def load_environment(global_conf, app_conf):
    """Configure the application environment."""
    conf = ckanofworms.conf  # Empty dictionary
    conf.update(strings.deep_decode(global_conf))
    conf.update(strings.deep_decode(app_conf))
    conf.update(conv.check(conv.struct(
        {
            'app_conf': conv.set_value(app_conf),
            'app_dir': conv.set_value(app_dir),
            'biryani1_i18n_dir': conv.pipe(
                conv.default(os.path.normpath(os.path.join(app_dir, '..', '..', 'biryani1', 'biryani1', 'i18n'))),
                conv.test(os.path.exists),
                ),
            'cache_dir': conv.default(os.path.join(os.path.dirname(app_dir), 'cache')),
            'cookie': conv.default('ckan-of-worms'),
            'database': conv.default('ckan_of_worms'),
            'debug': conv.pipe(conv.guess_bool, conv.default(False)),
            'fedmsg.environment': conv.pipe(
                conv.empty_to_none,
                conv.test_in(['dev', 'prod', 'stg']),
                conv.default('dev'),
                ),
            'fedmsg.modname': conv.pipe(
                conv.empty_to_none,
                conv.test(lambda value: value == value.strip('.'), error = 'Value must not begin or end with a "."'),
                conv.default('ckan_of_worms'),
                ),
            'fedmsg.name': conv.pipe(
                conv.empty_to_none,
                conv.default('ckan_of_worms.{}'.format(hostname)),
                ),
            'fedmsg.topic_prefix': conv.pipe(
                conv.empty_to_none,
                conv.test(lambda value: value == value.strip('.'), error = 'Value must not begin or end with a "."'),
                conv.not_none,
                ),
            'global_conf': conv.set_value(global_conf),
#            'host_urls': conv.pipe(
#                conv.function(lambda host_urls: host_urls.split()),
#                conv.uniform_sequence(
#                    conv.make_input_to_url(error_if_fragment = True, error_if_path = True, error_if_query = True,
#                        full = True, schemes = (u'ws', u'wss')),
#                    constructor = lambda host_urls: sorted(set(host_urls)),
#                    ),
#                ),
            'i18n_dir': conv.default(os.path.join(app_dir, 'i18n')),
            'log_level': conv.pipe(
                conv.default('WARNING'),
                conv.function(lambda log_level: getattr(logging, log_level.upper())),
                ),
            'package_name': conv.default('ckan-of-worms'),
            'realm': conv.default(u'CKAN-of-Worms'),
            # Whether this application serves its own static files.
            'static_files': conv.pipe(conv.guess_bool, conv.default(True)),
            'static_files_dir': conv.default(os.path.join(app_dir, 'static')),
            },
        default = 'drop',
        ))(conf))

    # Configure logging.
    logging.basicConfig(level = conf['log_level'], stream = sys.stderr)

    errorware = conf.setdefault('errorware', {})
    errorware['debug'] = conf['debug']
    if not errorware['debug']:
        errorware['error_email'] = conf['email_to']
        errorware['error_log'] = conf.get('error_log', None)
        errorware['error_message'] = conf.get('error_message', 'An internal server error occurred')
        errorware['error_subject_prefix'] = conf.get('error_subject_prefix', 'CKAN-of-Worms Error: ')
        errorware['from_address'] = conf['from_address']
        errorware['smtp_server'] = conf.get('smtp_server', 'localhost')

    # Configure fedmsg.
    fedmsg.init(active = True, name = 'relay_inbound', **dict(
        (key[len('fedmsg.'):], value)
        for key, value in conf.iteritems()
        if key.startswith('fedmsg.') and key != 'fedmsg.name' and value is not None
        ))

    # Load MongoDB database.
    db = pymongo.Connection()[conf['database']]
    model.init(db)

    # Create the Mako TemplateLookup, with the default auto-escaping.
    templates.dirs = [os.path.join(app_dir, 'templates')]

    # Configure WebAssets.
    conf['assets'] = configure_assets(debug = conf['debug'], static_dir = conf['static_files_dir'])


def setup_environment():
    """Setup the application environment (after it has been loaded)."""

    # Setup MongoDB database.
    model.setup()
