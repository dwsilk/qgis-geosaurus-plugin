# -*- coding: utf-8 -*-

import csv
import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, Qt, QVariant
from PyQt4.QtGui import QDialog

from qgis.core import (
    edit, QGis, QgsFeature, QgsFeatureRequest, QgsField, QgsGeometry,
    QgsMapLayerRegistry, QgsVectorLayer, QgsVectorFileWriter,
    QgsCurvePolygonV2
)
from qgis.gui import QgsRubberBand
from qgis.utils import iface

from ..postgis import (
    select_one_geom, select_buffer, postgis_version,
    select_one_geom_return_text, select_scale
)

END_CAP_ENUM = ["round", "flat", "square"]
JOIN_ENUM = ["round", "mitre", "bevel"]

GEOM_RETURNING_FUNCTIONS = [
    "ST_Boundary",
    "ST_Buffer",
    "ST_BuildArea",
    "ST_Centroid",
    "ST_ConvexHull",
    "ST_EndPoint",
    "ST_Envelope",
    "ST_FlipCoordinates",
    "ST_MakeLine",
    "ST_MakePolygon",
    # "ST_MinimumClearanceLine",
    "ST_PointOnSurface",
    "ST_Reverse",
    "ST_Scale",
    "ST_StartPoint",
]

TEXT_RETURNING_FUNCTIONS = [
    "ST_Area",
    "ST_CoordDim",
    "ST_Dimension",
    "ST_GeometryType",
    "ST_IsClosed",
    "ST_IsCollection",
    "ST_IsEmpty",
    "ST_IsRing",
    "ST_IsSimple",
    "ST_IsValid",
    "ST_IsValidReason",
    "ST_IsValidDetail",
    "ST_Length",
    "ST_NDims",
    "ST_NPoints",
    "ST_NRings",
    "ST_NumGeometries",
    "ST_NumInteriorRings",
    "ST_NumPoints",
    "ST_Perimeter",
    "ST_SRID",
    "ST_Summary",
    "ST_X",
    "ST_XMax",
    "ST_XMin",
    "ST_Y",
    "ST_YMax",
    "ST_YMin",
]

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), "dialog.ui"))


class GeosaurusDialog(QDialog, FORM_CLASS):

    closingDialog = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(GeosaurusDialog, self).__init__(parent)
        self.setupUi(self)

        self.populate_postgis_combo()
        self.update_postgis_version()
        self.cmb_end_cap.addItems(END_CAP_ENUM)
        self.cmb_join.addItems(JOIN_ENUM)

        self.cmb_postgis_function.currentIndexChanged.connect(self.update_ui)
        self.cmb_postgis_function.currentIndexChanged.connect(self.display_result)

        # Buffer Signals
        self.sld_distance.valueChanged.connect(self.display_result)
        self.sld_segments.valueChanged.connect(self.display_result)
        self.sld_mitre.valueChanged.connect(self.display_result)
        self.cmb_end_cap.currentIndexChanged.connect(self.display_result)
        self.cmb_join.currentIndexChanged.connect(self.display_result)

        # Scale Signals
        self.sld_scale_x.valueChanged.connect(self.display_result)
        self.sld_scale_y.valueChanged.connect(self.display_result)

        self.point_lyr = self.prepare_memory_layer("Point", "Geosaurus Point")
        self.linestring_lyr = self.prepare_memory_layer("LineString", "Geosaurus LineString")
        self.polygon_lyr = self.prepare_memory_layer("Polygon", "Geosaurus Polygon")
        self.add_memory_layer_to_map(self.point_lyr)
        self.add_memory_layer_to_map(self.linestring_lyr)
        self.add_memory_layer_to_map(self.polygon_lyr)

        self.add_features(self.linestring_lyr)
        self.linestring_lyr.updateExtents()

        self.stk_params.hide()
        self.rubberbands = []

    def populate_layer_combo(self, combo_box):
        """Not used"""
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            combo_box.addItem(lyr.name())

    def populate_postgis_combo(self):
        self.cmb_postgis_function.addItems(GEOM_RETURNING_FUNCTIONS)
        self.cmb_postgis_function.addItems(TEXT_RETURNING_FUNCTIONS)

    def update_postgis_version(self):
        self.lbl_postgis_function.setText("PostGIS Version: {} - Docs".format(postgis_version()))

    def build_buffer_params(self):
        buffer_params = ""
        if self.sld_segments.value() != 8:
            buffer_params += "quad_segs={} ".format(self.sld_segments.value())
        if self.cmb_end_cap.currentText() != "round":
            buffer_params += "endcap={} ".format(self.cmb_end_cap.currentText())
        if self.cmb_join.currentText() != "round":
            buffer_params += "join={} ".format(self.cmb_join.currentText())
        if self.cmb_join.currentText() == "mitre" and self.sld_mitre.value() != 5:
            buffer_params += "mitre_limit={}.0".format(self.sld_mitre.value())
        buffer_params.rstrip()
        return buffer_params

    @staticmethod
    def prepare_memory_layer(geometry_type, name):
        """Prepare memory layers that will be used to display tests"""
        lyr = QgsVectorLayer(geometry_type, name, "memory")
        provider = lyr.dataProvider()
        with edit(lyr):
            provider.addAttributes([
                QgsField("id", QVariant.Int),
                QgsField("group_id", QVariant.Int),
                QgsField("description", QVariant.String),
                QgsField("result", QVariant.String),
            ])
        lyr.updateFields()
        return lyr

    @staticmethod
    def add_memory_layer_to_map(lyr):
        QgsMapLayerRegistry.instance().addMapLayer(lyr)

    @staticmethod
    def delete_features_from_lyr(lyr):
        """Delete all features from a layer"""
        with edit(lyr):
            ids = [feat.id() for feat in lyr.getFeatures()]
            lyr.deleteFeatures(ids)

    @staticmethod
    def add_features(lyr):
        linestring_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "wkt", "linestring_examples.wkt")
        print linestring_path

        with open(linestring_path, "rb") as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            feature_attr_rows = list(reader)[1:]

        with edit(lyr):
            feats = []
            count_feats = 0
            translate_x = 0
            translate_y = 0
            for row in feature_attr_rows:
                attrs = row[0:4]
                geom = QgsGeometry.fromWkt(row[4])
                if count_feats == 6:
                    translate_x = 0
                    translate_y += -0.002
                    count_feats = 0
                geom.translate(translate_x, translate_y)
                translate_x += 0.002
                count_feats += 1
                feat = QgsFeature()
                feat.setGeometry(geom)
                feat.setAttributes(attrs)
                feats.append(feat)
            lyr.addFeatures(feats, False)

    def update_ui(self):
        postgis_function = self.cmb_postgis_function.currentText()
        if postgis_function == "ST_Buffer":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(0)
        elif postgis_function == "ST_Scale":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(1)
        else:
            self.stk_params.hide()

    def display_result(self):
        for x in self.rubberbands:
            x.reset()
        self.rubberbands = []

        self.txtb_result.setText("")

        lyr = self.linestring_lyr
        with edit(lyr):
            for f in lyr.getFeatures():
                g_wkt = f.geometry().exportToWkt()
                postgis_function = self.cmb_postgis_function.currentText()
                if postgis_function == "ST_Buffer":
                    buffer_params = self.build_buffer_params()
                    self.display_query(g_wkt, self.sld_distance.value()*0.00001, buffer_params)
                    new_g_wkt = select_buffer(g_wkt, self.sld_distance.value()*0.00001, buffer_params)[0]
                    self.txtb_result.setText(new_g_wkt)
                elif postgis_function == "ST_Scale":
                    self.display_query(g_wkt, self.sld_scale_x.value()*0.04, self.sld_scale_y.value()*0.04)
                    new_g_wkt = select_scale(g_wkt, self.sld_scale_x.value()*0.04, self.sld_scale_y.value()*0.04)[0]
                    self.txtb_result.setText(new_g_wkt)
                elif postgis_function in GEOM_RETURNING_FUNCTIONS:
                    self.display_query(g_wkt, postgis_function)
                    new_g_wkt = select_one_geom(postgis_function, g_wkt)[0]
                    self.txtb_result.setText(new_g_wkt)
                else:
                    text_result = select_one_geom_return_text(postgis_function, g_wkt)[0]
                    self.txtb_result.setText(text_result)
                    lyr.changeAttributeValue(f.id(), 3, text_result)
                    continue

                new_g = QgsGeometry.fromWkt(new_g_wkt)

                if new_g:
                    if new_g.type() == 2:  # Polygon
                        new_ag = new_g.geometry()
                        if new_ag.numInteriorRings() > 0:
                            new_ig = QgsGeometry.fromWkt(new_ag.interiorRing(0).asWkt())

                            r = QgsRubberBand(iface.mapCanvas(), QGis.Line)
                            r.setToGeometry(new_ig, lyr)
                            r.setBorderColor(Qt.darkBlue)
                            r.setWidth(5)
                            r.show()

                            r2 = QgsRubberBand(iface.mapCanvas(), QGis.Line)
                            r2.setToGeometry(new_ig, lyr)
                            r2.setBorderColor(Qt.white)
                            r2.setWidth(2)
                            r2.show()

                            self.rubberbands.append(r)
                            self.rubberbands.append(r2)

                    # poly = new_g.asPolygon()
                    # print poly
                    # print "Rings: {}".format(poly.numInteriorRings())
                    # if poly.numInteriorRings() > 0:
                    #     print poly.interiorRing(1)

                    r = QgsRubberBand(iface.mapCanvas(), QGis.Polygon)
                    r.setToGeometry(new_g, lyr)
                    r.setBorderColor(Qt.darkBlue)
                    r.setWidth(5)
                    r.show()

                    r2 = QgsRubberBand(iface.mapCanvas(), QGis.Polygon)
                    r2.setToGeometry(new_g, lyr)
                    r2.setBorderColor(Qt.white)
                    r2.setWidth(2)
                    r2.show()

                    self.rubberbands.append(r)
                    self.rubberbands.append(r2)

    def display_query(self, *args):
        postgis_function = self.cmb_postgis_function.currentText()
        if postgis_function == "ST_Buffer":
            wkt = args[0]
            distance = args[1]
            buffer_string = args[2]
            self.txtb_query.setText("SELECT ST_AsText(ST_Buffer(ST_GeomFromText('{0}', {1:.5f}, '{2}')))".format(wkt, distance, buffer_string))
        elif postgis_function == "ST_Scale":
            wkt = args[0]
            scale_x = args[1]
            scale_y = args[2]
            self.txtb_query.setText("SELECT ST_AsText(ST_Scale(ST_GeomFromText'{0}', {1:.2f}, {2:.2f})))".format(wkt, scale_x, scale_y))
        else:
            wkt = args[0]
            function_name = args[1]
            self.txtb_query.setText("SELECT ST_AsText({1}(ST_GeomFromText('{0}')))".format(wkt, function_name))

    def closeEvent(self, event):
        self.closingDialog.emit()
        event.accept()
