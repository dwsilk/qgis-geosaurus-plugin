# -*- coding: utf-8 -*-

from ...core import database as db
from ..enums import (
    ReturnType, SpatialFunctionGroup, SpatialType)
from ..template import AbstractSpatialFunction


class LineSubstring(AbstractSpatialFunction):
    """
    ST_LineSubstring
    """

    def __init__(self, startfraction=0, endfraction=1):
        self._startfraction = startfraction
        self._endfraction = endfraction

    @property
    def startfraction(self):
        return self._startfraction

    @startfraction.setter
    def startfraction(self, value):
        self._startfraction = value

    @property
    def endfraction(self):
        return self._endfraction

    @endfraction.setter
    def endfraction(self, value):
        self._startfraction = value

    @classmethod
    def function_name(cls):
        return "ST_LineSubstring"

    @classmethod
    def alias_name(cls):
        return [
            "ST_Line_Substring", "2.0.x"
        ]

    @classmethod
    def function_group(cls):
        return SpatialFunctionGroup.EDITORS

    @classmethod
    def function_help(cls):
        return "https://postgis.net/docs/ST_LineSubstring.html"

    @classmethod
    def start_postgis_version(cls):
        return "1.1.1"

    @classmethod
    def spatial_type_support(cls):
        return [
            SpatialType.GEOMETRY,
            SpatialType.HAS_Z_OR_M,
        ]

    @classmethod
    def return_type(cls):
        return ReturnType.GEOMETRY

    def execute_query(self, wkt):
        output = db.execute("""
            SELECT ST_AsText(ST_LineSubstring(ST_GeomFromText(%s), %s, %s));
        """, (wkt, self.startfraction, self.endfraction, ))
        return output

    def sample_query_as_text(self, wkt):
        return """
            SELECT ST_AsText(ST_LineSubstring(ST_GeomFromText('{0}'), {1:.2f}, {2:.2f}))
        """.format(wkt, self.startfraction, self.endfraction, )
