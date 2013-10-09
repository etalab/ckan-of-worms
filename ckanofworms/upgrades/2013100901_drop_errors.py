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


"""Drop errors from objects (replaced with "alerts")."""


import collections
import logging
import os
import sys

from ckanofworms import objects

app_name = os.path.splitext(os.path.basename(__file__))[0]
log = logging.getLogger(app_name)


def main():
    import argparse

    import paste.deploy

    from ckanofworms import environment, model

    parser = argparse.ArgumentParser(description = __doc__)
    parser.add_argument('config_path', help = 'path of CKAN-of-Worms Paste configuration file')
    parser.add_argument('-v', '--verbose', action = 'store_true', help = 'increase output verbosity')
    args = parser.parse_args()
    logging.basicConfig(level = logging.DEBUG if args.verbose else logging.WARNING, stream = sys.stdout)
    site_conf = paste.deploy.appconfig('config:{}'.format(os.path.abspath(args.config_path)))
    environment.load_environment(site_conf.global_conf, site_conf.local_conf)

    status = model.Status.find_one()
    if status is None:
        status = model.Status()
    upgrade(status)

    return 0


def upgrade(status):
    db = objects.Wrapper.db

    for account in db.accounts.find(dict(errors = {'$exists': True}), as_class = collections.OrderedDict):
        del account['errors']
        db.accounts.save(account)
    for dataset in db.datasets.find(dict(errors = {'$exists': True}), as_class = collections.OrderedDict):
        del dataset['errors']
        db.datasets.save(dataset)
    for group in db.groups.find(dict(errors = {'$exists': True}), as_class = collections.OrderedDict):
        del group['errors']
        db.groups.save(group)
    for organization in db.organizations.find(dict(errors = {'$exists': True}), as_class = collections.OrderedDict):
        del organization['errors']
        db.organizations.save(organization)

    if status.last_upgrade_name is None or status.last_upgrade_name < app_name:
        status.last_upgrade_name = app_name
        status.save()


if __name__ == "__main__":
    sys.exit(main())
