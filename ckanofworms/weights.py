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


"""Helpers to compute ranking of datasets"""


import math


def compute_dataset_weight(dataset):
    # Compute certified public service weight
# TODO once we have the flag organization.certified_public_service
#    organization_id = dataset.owner_org
#    if organization_id is not None:
#        certified_public_service = model.Session.query(plugin_model.CertifiedPublicService).filter(
#            plugin_model.CertifiedPublicService.organization_id == organization_id,
#            ).first()
#    else:
#        certified_public_service = None
#    certified_weight = 2.0 if certified_public_service is not None else 0.5
    certified_weight = 1.0

    # Compute related weight.
    related_weight = 1.0 + len(dataset.related or [])
    related_weight = normalize_weight(related_weight)

    # Compute temporal weight.
#    temporal_coverage_from = dataset.temporal_coverage_from
#    year_from = temporal_coverage_from.split('-', 1)[0] if temporal_coverage_from is not None else None
#    temporal_coverage_to = dataset.temporal_coverage_to
#    year_to = temporal_coverage_to.split('-', 1)[0] if temporal_coverage_to is not None else None
#    if not year_from:
#        if year_to:
#            covered_years = [year_to]
#        else:
#            covered_years = []
#    elif not year_to:
#        covered_years = [year_from]
#    else:
#        year_from, year_to = sorted([year_from, year_to])
#        covered_years = [
#            str(year)
#            for year in range(int(year_from), int(year_to) + 1)
#            ]
#    # When no temporal coverage is given, consider that it is less than a year (0.9), to boost datasets with a
#    # temporal coverage.
#    temporal_weight = max(0.9, len(covered_years))
#    temporal_weight = normalize_weight(temporal_weight)
    temporal_weight = 1.0

    # Compute a weight between 0 and 1.
    dataset.weight = (
        certified_weight
        * related_weight ** 2
        * temporal_weight
        * compute_territorial_weight(dataset) ** 2
        * compute_territorial_granularity_weight(dataset)
        )


def compute_territorial_granularity_weight(dataset):
    territorial_coverage_granularity = dataset.territorial_coverage_granularity
    if territorial_coverage_granularity:
        territorial_coverage_granularity = {
            'poi': 'CommuneOfFrance',
            'iris': 'CommuneOfFrance',
            'commune': 'CommuneOfFrance',
            'canton': 'CantonOfFrance',
            'epci': 'IntercommunalityOfFrance',
            'department': 'DepartmentOfFrance',
            'region': 'RegionOfFrance',
            'france': 'Country',
            }.get(territorial_coverage_granularity, territorial_coverage_granularity)
        territorial_granularity_weight = dict(
            ArrondissementOfCommuneOfFrance = 36700.0,
            ArrondissementOfFrance = 342.0,
            AssociatedCommuneOfFrance = 36700.0,
            CantonalFractionOfCommuneOfFrance = 36700.0,
            CantonCityOfFrance = 3785.0,
            CantonOfFrance = 4055.0,
            CatchmentAreaOfFrance = 1666.0,
            CommuneOfFrance = 36700.0,
            Country = 1.0,
            DepartmentOfFrance = 101.0,
            EmploymentAreaOfFrance = 322.0,
            IntercommunalityOfFrance = 2582.0,
            InternationalOrganization = 1.0,
            JusticeAreaOfFrance = 316.0,  # TODO: Justice areas have not the same size.
            MetropoleOfCountry = 27.0,
            Mountain = (36700.0 * 7.0) / 8857.0,
            OverseasCollectivityOfFrance = 109.0,
            OverseasOfCountry = 27.0 / 5.0,
            PaysOfFrance = (36700.0 * 358.0) / 28849.0,
            RegionalNatureParkOfFrance = (36700.0 * 47.0) / 4126.0,
            RegionOfFrance = 27.0,
            UrbanAreaOfFrance = 796.0,
            UrbanTransportsPerimeterOfFrance = (36700.0 * 297.0) / 4077.0,
            UrbanUnitOfFrance = 2390.0,
            ).get(territorial_coverage_granularity, 0.0)
    else:
        territorial_granularity_weight = 0.0
    # Ensure that territorial_granularity is beween 0.5 and 2.0.
    territorial_granularity_weight *= 1.5 / 36700.0
    territorial_granularity_weight += 0.5
    return territorial_granularity_weight


def compute_territorial_weight(dataset, *local_kinds):
    territorial_coverage = dataset.territorial_coverage
    if territorial_coverage:
        # When local_kinds is empty, compute a territorial_weight between 0 and 1, except when kind belongs to
        # local_kinds where it equals 2.
        # When local_kinds is not empty, compute a territorial_weight between 0 and 2.
        territorial_weight = 0
        for covered_kind in (
                covered_territory.split('/', 1)[0]
                for covered_territory in territorial_coverage.split(',')
                if covered_territory
                ):
            if covered_kind in local_kinds:
                return 2.0
            territorial_weight += dict(
                ArrondissementOfCommuneOfFrance = 1.0 / 36700.0,
                ArrondissementOfFrance = 1.0 / 342.0,
                AssociatedCommuneOfFrance = 1.0 / 36700.0,
                CantonalFractionOfCommuneOfFrance = 1.0 / 36700.0,
                CantonCityOfFrance = 1.0 / 3785.0,
                CantonOfFrance = 1.0 / 4055.0,
                CatchmentAreaOfFrance = 1.0 / 1666.0,
                CommuneOfFrance = 1.0 / 36700.0,
                Country = 1.0,
                DepartmentOfFrance = 1.0 / 101.0,
                EmploymentAreaOfFrance = 1.0 / 322.0,
                IntercommunalityOfFrance = 1.0 / 2582.0,
                InternationalOrganization = 1.0,
                JusticeAreaOfFrance = 1.0 / 316.0,  # TODO: Justice areas have not the same size.
                MetropoleOfCountry = 22.0 / 27.0,
                Mountain = 8857.0 / (36700.0 * 7.0),
                OverseasCollectivityOfFrance = 1.0 / 109.0,
                OverseasOfCountry = 5.0 / 27.0,
                PaysOfFrance = 28849.0 / (36700.0 * 358.0),
                RegionalNatureParkOfFrance = 4126.0 / (36700.0 * 47.0),
                RegionOfFrance = 1.0 / 27.0,
                UrbanAreaOfFrance = 1.0 / 796.0,
                UrbanTransportsPerimeterOfFrance = 4077.0 / (36700.0 * 297.0),
                UrbanUnitOfFrance = 1.0 / 2390.0,
                ).get(covered_kind, 1.0 / 40000.0)
            if territorial_weight >= 1.0:
                territorial_weight = 1.0
                break
    else:
        # When no territorial coverage is given, consider that it is less than a commune.
        territorial_weight = 1.0 / 40000.0
    # Note: territorial_weight is between 0 and 1.
    if local_kinds:
        # Ensure that territorial_weight is between 0.5 and 1.
        territorial_weight /= 2.0
        territorial_weight += 0.5
    else:
        # Ensure that territorial_weight is between 0.5 and 2.
        territorial_weight *= 1.5
        territorial_weight += 0.5
    return territorial_weight


def normalize_weight(weight):
    # Convert a weight between 0 and infinite to a number between 0.5 and 2.
    # cf http://en.wikipedia.org/wiki/Inverse_trigonometric_functions
    return math.atan(weight) * 3 / math.pi + 0.5
