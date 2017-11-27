# -*- coding: utf-8 -*-

from ...core import database as db
from ..enums import (
    ReturnType, SpatialFunctionGroup, SpatialType)
from ..template import AbstractSpatialFunction


class Scale(AbstractSpatialFunction):
    """
    ST_Scale
    """

    def __init__(self, xfactor=0, yfactor=0):
        self._xfactor = xfactor
        self._yfactor = yfactor

    @property
    def xfactor(self):
        return self._xfactor

    @xfactor.setter
    def xfactor(self, value):
        self._xfactor = value

    @property
    def yfactor(self):
        return self._yfactor

    @yfactor.setter
    def yfactor(self, value):
        self._yfactor = value

    @classmethod
    def function_name(cls):
        return "ST_Scale"

    @classmethod
    def alias_name(cls):
        return None

    @classmethod
    def function_group(cls):
        return SpatialFunctionGroup.EDITORS

    @classmethod
    def function_help(cls):
        return "https://postgis.net/docs/ST_Scale.html"

    @classmethod
    def start_postgis_version(cls):
        return "1.1.0"

    @classmethod
    def spatial_type_support(cls):
        return [
            SpatialType.GEOMETRY,
            SpatialType.HAS_Z_OR_M,
            SpatialType.CURVES,
            SpatialType.POLYHEDRAL,
            SpatialType.TRIANGLES_OR_TIN,
        ]

    @classmethod
    def return_type(cls):
        return ReturnType.GEOMETRY

    def execute_query(self, wkt):
        output = db.execute("""
            SELECT ST_AsText(ST_Scale(ST_GeomFromText(%s), %s, %s));
        """, (wkt, self.xfactor, self.yfactor, ))
        return output

    def sample_query_as_text(self, wkt):
        return """
            SELECT ST_AsText(ST_Scale(ST_GeomFromText('{0}'), {1:.2f}, {2:.2f}))
        """.format(wkt, self.xfactor, self.yfactor, )
