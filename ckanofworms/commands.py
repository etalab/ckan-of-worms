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


"""Setup commands"""


import logging
import os
import shutil

from glob import iglob
from os import makedirs
from os.path import dirname, join, exists, isdir

import setuptools
import webassets.script

from . import environment

STATIC = join(dirname(__file__), 'static')

TO_COPY = {
    'bower/bootstrap/dist/fonts/*': 'fonts/',
    'bower/etalab-assets/fonts/*': 'fonts/',
    'bower/etalab-assets/img/*': 'img/',
    'bower/etalab-assets/img/flags/*': 'img/flags/',
}


class BuildAssets(setuptools.Command):
    """Build assets for production deployment."""
    description = "Precompile WebAssets environment."
    user_options = []

    def finalize_options(self):
        pass

    def initialize_options(self):
        pass

    def run(self):
        assets = environment.configure_assets(
            debug = False,
            static_dir = STATIC,
            )

        log = logging.getLogger('webassets')
        log.addHandler(logging.StreamHandler())
        log.setLevel(logging.DEBUG)

        command_line_environment = webassets.script.CommandLineEnvironment(assets, log)
        command_line_environment.build()

        for source, destination in TO_COPY.items():
            log.info('Copying %s to %s', source, destination)
            destination_path = os.path.join(STATIC, destination)
            if not exists(destination_path):
                makedirs(destination_path)
            for filename in iglob(join(STATIC, source)):
                if isdir(filename):
                    continue
                shutil.copy(filename, destination_path)
