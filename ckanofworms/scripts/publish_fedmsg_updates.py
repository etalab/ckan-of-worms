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


"""Setup application (Create indexes, launch upgrade scripts, etc)."""


import argparse
import logging
import os
import re
import sys
import time

import paste.deploy
import pymongo

from ckanofworms import contexts, model, environment


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)
invalid_cursor_re = re.compile(r"cursor id '\d+' not valid at server$")


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config', help = "CKAN-of-Worms configuration file")
    parser.add_argument('-a', '--all', action = 'store_true', default = False, help = "publish everything")
    parser.add_argument('-d', '--dataset', action = 'store_true', default = False, help = "publish datasets")
    parser.add_argument('-g', '--group', action = 'store_true', default = False, help = "publish groups")
    parser.add_argument('-o', '--organization', action = 'store_true', default = False, help = "publish organizations")
    parser.add_argument('-s', '--section', default = 'main',
        help = "Name of configuration section in configuration file")
    parser.add_argument('-u', '--user', action = 'store_true', default = False, help = "publish users")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)
    site_conf = paste.deploy.appconfig('config:{0}#{1}'.format(os.path.abspath(args.config), args.section))
    environment.load_environment(site_conf.global_conf, site_conf.local_conf)

    ctx = contexts.null_ctx

    if args.all or args.dataset:
        index = 0
        while True:
            try:
                for index, dataset in enumerate(model.Dataset.find().skip(index), index):
                    log.info(u'Publishing dataset update: {} - {}'.format(index, dataset.name))
                    bson = dataset.to_bson() or {}
                    dataset.after_upsert(ctx, bson, bson)
                    time.sleep(1.0)
            except pymongo.errors.OperationFailure, exception:
                if invalid_cursor_re.match(str(exception)) is None:
                    raise
            else:
                break

    if args.all or args.group:
        index = 0
        while True:
            try:
                for index, group in enumerate(model.Group.find().skip(index), index):
                    log.info(u'Publishing group update: {} - {}'.format(index, group.name))
                    bson = group.to_bson() or {}
                    group.after_upsert(ctx, bson, bson)
                    time.sleep(1.0)
            except pymongo.errors.OperationFailure, exception:
                if invalid_cursor_re.match(str(exception)) is None:
                    raise
            else:
                break

    if args.all or args.organization:
        index = 0
        while True:
            try:
                for index, organization in enumerate(model.Organization.find().skip(index), index):
                    log.info(u'Publishing organization update: {} - {}'.format(index, organization.name))
                    bson = organization.to_bson() or {}
                    organization.after_upsert(ctx, bson, bson)
                    time.sleep(1.0)
            except pymongo.errors.OperationFailure, exception:
                if invalid_cursor_re.match(str(exception)) is None:
                    raise
            else:
                break

    if args.all or args.user:
        index = 0
        while True:
            try:
                for index, user in enumerate(model.User.find().skip(index), index):
                    log.info(u'Publishing user update: {} - {}'.format(index,
                        related_link.title or related_link.url or related_link.image_url))
                    bson = related_link.to_bson() or {}
                    related_link.after_upsert(ctx, bson, bson)
                    time.sleep(1.0)
            except pymongo.errors.OperationFailure, exception:
                if invalid_cursor_re.match(str(exception)) is None:
                    raise
            else:
                break

    return 0


if __name__ == "__main__":
    sys.exit(main())
