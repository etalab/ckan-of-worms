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
import itertools
import re
import urlparse

from biryani1 import strings
import fedmsg

from . import conf, objects, texthelpers, urls, weights, wsgihelpers


uuid_re = re.compile(ur'[\da-f]{8}-[\da-f]{4}-[\da-f]{4}-[\da-f]{4}-[\da-f]{12}$')


class Account(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    admin = False
    alerts = None
    api_key = None
    collection_name = 'accounts'
    email = None
    words = None

    # CKAN attributes
    about = None
    created = None
    email_hash = None
    fullname = None
    name = None
    sysadmin = None

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

    def compute_words(self):
        self.words = sorted(set(strings.slugify(u'-'.join(
            fragment
            for fragment in (
                self._id,
                self.email,
                self.fullname,
                self.name,
                )
            if fragment is not None
            )).split(u'-'))) or None

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'accounts', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'accounts', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_full_url(ctx, self.name or self._id, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_url(ctx, self.name or self._id, *path, **query)

    def get_groups_cursor(self):
        return Group.find({'users.id': self._id})

    def get_organizations_cursor(self):
        return Organization.find({'users.id': self._id})

    def get_title(self, ctx):
        return self.fullname or self.name or self.email or self._id

    @classmethod
    def make_id_or_name_or_words_to_instance(cls):
        def id_or_name_or_words_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            match = uuid_re.match(value)
            if match is None:
                self = cls.find_one(dict(name = value), as_class = collections.OrderedDict)
            else:
                self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                slug = strings.slugify(value)
                words = sorted(set(slug.split(u'-')))
                instances = list(cls.find(
                    dict(
                        words = {'$all': [
                            re.compile(u'^{}'.format(re.escape(word)))
                            for word in words
                            ]},
                        ),
                    as_class = collections.OrderedDict,
                    ).limit(2))
                if not instances:
                    return value, state._(u"No organization with ID, name or words: {0}").format(value)
                if len(instances) > 1:
                    return value, state._(u"Too much organizations with words: {0}").format(u' '.join(words))
                self = instances[0]
            return self, None
        return id_or_name_or_words_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = id
        return value, None


class Dataset(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    _organization = UnboundLocalError
    alerts = None
    collection_name = u'datasets'
    timestamp = None
    weight = None
    words = None

    # CKAN attributes
    author = None
    author_email = None
    extras = None
    frequency = None
    groups = None  # TODO: Replace with groups_id
    license_id = None
    maintainer = None
    maintainer_email = None
    metadata_created = None
    metadata_modified = None
    name = None
    notes = None
    owner_org = None
    related = None
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
    url = None

    def after_delete(self, ctx, old_bson):
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = conv.check(self.bson_to_json)(old_bson, state = ctx),
            topic = 'dataset.delete',
            )

    def after_upsert(self, ctx, old_bson, bson):
        json = conv.check(self.bson_to_json)(bson, state = ctx)
        fedmsg.publish(
            modname = conf['fedmsg.modname'],
            msg = json,
            topic = 'dataset.{}'.format('create' if old_bson is None else 'update'),
            )

        # Publish changes in related links.
        old_related_link_by_id = dict(
            (related_link['id'], related_link)
            for related_link in ((old_bson or {}).get('related') or [])
            )
        related_link_by_id = dict(
            (related_link['id'], related_link)
            for related_link in (bson.get('related') or [])
            )
        for related_link in related_link_by_id.itervalues():
            old_related_link = old_related_link_by_id.get(related_link['id'])
            if related_link != old_related_link:
                related_link_json = related_link.copy()
                related_link_json['dataset'] = json
                owner_id = related_link.get('owner_id')
                if owner_id is not None:
                    owner = Account.find_one(owner_id)
                    if owner is not None:
                        related_link_json['owner'] = conv.check(conv.method('turn_to_json'))(owner, state = ctx)
                fedmsg.publish(
                    modname = conf['fedmsg.modname'],
                    msg = related_link_json,
                    topic = 'related.{}'.format('create' if old_related_link is None else 'update'),
                    )
        for old_related_link in old_related_link_by_id.itervalues():
            if old_related_link['id'] not in related_link_by_id:
                old_related_link_json = old_related_link.copy()
                old_related_link_json['dataset'] = json
                owner_id = old_related_link.get('owner_id')
                if owner_id is not None:
                    owner = Account.find_one(owner_id)
                    if owner is not None:
                        old_related_link_json['owner'] = conv.check(conv.method('turn_to_json'))(owner, state = ctx)
                fedmsg.publish(
                    modname = conf['fedmsg.modname'],
                    msg = old_related_link_json,
                    topic = 'related.delete',
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

    def compute_words(self):
        self.words = sorted(set(strings.slugify(u'-'.join(
            fragment
            for fragment in itertools.chain(
                (
                    self._id,
                    texthelpers.textify_markdown(self.notes),
                    self.title,
                    ),
                itertools.chain(*(
                    [
                        texthelpers.textify_markdown(related_link.get('description')),
                        related_link.get('title'),
                        ]
                    for related_link in (self.related or [])
                    )),
                itertools.chain(*(
                    [
                        texthelpers.textify_markdown(resource.get('description')),
                        resource.get('format'),
                        resource.get('name'),
                        ]
                    for resource in (self.resources or [])
                    )),
                (
                    tag['name']
                    for tag in (self.tags or [])
                    ),
                )
            if fragment is not None
            )).split(u'-'))) or None

    def compute_timestamp(self):
        timestamp = self.revision_timestamp
        # Related links have no revision_timestamp => Use created.
        for related_link in (self.related or []):
            if related_link['created'] > timestamp:
                timestamp = related_link['created']
        for resource in (self.resources or []):
            if resource['revision_timestamp'] > timestamp:
                timestamp = resource['revision_timestamp']
        self.timestamp = timestamp

    def compute_weight(self):
        return weights.compute_dataset_weight(self)

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'datasets', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'datasets', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_full_url(ctx, self.name or self._id, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_url(ctx, self.name or self._id, *path, **query)

    def get_back_url(self, ctx):
        if self.url is not None:
            # When dataset has been supplied by another repository, it should be edited in the supplier's site.
            return self.url
        if self.name is None:
            return None
        return urlparse.urljoin(conf['ckan_url'], u'dataset/{}'.format(self.name))

    @classmethod
    def get_class_back_url(cls, ctx):
        return urlparse.urljoin(conf['ckan_url'], u'dataset')

    @classmethod
    def get_class_front_url(cls, ctx, *path, **query):
        return urlparse.urljoin(conf['weckan_url'], u'dataset')

    def get_front_url(self, ctx, *path, **query):
        if self.name is None:
            return None
        return urlparse.urljoin(conf['weckan_url'], u'dataset/{}'.format(self.name))

    def get_organization(self, ctx):
        if self._organization is UnboundLocalError:
            self._organization = Organization.find_one(self.owner_org) if self.owner_org is not None else None
        return self._organization

    def get_title(self, ctx):
        return self.title or self.name or self._id

    @classmethod
    def make_id_or_name_or_words_to_instance(cls):
        def id_or_name_or_words_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            match = uuid_re.match(value)
            if match is None:
                self = cls.find_one(dict(name = value), as_class = collections.OrderedDict)
            else:
                self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                slug = strings.slugify(value)
                words = sorted(set(slug.split(u'-')))
                instances = list(cls.find(
                    dict(
                        words = {'$all': [
                            re.compile(u'^{}'.format(re.escape(word)))
                            for word in words
                            ]},
                        ),
                    as_class = collections.OrderedDict,
                    ).limit(2))
                if not instances:
                    return value, state._(u"No dataset with ID, name or words: {0}").format(value)
                if len(instances) > 1:
                    return value, state._(u"Too much datasets with words: {0}").format(u' '.join(words))
                self = instances[0]
            return self, None
        return id_or_name_or_words_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = id
        return value, None


class Group(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    alerts = None
    collection_name = u'groups'
    words = None

    # CKAN attributes
    created = None
    description = None
    image_url = None
    name = None
    revision_id = None
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

    def compute_words(self):
        self.words = sorted(set(strings.slugify(u'-'.join(
            fragment
            for fragment in (
                self._id,
                texthelpers.textify_markdown(self.description),
                self.title,
                )
            if fragment is not None
            )).split(u'-'))) or None

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'groups', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'groups', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_full_url(ctx, self.name or self._id, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_url(ctx, self.name or self._id, *path, **query)

    def get_back_url(self, ctx):
        if self.name is None:
            return None
        return urlparse.urljoin(conf['ckan_url'], u'group/{}'.format(self.name))

    @classmethod
    def get_class_back_url(cls, ctx):
        return urlparse.urljoin(conf['ckan_url'], u'group')

    @classmethod
    def get_class_front_url(cls, ctx, *path, **query):
        return urlparse.urljoin(conf['weckan_url'], u'group')

    def get_front_url(self, ctx, *path, **query):
        if self.name is None:
            return None
        return urlparse.urljoin(conf['weckan_url'], u'group/{}'.format(self.name))

    def get_title(self, ctx):
        return self.title or self.name or self._id

    @classmethod
    def make_id_or_name_or_words_to_instance(cls):
        def id_or_name_or_words_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            match = uuid_re.match(value)
            if match is None:
                self = cls.find_one(dict(name = value), as_class = collections.OrderedDict)
            else:
                self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                slug = strings.slugify(value)
                words = sorted(set(slug.split(u'-')))
                instances = list(cls.find(
                    dict(
                        words = {'$all': [
                            re.compile(u'^{}'.format(re.escape(word)))
                            for word in words
                            ]},
                        ),
                    as_class = collections.OrderedDict,
                    ).limit(2))
                if not instances:
                    return value, state._(u"No group with ID, name or words: {0}").format(value)
                if len(instances) > 1:
                    return value, state._(u"Too much groups with words: {0}").format(u' '.join(words))
                self = instances[0]
            return self, None
        return id_or_name_or_words_to_instance

    def turn_to_json_attributes(self, state):
        value, error = conv.object_to_clean_dict(self, state = state)
        if error is not None:
            return value, error
        id = value.pop('_id', None)
        if id is not None:
            value['id'] = id
        return value, None


class Organization(objects.Initable, objects.JsonMonoClassMapper, objects.Mapper, objects.SmartWrapper):
    alerts = None
    collection_name = u'organizations'
    words = None

    # CKAN attributes
    created = None
    description = None
    image_url = None
    name = None
    revision_id = None
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

    def compute_words(self):
        self.words = sorted(set(strings.slugify(u'-'.join(
            fragment
            for fragment in (
                self._id,
                texthelpers.textify_markdown(self.description),
                self.title,
                )
            if fragment is not None
            )).split(u'-'))) or None

    @classmethod
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'organizations', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'organizations', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_full_url(ctx, self.name or self._id, *path, **query)

    def get_admin_url(self, ctx, *path, **query):
        if self._id is None and self.name is None:
            return None
        return self.get_admin_class_url(ctx, self.name or self._id, *path, **query)

    def get_back_url(self, ctx):
        if self.name is None:
            return None
        return urlparse.urljoin(conf['ckan_url'], u'organization/{}'.format(self.name))

    @classmethod
    def get_class_back_url(cls, ctx):
        return urlparse.urljoin(conf['ckan_url'], u'organization')

    @classmethod
    def get_class_front_url(cls, ctx, *path, **query):
        return urlparse.urljoin(conf['weckan_url'], u'organization')

    def get_front_url(self, ctx, *path, **query):
        if self.name is None:
            return None
        return urlparse.urljoin(conf['weckan_url'], u'organization/{}'.format(self.name))

    def get_title(self, ctx):
        return self.title or self.name or self._id

    @classmethod
    def make_id_or_name_or_words_to_instance(cls):
        def id_or_name_or_words_to_instance(value, state = None):
            if value is None:
                return value, None
            if state is None:
                state = conv.default_state
            match = uuid_re.match(value)
            if match is None:
                self = cls.find_one(dict(name = value), as_class = collections.OrderedDict)
            else:
                self = cls.find_one(value, as_class = collections.OrderedDict)
            if self is None:
                slug = strings.slugify(value)
                words = sorted(set(slug.split(u'-')))
                instances = list(cls.find(
                    dict(
                        words = {'$all': [
                            re.compile(u'^{}'.format(re.escape(word)))
                            for word in words
                            ]},
                        ),
                    as_class = collections.OrderedDict,
                    ).limit(2))
                if not instances:
                    return value, state._(u"No account with ID, name or words: {0}").format(value)
                if len(instances) > 1:
                    return value, state._(u"Too much accounts with words: {0}").format(u' '.join(words))
                self = instances[0]
            return self, None
        return id_or_name_or_words_to_instance

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
    def get_admin_class_full_url(cls, ctx, *path, **query):
        return urls.get_full_url(ctx, 'admin', 'sessions', *path, **query)

    @classmethod
    def get_admin_class_url(cls, ctx, *path, **query):
        return urls.get_url(ctx, 'admin', 'sessions', *path, **query)

    def get_admin_full_url(self, ctx, *path, **query):
        if self.token is None:
            return None
        return self.get_admin_class_full_url(ctx, self.token, *path, **query)

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
        if self._user is UnboundLocalError:
            self._user = Account.find_one(self.user_id) if self.user_id is not None else None
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
    Account.ensure_index('email')
    Account.ensure_index('name', unique = True)
    Account.ensure_index('words')

    Dataset.ensure_index('name', unique = True)
    Dataset.ensure_index('related.id')
    Dataset.ensure_index('related.owner_id')
    Dataset.ensure_index('timestamp')
    Dataset.ensure_index('words')

    Group.ensure_index('name', unique = True)
    Group.ensure_index('users.id')
    Group.ensure_index('words')

    Organization.ensure_index('name', unique = True)
    Organization.ensure_index('users.id')
    Organization.ensure_index('words')

    Session.ensure_index('expiration')
    Session.ensure_index('token', unique = True)
