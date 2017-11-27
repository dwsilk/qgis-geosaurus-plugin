# -*- coding: utf-8 -*-

import re

from ...core import database as db
from ..enums import (
    ReturnType, SpatialFunctionGroup, SpatialType)
from ..template import AbstractSpatialFunction


class Buffer(AbstractSpatialFunction):
    """
    ST_Buffer
    """

    def __init__(self, distance=0, quad_segs=8, endcap="round", join="round",
                 mitre_limit=5.0, parameter_string=""):
        self._distance = distance
        self._quad_segs = quad_segs
        self._endcap = endcap
        self._join = join
        self._mitre_limit = mitre_limit
        self._parameter_string = parameter_string
        if self._parameter_string == "":
            pass

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, value):
        self._distance = value

    @property
    def quad_segs(self):
        return self._quad_segs

    @quad_segs.setter
    def quad_segs(self, value):
        self._quad_segs = value

    @property
    def endcap(self):
        return self._endcap

    @endcap.setter
    def endcap(self, value):
        self._endcap = value

    @property
    def join(self):
        return self._join

    @join.setter
    def join(self, value):
        self._join = value

    @property
    def mitre_limit(self):
        return self._mitre_limit

    @mitre_limit.setter
    def mitre_limit(self, value):
        self._mitre_limit = value

    @property
    def parameter_string(self):
        parameter_string = ""
        if self._quad_segs != 8:
            parameter_string += "quad_segs={} ".format(self._quad_segs)
        if self._endcap != "round":
            parameter_string += "endcap={} ".format(self._endcap)
        if self._join != "round":
            parameter_string += "join={} ".format(self._join)
        if self._join == "mitre" and self._mitre_limit != 5:
            parameter_string += "mitre_limit={}.0".format(self._mitre_limit)
        parameter_string.rstrip()
        return parameter_string

    @parameter_string.setter
    def parameter_string(self, value):
        if "quad_segs" in value:
            result = re.search(r"quad_segs=(.*)\b", value)
            if result.group(1):
                self.quad_segs = result.group(1)
        if "endcap" in value:
            result = re.search(r"endcap=(.*)\b", value)
            if result.group(1):
                self.endcap = result.group(1)
        if "join" in value:
            result = re.search(r"join=(.*)\b", value)
            if result.group(1):
                self.join = result.group(1)
        if "mitre_limit" in value:
            result = re.search(r"mitre_limit=(.*)\b", value)
            if result.group(1):
                self.mitre_limit = result.group(1)

    @classmethod
    def function_name(cls):
        return "ST_Buffer"

    @classmethod
    def alias_name(cls):
        return None

    @classmethod
    def function_group(cls):
        return SpatialFunctionGroup.PROCESSING

    @classmethod
    def function_help(cls):
        return "http://www.postgis.org/docs/ST_Buffer.html"

    @classmethod
    def start_postgis_version(cls):
        return "1.5.0"

    @classmethod
    def spatial_type_support(cls):
        return [
            SpatialType.GEOMETRY,
            SpatialType.SQL_MM,
        ]

    @classmethod
    def return_type(cls):
        return ReturnType.GEOMETRY

    def execute_query(self, wkt):
        if self.parameter_string:
            output = db.execute("""
                SELECT ST_AsText(ST_Buffer(ST_GeomFromText(%s), %s, %s));
            """, (wkt, self.distance, self.parameter_string, ))
        else:
            output = db.execute("""
                SELECT ST_AsText(ST_Buffer(ST_GeomFromText(%s), %s));
            """, (wkt, self.distance, ))
        return output

    def sample_query_as_text(self, wkt):
        return """
            SELECT ST_AsText(ST_Buffer(ST_GeomFromText('{0}', {1:.5f}, '{2}')))
        """.format(wkt, self.distance, self.parameter_string)
