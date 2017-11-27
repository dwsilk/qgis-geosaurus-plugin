# -*- coding: utf-8 -*-

from ...core import database as db
from ..enums import (
    ReturnType, SpatialFunctionGroup, SpatialType)
from ..template import AbstractSpatialFunction


class RotateX(AbstractSpatialFunction):
    """
    ST_RotateX
    """

    def __init__(self, radians=0):
        self._radians = radians

    @property
    def radians(self):
        return self._radians

    @radians.setter
    def radians(self, value):
        self._radians = value

    @classmethod
    def function_name(cls):
        return "ST_RotateX"

    @classmethod
    def alias_name(cls):
        return None

    @classmethod
    def function_group(cls):
        return SpatialFunctionGroup.EDITORS

    @classmethod
    def function_help(cls):
        return "https://postgis.net/docs/ST_RotateX.html"

    @classmethod
    def start_postgis_version(cls):
        return "1.2.2"

    @classmethod
    def spatial_type_support(cls):
        return [
            SpatialType.GEOMETRY,
            SpatialType.HAS_Z_OR_M,
            SpatialType.POLYHEDRAL,
            SpatialType.TRIANGLES_OR_TIN
        ]

    @classmethod
    def return_type(cls):
        return ReturnType.GEOMETRY

    def execute_query(self, wkt):
        output = db.execute("""
            SELECT ST_AsText(ST_RotateX(ST_GeomFromText(%s), %s));
        """, (wkt, self.radians, ))
        return output

    def sample_query_as_text(self, wkt):
        return """
            SELECT ST_AsText(ST_RotateX(ST_GeomFromText('{0}'), {1}))
        """.format(wkt, self.radians)
