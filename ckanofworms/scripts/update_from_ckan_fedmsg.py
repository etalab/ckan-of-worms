#! /usr/bin/env python
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


"""Consume fedmsg messages from CKAN and send them to CKAN-of-Worms."""


import argparse
import ConfigParser
import json
import logging
import os
import sys
import urllib2
import urlparse

from biryani1 import baseconv, custom_conv, states
import fedmsg


app_name = os.path.splitext(os.path.basename(__file__))[0]
conv = custom_conv(baseconv, states)
log = logging.getLogger(app_name)


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config', help = 'path of configuration file')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'increase output verbosity')

    global args
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)

    config_parser = ConfigParser.SafeConfigParser(dict(here = os.path.dirname(args.config)))
    config_parser.read(args.config)
    conf = conv.check(conv.pipe(
        conv.test_isinstance(dict),
        conv.struct(
            {
                'ckan_of_worms.api_key': conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                'ckan_of_worms.site_url': conv.pipe(
                    conv.make_input_to_url(error_if_fragment = True, error_if_path = True, error_if_query = True,
                        full = True),
                    conv.not_none,
                    ),
                'user_agent': conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                },
            default = 'drop',
            ),
        conv.not_none,
        ))(dict(config_parser.items('CKAN-of-Worms-Harvesters')), conv.default_state)

    fedmsg_conf = conv.check(conv.struct(
        dict(
            environment = conv.pipe(
                conv.empty_to_none,
                conv.test_in(['dev', 'prod', 'stg']),
                ),
            modname = conv.pipe(
                conv.empty_to_none,
                conv.test(lambda value: value == value.strip('.'), error = 'Value must not begin or end with a "."'),
                conv.default('ckan_of_worms'),
                ),
#            name = conv.pipe(
#                conv.empty_to_none,
#                conv.default('ckan_of_worms.{}'.format(hostname)),
#                ),
            topic_prefix = conv.pipe(
                conv.empty_to_none,
                conv.test(lambda value: value == value.strip('.'), error = 'Value must not begin or end with a "."'),
                ),
            ),
        default = 'drop',
        ))(dict(config_parser.items('fedmsg')))

    headers = {
        'User-Agent': conf['user_agent'],
        }
    target_api_key = conf['ckan_of_worms.api_key']
    target_site_url = conf['ckan_of_worms.site_url']

    # Read in the config from /etc/fedmsg.d/.
    fedmsg_config = fedmsg.config.load_config([], None)
    # Disable a warning about not sending.  We know.  We only want to tail.
    fedmsg_config['mute'] = True
    # Disable timing out so that we can tail forever.  This is deprecated
    # and will disappear in future versions.
    fedmsg_config['timeout'] = 0
    # For the time being, don't require message to be signed.
    fedmsg_config['validate_signatures'] = False
    for key, value in fedmsg_conf.iteritems():
        if value is not None:
            fedmsg_config[key] = value

    expected_topic_prefix = '{}.{}.ckan.'.format(fedmsg_config['topic_prefix'], fedmsg_config['environment'])
    for name, endpoint, topic, message in fedmsg.tail_messages(**fedmsg_config):
        if not topic.startswith(expected_topic_prefix):
            log.debug(u'Ignoring message: {}, {}'.format(topic, name))
            continue
        kind, action = topic[len(expected_topic_prefix):].split('.')
        if kind == 'group':
            if action in ('create', 'update'):
                group = message['msg']

                log.info(u'Upserting group: {}'.format(group['name']))
                request_headers = headers.copy()
                request_headers['Content-Type'] = 'application/json'
                request = urllib2.Request(urlparse.urljoin(target_site_url, 'api/1/groups/ckan'),
                    headers = request_headers)
                try:
                    response = urllib2.urlopen(request, json.dumps(dict(
                        api_key = target_api_key,
                        value = group,
                        )))
                except urllib2.HTTPError as response:
                    log.error(u'An error occured while upserting group: {}'.format(group))
                    response_text = response.read()
                    try:
                        response_dict = json.loads(response_text)
                    except ValueError:
                        log.error(response_text)
                        raise
                    for key, value in response_dict.iteritems():
                        print '{} = {}'.format(key, value)
                    raise
                else:
                    assert response.code == 200
                    response_dict = json.loads(response.read())
#                    group = response_dict['value']
#                    print group
            else:
                log.warning(u'TODO: Handle {}, {} for {}'.format(kind, action, message))
        elif kind == 'organization':
            if action in ('create', 'update'):
                organization = message['msg']

                log.info(u'Upserting organization: {}'.format(organization['name']))
                request_headers = headers.copy()
                request_headers['Content-Type'] = 'application/json'
                request = urllib2.Request(urlparse.urljoin(target_site_url, 'api/1/organizations/ckan'),
                    headers = request_headers)
                try:
                    response = urllib2.urlopen(request, json.dumps(dict(
                        api_key = target_api_key,
                        value = organization,
                        )))
                except urllib2.HTTPError as response:
                    log.error(u'An error occured while upserting organization: {}'.format(organization))
                    response_text = response.read()
                    try:
                        response_dict = json.loads(response_text)
                    except ValueError:
                        log.error(response_text)
                        raise
                    for key, value in response_dict.iteritems():
                        print '{} = {}'.format(key, value)
                    raise
                else:
                    assert response.code == 200
                    response_dict = json.loads(response.read())
#                    organization = response_dict['value']
#                    print organization
            else:
                log.warning(u'TODO: Handle {}, {} for {}'.format(kind, action, message))
        elif kind == 'package':
            if action in ('create', 'update'):
                package = message['msg']

                log.info(u'Upserting package: {}'.format(package['name']))
                request_headers = headers.copy()
                request_headers['Content-Type'] = 'application/json'
                request = urllib2.Request(urlparse.urljoin(target_site_url, 'api/1/datasets/ckan'),
                    headers = request_headers)
                try:
                    response = urllib2.urlopen(request, json.dumps(dict(
                        api_key = target_api_key,
                        value = package,
                        )))
                except urllib2.HTTPError as response:
                    log.error(u'An error occured while upserting package: {}'.format(package))
                    response_text = response.read()
                    try:
                        response_dict = json.loads(response_text)
                    except ValueError:
                        log.error(response_text)
                        raise
                    for key, value in response_dict.iteritems():
                        print '{} = {}'.format(key, value)
                    raise
                else:
                    assert response.code == 200
                    response_dict = json.loads(response.read())
#                    dataset = response_dict['value']
#                    print dataset
            else:
                log.warning(u'TODO: Handle {}, {} for {}'.format(kind, action, message))
#        elif kind == 'related':
#            if action in ('create', 'update'):
#                related = message['msg']

#                log.info(u'Upserting related: {} '.format(
#                    related.get('title') or related.get('url') or related.get('image_url')))
#                request_headers = headers.copy()
#                request_headers['Content-Type'] = 'application/json'
#                request = urllib2.Request(urlparse.urljoin(target_site_url, 'api/1/related_links/ckan'),
#                    headers = request_headers)
#                try:
#                    response = urllib2.urlopen(request, json.dumps(dict(
#                        api_key = target_api_key,
#                        value = related,
#                        )))
#                except urllib2.HTTPError as response:
#                    log.error(u'An error occured while upserting related: {}'.format(related))
#                    response_text = response.read()
#                    try:
#                        response_dict = json.loads(response_text)
#                    except ValueError:
#                        log.error(response_text)
#                        raise
#                    for key, value in response_dict.iteritems():
#                        print '{} = {}'.format(key, value)
#                    raise
#                else:
#                    assert response.code == 200
#                    response_dict = json.loads(response.read())
##                    related = response_dict['value']
##                    print related
#            else:
#                log.warning(u'TODO: Handle {}, {} for {}'.format(kind, action, message))
        else:
            log.warning(u'TODO: Handle {}, {} for {}'.format(kind, action, message))

    return 0


if __name__ == '__main__':
    sys.exit(main())
