# -*- coding: utf-8 -*-
"""
################################################################################
#
# Copyright 2016 Crown copyright (c)
# Land Information New Zealand and the New Zealand Government.
# All rights reserved
#
# This program is released under the terms of the 3 clause BSD license. See the
# LICENSE file for more information.
#
################################################################################

"""

import importlib


def create_spatial_function(function_name, kwargs):
    """Create instance of chosen spatial function class."""

    module = importlib.import_module("geosaurus.functions")
    spatial_function = getattr(module, function_name[3:])
    return spatial_function(**kwargs)
