# -*- coding: utf-8 -*-


class ReturnType:
    GEOMETRY = 1
    TEXT = 2
    BOOLEAN = 3


class SpatialFunctionGroup:
    ACCESSORS = 1
    CONSTRUCTORS = 2
    EDITORS = 3
    LINEAR_REFERENCING = 4
    MEASUREMENTS = 5
    OPERATORS = 6
    OUTPUTS = 7
    PROCESSING = 8
    RELATIONSHIPS = 9


class SpatialType:
    GEOMETRY = 1
    GEOGRAPHY = 2
    HAS_Z_OR_M = 3
    CURVES = 4
    SQL_MM = 5
    POLYHEDRAL = 6
    TRIANGLES_OR_TIN = 7
