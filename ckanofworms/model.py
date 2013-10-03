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


"""The application's model objects"""


import collections
import conv
import datetime

import fedmsg

from . import conf, objects, urls, wsgihelpers


class Account(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    admin = False
    api_key = None
    collection_name = 'accounts'
    email = None
    errors = None

    # CKAN attributes
    created = None
    fullname = None
    name = None

    def after_delete(self, ctx, old_bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(old_bson, state = ctx),
            topic = 'account.delete',
            )

    def after_upsert(self, ctx, old_bson, bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(bson, state = ctx),
            topic = 'account.{}'.format('create' if old_bson is None else 'update'),
            )

    @classmethod
    def bson_to_json(cls, value, state = None):
        if value is None:
            return value, None
        value = value.copy()
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'accounts', *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_admin_class_url(ctx, self._id, *path, **query)

    def get_groups_cursor(self):
        return Group.find({'users.id': self._id})

    def get_organizations_cursor(self):
        return Organization.find({'users.id': self._id})

    def get_title(self, ctx):
        return self.fullname or self.name or self.email or self._id

    @classmethod
    def make_id_to_instance(cls):
        def id_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                return value, state._(u"No account with ID {0}").format(value)
            return self, None
        return id_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = id
        return value, None


class Dataset(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    collection_name = u'datasets'
    errors = None

    # CKAN attributes
    author = None
    author_email = None
    extras = None
    groups = None  # TODO: Replace with groups_id
    license_id = None
    maintainer = None
    maintainer_email = None
    metadata_created = None
    metadata_modified = None
    name = None
    notes = None
    owner_org = None
    resources = None
    revision_id = None
    revision_timestamp = None
    supplier_id = None
    tags = None
    temporal_coverage_from = None
    temporal_coverage_to = None
    territorial_coverage = None
    territorial_coverage_granularity = None
    title = None

    def after_delete(self, ctx, old_bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(old_bson, state = ctx),
            topic = 'dataset.delete',
            )

    def after_upsert(self, ctx, old_bson, bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(bson, state = ctx),
            topic = 'dataset.{}'.format('create' if old_bson is None else 'update'),
            )

    @classmethod
    def bson_to_json(cls, value, state = None):
        if value is None:
            return value, None
        value = value.copy()
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'datasets', *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_admin_class_url(ctx, self._id, *path, **query)

    def get_title(self, ctx):
        return self.title or self.name or self._id

    @classmethod
    def make_id_to_instance(cls):
        def id_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                return value, state._(u"No dataset with ID {0}").format(value)
            return self, None
        return id_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = id
        return value, None


class Group(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    collection_name = u'groups'
    errors = None

    # CKAN attributes
    created = None
    name = None
    title = None

    def after_delete(self, ctx, old_bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(old_bson, state = ctx),
            topic = 'group.delete',
            )

    def after_upsert(self, ctx, old_bson, bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(bson, state = ctx),
            topic = 'group.{}'.format('create' if old_bson is None else 'update'),
            )

    @classmethod
    def bson_to_json(cls, value, state = None):
        if value is None:
            return value, None
        value = value.copy()
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'groups', *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_admin_class_url(ctx, self._id, *path, **query)

    def get_title(self, ctx):
        return self.title or self.name or self._id

    @classmethod
    def make_id_to_instance(cls):
        def id_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                return value, state._(u"No group with ID {0}").format(value)
            return self, None
        return id_to_instance

    @classmethod
    def make_title_to_instance(cls):
        def title_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            self = cls.find_one(
                dict(
                    title = value,
                    ),
                as_class = collections.OrderedDict,
                )
            if self is None:
                return value, state._(u"No group with title {0}").format(value)
            return self, None
        return title_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = id
        return value, None


class Organization(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    collection_name = u'organizations'
    errors = None

    # CKAN attributes
    created = None
    name = None
    title = None

    def after_delete(self, ctx, old_bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(old_bson, state = ctx),
            topic = 'organization.delete',
            )

    def after_upsert(self, ctx, old_bson, bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(bson, state = ctx),
            topic = 'organization.{}'.format('create' if old_bson is None else 'update'),
            )

    @classmethod
    def bson_to_json(cls, value, state = None):
        if value is None:
            return value, None
        value = value.copy()
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = unicode(id)
        return value, None

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'organizations', *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None:
            return None
        return self.get_admin_class_url(ctx, self._id, *path, **query)

    def get_title(self, ctx):
        return self.title or self.name or self._id

    @classmethod
    def make_id_to_instance(cls):
        def id_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                return value, state._(u"No organization with ID {0}").format(value)
            return self, None
        return id_to_instance

    @classmethod
    def make_title_to_instance(cls):
        def title_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            self = cls.find_one(
                dict(
                    title = value,
                    ),
                as_class = collections.OrderedDict,
                )
            if self is None:
                return value, state._(u"No organization with title {0}").format(value)
            return self, None
        return title_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = id
        return value, None


class Session(objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    _user = UnboundLocalError
    collection_name = 'sessions'
    expiration = None
    token = None  # the cookie token
    user_id = None

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'sessions', *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self.token is None:
            return None
        return self.get_admin_class_url(ctx, self.token, *path, **query)

    def get_title(self, ctx):
        user = self.user
        if user is None:
            return ctx._(u'Session {0}').format(self.token)
        return ctx._(u'Session {0} of {1}').format(self.token, user.get_title(ctx))

    @classmethod
    def make_token_to_instance(cls):
        def token_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state

            # First, delete expired sessions.
            cls.remove_expired(state)

            self = cls.find_one(dict(token = value), as_class = collections.OrderedDict)
            if self is None:
                return value, state._(u"No session with token {0}").format(value)
            return self, None
        return token_to_instance

    @classmethod
    def remove_expired(cls, ctx):
        for self in cls.find(
                dict(expiration = {'$lt': datetime.datetime.utcnow()}),
                as_class = collections.OrderedDict,
                ):
            self.delete(ctx)

    def to_bson(self):
        self_bson = self.__dict__.copy()
        self_bson.pop('_user', None)
        return self_bson

    @property
    def user(self):
        from . import model
        if self._user is UnboundLocalError:
            self._user = model.Account.find_one(self.user_id) if self.user_id is not None else None
        return self._user


class Status(objects.Mapper, objects.Wrapper):
    collection_name = 'status'
    last_upgrade_name = None


def configure(ctx):
    pass


def get_user(ctx, check = False):
    user = ctx.user
    if user is UnboundLocalError:
        session = ctx.session
        ctx.user = user = session.user if session is not None else None
    if user is None and check:
        raise wsgihelpers.unauthorized(ctx)
    return user


def init(db):
    objects.Wrapper.db = db


def is_admin(ctx, check = False):
    user = get_user(ctx)
    if user is None or not user.admin:
        if user is not None and Account.find_one(dict(admin = True), []) is None:
            # Whem there is no admin, every logged user is an admin.
            return True
        if check:
            raise wsgihelpers.forbidden(ctx, message = ctx._(u"You must be an administrator to access this page."))
        return False
    return True


def setup():
    """Setup MongoDb database."""
    import imp
    import os
    from . import upgrades

    upgrades_dir = os.path.dirname(upgrades.__file__)
    upgrades_name = sorted(
        os.path.splitext(upgrade_filename)[0]
        for upgrade_filename in os.listdir(upgrades_dir)
        if upgrade_filename.endswith('.py') and upgrade_filename != '__init__.py'
        )
    status = Status.find_one(as_class = collections.OrderedDict)
    if status is None:
        status = Status()
        if upgrades_name:
            status.last_upgrade_name = upgrades_name[-1]
        status.save()
    else:
        for upgrade_name in upgrades_name:
            if status.last_upgrade_name is None or status.last_upgrade_name < upgrade_name:
                print 'Upgrading "{0}"'.format(upgrade_name)
                upgrade_file, upgrade_file_path, description = imp.find_module(upgrade_name, [upgrades_dir])
                try:
                    upgrade_module = imp.load_module(upgrade_name, upgrade_file, upgrade_file_path, description)
                finally:
                    if upgrade_file:
                        upgrade_file.close()
                upgrade_module.upgrade(status)

    Account.ensure_index('admin', sparse = True)
    Account.ensure_index('api_key', sparse = True, unique = True)
    Account.ensure_index('email', sparse = True, unique = True)

    Dataset.ensure_index('name', unique = True)

    Group.ensure_index('users.id')

    Organization.ensure_index('users.id')

    Session.ensure_index('expiration')
    Session.ensure_index('token', unique = True)
