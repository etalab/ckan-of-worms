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


"""Reindex objects."""


import argparse
import logging
import os
import sys

import paste.deploy

from ckanofworms import contexts, environment, model


app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def main():
    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config', help = "CKAN-of-Worms configuration file")
    parser.add_argument('-a', '--all', action = 'store_true', default = False, help = "publish everything")
    parser.add_argument('-d', '--dataset', action = 'store_true', default = False, help = "publish datasets")
    parser.add_argument('-g', '--group', action = 'store_true', default = False, help = "publish groups")
    parser.add_argument('-o', '--organization', action = 'store_true', default = False, help = "publish organizations")
    parser.add_argument('-s', '--section', default = 'main',
        help = "Name of configuration section in configuration file")
    parser.add_argument('-u', '--user', action = 'store_true', default = False, help = "publish accounts")
    parser.add_argument('-v', '--verbose', action = 'store_true', default = False, help = "increase output verbosity")
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)
    site_conf = paste.deploy.appconfig('config:{0}#{1}'.format(os.path.abspath(args.config), args.section))
    environment.load_environment(site_conf.global_conf, site_conf.local_conf)

    ctx = contexts.null_ctx

    if args.all or args.dataset:
        for dataset in model.Dataset.find():
            dataset.compute_weight()
            dataset.compute_timestamp()
            if dataset.save(ctx, safe = False):
                log.info(u'Updated dataset: {}'.format(dataset.name))

    if args.all or args.user:
        for account in model.Account.find():
            account.compute_slug_and_words()
            if account.save(ctx, safe = False):
                log.info(u'Updated account: {} - {} <{}>'.format(account.name, account.fullname, account.email))

    return 0


if __name__ == "__main__":
    sys.exit(main())
