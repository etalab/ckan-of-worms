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


"""Harvest a CKAN repository."""


import argparse
import ConfigParser
import json
import logging
import os
import sys
import urllib
import urllib2
import urlparse

from biryani1 import baseconv, custom_conv, states


app_name = os.path.splitext(os.path.basename(__file__))[0]
conv = custom_conv(baseconv, states)
log = logging.getLogger(app_name)


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config', help = 'path of configuration file')
    parser.add_argument('-a', '--all', action = 'store_true', default = False, help = "harvest everything")
    parser.add_argument('-g', '--group', action = 'store_true', default = False, help = "harvest groups")
    parser.add_argument('-o', '--organization', action = 'store_true', default = False, help = "harvest organizations")
    parser.add_argument('-p', '--package', action = 'store_true', default = False, help = "harvest packages")
    parser.add_argument('-u', '--user', action = 'store_true', default = False, help = "harvest users")
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
                'ckan.api_key': conv.pipe(
                    conv.cleanup_line,
                    conv.not_none,
                    ),
                'ckan.site_url': conv.pipe(
                    conv.make_input_to_url(error_if_fragment = True, error_if_path = True, error_if_query = True,
                        full = True),
                    conv.not_none,
                    ),
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

    source_headers = {
        'Authorization': conf['ckan.api_key'],  # API key is required to get full user profile.
        'User-Agent': conf['user_agent'],
        }
    source_site_url = conf['ckan.site_url']
    target_api_key = conf['ckan_of_worms.api_key']
    target_headers = {
        'User-Agent': conf['user_agent'],
        }
    target_site_url = conf['ckan_of_worms.site_url']

    if args.all or args.group:
        # Retrieve names of groups in source.
        request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/group_list'),
            headers = source_headers)
        response = urllib2.urlopen(request, '{}')  # CKAN < 2.0 requires a POST.
        response_dict = json.loads(response.read())
        groups_source_name = response_dict['result']

        # Retrieve groups from source.
        for group_source_name in groups_source_name:
            log.info(u'Upserting group: {}'.format(group_source_name))

            # Retrieve group.
            request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/group_show'),
                headers = source_headers)
            try:
                response = urllib2.urlopen(request, urllib.quote(json.dumps(dict(
                            id = group_source_name,
                            ))))  # CKAN < 2.0 requires a POST.
            except urllib2.HTTPError as response:
                if response.code == 403:
                    # Private dataset
                    continue
                raise
            response_dict = json.loads(response.read())
            group = response_dict['result']

            request_headers = target_headers.copy()
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
#                dataset = response_dict['value']
#                print dataset

    if args.all or args.organization:
        # Retrieve names of organizations in source.
        request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/organization_list'),
            headers = source_headers)
        response = urllib2.urlopen(request, '{}')  # CKAN < 2.0 requires a POST.
        response_dict = json.loads(response.read())
        organizations_source_name = response_dict['result']

        # Retrieve organizations from source.
        for organization_source_name in organizations_source_name:
            log.info(u'Upserting organization: {}'.format(organization_source_name))

            # Retrieve organization.
            request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/organization_show'),
                headers = source_headers)
            try:
                response = urllib2.urlopen(request, urllib.quote(json.dumps(dict(
                            id = organization_source_name,
                            ))))  # CKAN < 2.0 requires a POST.
            except urllib2.HTTPError as response:
                if response.code == 403:
                    # Private dataset
                    continue
                raise
            response_dict = json.loads(response.read())
            organization = response_dict['result']

            request_headers = target_headers.copy()
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
#                dataset = response_dict['value']
#                print dataset

    if args.all or args.package:
        # Retrieve names of packages in source.
        request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/package_list'),
            headers = source_headers)
        response = urllib2.urlopen(request, '{}')  # CKAN < 2.0 requires a POST.
        response_dict = json.loads(response.read())
        packages_source_name = response_dict['result']

        # Retrieve packages from source.
        for package_source_name in packages_source_name:
            log.info(u'Upserting dataset from package: {}'.format(package_source_name))

            # Retrieve package.
            request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/package_show'),
                headers = source_headers)
            try:
                response = urllib2.urlopen(request, urllib.quote(json.dumps(dict(
                    id = package_source_name,
                    ))))  # CKAN < 2.0 requires a POST.
            except urllib2.HTTPError as response:
                if response.code == 403:
                    # Private dataset
                    continue
                raise
            response_dict = json.loads(response.read())
            package = response_dict['result']

            # Retrieve package's related.
            request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/related_list'),
                headers = source_headers)
            response = urllib2.urlopen(request, urllib.quote(json.dumps(dict(
                id = package_source_name,
                ))))  # CKAN < 2.0 requires a POST.
            response_dict = json.loads(response.read())
            package['related'] = response_dict['result']

            request_headers = target_headers.copy()
            request_headers['Content-Type'] = 'application/json'
            request = urllib2.Request(urlparse.urljoin(target_site_url, 'api/1/datasets/ckan'),
                headers = request_headers)
            try:
                response = urllib2.urlopen(request, json.dumps(dict(
                    api_key = target_api_key,
                    value = package,
                    )))
            except urllib2.HTTPError as response:
                log.error(u'An error occured while upserting dataset from package: {}'.format(package))
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
#                dataset = response_dict['value']
#                print dataset

    if args.all or args.user:
        # Retrieve names of users in source.
        request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/user_list'),
            headers = source_headers)
        response = urllib2.urlopen(request, '{}')  # CKAN < 2.0 requires a POST.
        response_dict = json.loads(response.read())
        users = response_dict['result']

        # Retrieve users from source.
        for user in users:
            log.info(u'Upserting account from user: {} ({}) {}'.format(user.get('fullname'), user.get('name'),
                user.get('email')))

            # Retrieve full user.
            request = urllib2.Request(urlparse.urljoin(source_site_url, 'api/3/action/user_show'),
                headers = source_headers)
            try:
                response = urllib2.urlopen(request, urllib.quote(json.dumps(dict(
                    id = user['id'],
                    ))))  # CKAN < 2.0 requires a POST.
            except urllib2.HTTPError as response:
                if response.code == 403:
                    # Private user
                    continue
                raise
            response_dict = json.loads(response.read())
            user = response_dict['result']

            request_headers = target_headers.copy()
            request_headers['Content-Type'] = 'application/json'
            request = urllib2.Request(urlparse.urljoin(target_site_url, 'api/1/accounts/ckan'),
                headers = request_headers)
            try:
                response = urllib2.urlopen(request, json.dumps(dict(
                    api_key = target_api_key,
                    value = user,
                    )))
            except urllib2.HTTPError as response:
                log.error(u'An error occured while upserting account from user: {}'.format(user))
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
#                account = response_dict['value']
#                print account

    return 0


if __name__ == '__main__':
    sys.exit(main())
