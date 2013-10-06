## -*- coding: utf-8 -*-


## CKAN-of-Worms -- A logger for errors found in CKAN datasets
## By: Emmanuel Raviart <emmanuel@raviart.com>
##
## Copyright (C) 2013 Etalab
## http://github.com/etalab/ckan-of-worms
##
## This file is part of CKAN-of-Worms.
##
## CKAN-of-Worms is free software; you can redistribute it and/or modify
## it under the terms of the GNU Affero General Public License as
## published by the Free Software Foundation, either version 3 of the
## License, or (at your option) any later version.
##
## CKAN-of-Worms is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU Affero General Public License for more details.
##
## You should have received a copy of the GNU Affero General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.


<%!
import copy
import json

from ckanofworms import model, urls
%>


<%inherit file="/object-admin-view.mako"/>


<%def name="breadcrumb_content()" filter="trim">
            <%parent:breadcrumb_content/>
            <li><a href="${urls.get_url(ctx, 'admin')}">${_(u"Admin")}</a></li>
            <li><a href="${model.Dataset.get_admin_class_url(ctx)}">${_(u"Datasets")}</a></li>
            <li class="active">${dataset.get_title(ctx)}</li>
</%def>


<%def name="container_content()" filter="trim">
        <h2>${dataset.get_title(ctx)}</h2>
        <%self:view_fields/>
        <div class="btn-toolbar">
            <a class="btn btn-default" href="${dataset.get_front_url(ctx)}" target="_blank">${_(u'View in Front')}</a>
            <a class="btn btn-default" href="${dataset.get_back_url(ctx)}" target="_blank">${_(u'View in Back')}</a>
            <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'stats')}">${_(u'Statistics')}</a>
            <a class="btn btn-default" href="${urls.get_url(ctx, 'api', 1, 'datasets', dataset._id)}">${_(u'JSON')}</a>
            <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'publish')}">${_(u'Publish')}</a>
##            <a class="btn btn-default" href="${dataset.get_admin_url(ctx, 'edit')}">${_(u'Edit')}</a>
##            <a class="btn btn-danger"  href="${dataset.get_admin_url(ctx, 'delete')}"><span class="glyphicon glyphicon-trash"></span> ${_('Delete')}</a>
        </div>
</%def>


<%def name="title_content()" filter="trim">
${dataset.get_title(ctx)} - ${parent.title_content()}
</%def>


<%def name="view_fields()" filter="trim">
<%
    dataset_errors = copy.deepcopy(dataset.errors) if dataset.errors is not None else {}
%>\
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
            <div class="col-sm-10">${dataset.name}</div>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(dataset_errors, 'name')}"/>
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
            <div class="col-sm-10">${dataset.title}</div>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(dataset_errors, 'title')}"/>
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'notes')
        value = dataset.notes
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Notes"))}</b></div>
            <pre class="break-word col-sm-10">${value}</pre>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
    resources_errors = self.attr.extract_item_errors(dataset_errors, 'resources')
%>\
    % if dataset.resources or resources_errors:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Resources"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for resource_index, resource in enumerate(dataset.resources or []):
<%
            resource_errors = self.attr.extract_item_errors(resources_errors, resource_index)
%>\
            <li class="list-group-item">
<%
            errors = self.attr.extract_item_errors(resource_errors, 'name')
            value = resource.get('name')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(resource_errors, 'description')
            value = resource.get('description')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
                    <pre class="break-word col-sm-10">${value}</pre>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(resource_errors, 'url')
            value = resource.get('url')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("URL"))}</b></div>
                    <div class="break-word col-sm-10"><a href="${value}">${value}</a></div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(resource_errors, 'format')
            value = resource.get('format')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Format"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(resource_errors, 'last_modified')
            value = resource.get('last_modified')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Last Modified"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(resource_errors, 'created')
            value = resource.get('created')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            remaining_keys = set()
            for author, author_errors in resource_errors.iteritems():
                remaining_keys.update(author_errors['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(resource.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_error errors="${self.attr.extract_item_errors(resource_errors, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_error errors="${resources_errors}"/>
    % endif
<%
    extras_errors = self.attr.extract_item_errors(dataset_errors, 'extras')
%>\
    % if dataset.extras or extras_errors:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Extras"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for extra_index, extra in enumerate(dataset.extras or []):
<%
            extra_errors = self.attr.extract_item_errors(extras_errors, extra_index)
%>\
            <li class="list-group-item">
<%
            errors = self.attr.extract_item_errors(extra_errors, 'key')
            value = extra.get('key')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Key"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(extra_errors, 'value')
            value = extra.get('value')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Value"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            remaining_keys = set()
            for author, author_errors in extra_errors.iteritems():
                remaining_keys.update(author_errors['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(extra.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_error errors="${self.attr.extract_item_errors(extra_errors, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_error errors="${extras_errors}"/>
    % endif
<%
        # TODO: Replace with groups_id.
        groups_errors = self.attr.extract_item_errors(dataset_errors, 'groups')
%>\
    % if dataset.groups or groups_errors:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Groups"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for group_index, group_attributes in enumerate(dataset.groups or []):
<%
            group_errors = self.attr.extract_item_errors(groups_errors, group_index)
%>\
            <li class="list-group-item">
<%
            errors = self.attr.extract_item_errors(group_errors, 'id')
            value = group_attributes.get('id')
            group = model.Group.find_one(value) if value is not None else None
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("ID"))}</b></div>
                    <div class="col-sm-10">
                    % if group is None:
                        ${value}
                    % else:
                        <a href="${group.get_admin_url(ctx)}">${group.get_title(ctx)}</a>
                    % endif
                    </div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            remaining_keys = set()
            for author, author_errors in group_errors.iteritems():
                remaining_keys.update(author_errors['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(group_attributes.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_error errors="${self.attr.extract_item_errors(group_errors, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_error errors="${groups_errors}"/>
    % endif
<%
        # TODO: Replace list of dicts with a list of strings.
        tags_errors = self.attr.extract_item_errors(dataset_errors, 'tags')
%>\
    % if dataset.tags or tags_errors:
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Tags"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for tag_index, tag in enumerate(dataset.tags or []):
<%
            tag_errors = self.attr.extract_item_errors(tags_errors, tag_index)
%>\
            <li class="list-group-item">
<%
            errors = self.attr.extract_item_errors(tag_errors, 'name')
            value = tag.get('name')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Name"))}</b></div>
                    <div class="col-sm-10">
                        <a href="${model.Dataset.get_admin_class_url(ctx, tag = value)}">${value}</a>
                    </div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            remaining_keys = set()
            for author, author_errors in tag_errors.iteritems():
                remaining_keys.update(author_errors['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(tag.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_error errors="${self.attr.extract_item_errors(tag_errors, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_error errors="${tags_errors}"/>
    % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'temporal_coverage_from')
        value = dataset.temporal_coverage_from
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Temporal Coverage From"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'temporal_coverage_to')
        value = dataset.temporal_coverage_to
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Temporal Coverage To"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'territorial_coverage')
        value = dataset.territorial_coverage
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Territorial Coverage"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'territorial_coverage_granularity')
        value = dataset.territorial_coverage_granularity
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Territorial Coverage Granularity"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'owner_org')
        value = dataset.owner_org
        organization = model.Organization.find_one(value) if value is not None else None
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Organization"))}</b></div>
            <div class="col-sm-10">
            % if organization is None:
                ${value}
            % else:
                <a href="${organization.get_admin_url(ctx)}">${organization.get_title(ctx)}</a>
            % endif
            </div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'author')
        value = dataset.author
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Office, Department or Service"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'author_email')
        value = dataset.author_email
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Contact Email"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'maintainer')
        value = dataset.maintainer
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Maintainer"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'maintainer_email')
        value = dataset.maintainer_email
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Maintainer Email"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'supplier_id')
        value = dataset.supplier_id
        organization = model.Organization.find_one(value) if value is not None else None
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Supplier"))}</b></div>
            <div class="col-sm-10">
            % if organization is None:
                ${value}
            % else:
                <a href="${organization.get_admin_url(ctx)}">${organization.get_title(ctx)}</a>
            % endif
            </div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'license_id')
        value = dataset.license_id
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("License"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'metadata_modified')
        value = dataset.metadata_modified
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Metadata Modified"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'metadata_created')
        value = dataset.metadata_created
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Metadata Created"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'revision_timestamp')
        value = dataset.revision_timestamp
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Revision Timestamp"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'timestamp')
        value = dataset.timestamp
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Timestamp"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
<%
        errors = self.attr.extract_item_errors(dataset_errors, 'revision_id')
        value = dataset.revision_id
%>\
        % if value is not None or errors:
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Revision ID"))}</b></div>
            <div class="col-sm-10">${value}</div>
        </div>
        <%self:field_error errors="${errors}"/>
        % endif
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("ID"))}</b></div>
            <div class="col-sm-10">${dataset._id}</div>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(dataset_errors, 'id')}"/>
<%
    related_links_errors = self.attr.extract_item_errors(dataset_errors, 'related')
%>\
 <%
    remaining_keys = set()
    for author, author_errors in dataset_errors.iteritems():
        remaining_keys.update(author_errors['error'].iterkeys())
%>\
    % for key in sorted(remaining_keys):
       <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
            <pre class="col-sm-10">${json.dumps(getattr(dataset, key, None),
                    encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
        </div>
        <%self:field_error errors="${self.attr.extract_item_errors(dataset_errors, key)}"/>
    % endfor
   % if dataset.related or related_links_errors:
        <h3>${u"Community Resources"}</h3>
        <div class="row">
            <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Related"))}</b></div>
            <ul class="col-sm-10 list-group">
        % for related_link_index, related_link in enumerate(dataset.related or []):
<%
            related_link_errors = self.attr.extract_item_errors(related_links_errors, related_link_index)
%>\
            <li class="list-group-item">
<%
            errors = self.attr.extract_item_errors(related_link_errors, 'title')
            value = related_link.get('title')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Title"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(related_link_errors, 'description')
            value = related_link.get('description')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Description"))}</b></div>
                    <pre class="break-word col-sm-10">${value}</pre>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(related_link_errors, 'url')
            value = related_link.get('url')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("URL"))}</b></div>
                    <div class="break-word col-sm-10"><a href="${value}">${value}</a></div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(related_link_errors, 'image_url')
            value = related_link.get('image_url')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Image"))}</b></div>
                    <div class="break-word col-sm-10"><img class="img-responsive" src="${value}"></div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(related_link_errors, 'type')
            value = related_link.get('type')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Type"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(related_link_errors, 'owner_id')
            value = related_link.get('owner_id')
            account = model.Account.find_one(value) if value is not None else None
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Owner"))}</b></div>
                    <div class="col-sm-10">
                    % if account is None:
                        ${value}
                    % else:
                        <a href="${account.get_admin_url(ctx)}">${account.get_title(ctx)}</a>
                    % endif
                    </div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            errors = self.attr.extract_item_errors(related_link_errors, 'created')
            value = related_link.get('created')
%>\
            % if value is not None or errors:
                <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(_("Created"))}</b></div>
                    <div class="col-sm-10">${value}</div>
                </div>
                <%self:field_error errors="${errors}"/>
            % endif
<%
            remaining_keys = set()
            for author, author_errors in related_link_errors.iteritems():
                remaining_keys.update(author_errors['error'].iterkeys())
%>\
            % for key in sorted(remaining_keys):
               <div class="row">
                    <div class="col-sm-2 text-right"><b>${_(u'{0}:').format(key)}</b></div>
                    <pre class="col-sm-10">${json.dumps(related_link.get(key),
                            encoding = 'utf-8', ensure_ascii = False, indent = 2)}</pre>
                </div>
                <%self:field_error errors="${self.attr.extract_item_errors(related_link_errors, key)}"/>
            % endfor
            </li>
        % endfor
            </ul>
        </div>
        <%self:field_error errors="${related_links_errors}"/>
    % endif
</%def>

