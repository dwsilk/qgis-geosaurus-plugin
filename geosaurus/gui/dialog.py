# -*- coding: utf-8 -*-

import csv
import math
import os.path

from PyQt4 import uic
from PyQt4.QtCore import pyqtSignal, pyqtSlot, Qt, QVariant
from PyQt4.QtGui import QDialog

from qgis.core import (
    edit, QGis, QgsFeature, QgsFeatureRequest, QgsField, QgsGeometry,
    QgsMapLayerRegistry, QgsVectorLayer, QgsVectorFileWriter,
    QgsCurvePolygonV2
)
from qgis.gui import QgsRubberBand
from qgis.utils import iface

from ..core.postgis import (
    select_one_geom, postgis_version,
    select_one_geom_return_text,
)

from ..functions import SPATIAL_FUNCTION_CATEGORIES
from ..functions.factory import create_spatial_function

EPSG = 4326

END_CAP_ENUM = ["round", "flat", "square"]
JOIN_ENUM = ["round", "mitre", "bevel"]

OTHER_SUPPORTED_FUNCTIONS = [
    "ST_AddPoint",
    "ST_Segmentize",
    "ST_Buffer",
    "ST_Scale",
    "ST_LineSubstring",
    "ST_LineInterpolatePoint",
    "ST_RotateX",
    "ST_RotateY",
    "ST_OffsetCurve",
]

GEOM_RETURNING_FUNCTIONS = [
    "ST_Boundary",
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

        self.cmb_function_filter.addItems(sorted(SPATIAL_FUNCTION_CATEGORIES.keys()))
        self.cmb_function_filter.setCurrentIndex(1)  # All
        self.populate_postgis_combo()
        self.update_postgis_version()
        self.cmb_end_cap.addItems(END_CAP_ENUM)
        self.cmb_join.addItems(JOIN_ENUM)

        self.btn_single_geom.clicked.connect(self.single_geom_mode)
        self.btn_predicates.clicked.connect(self.predicate_mode)

        self.chk_point.stateChanged.connect(self.load_layers)
        self.chk_linestring.stateChanged.connect(self.load_layers)
        self.chk_polygon.stateChanged.connect(self.load_layers)
        self.chk_multipoint.stateChanged.connect(self.load_layers)
        self.chk_multilinestring.stateChanged.connect(self.load_layers)
        self.chk_multipolygon.stateChanged.connect(self.load_layers)

        self.cmb_base_relate.currentIndexChanged.connect(self.load_layers)
        self.cmb_compare_relate.currentIndexChanged.connect(self.load_layers)

        self.cmb_function_filter.currentIndexChanged.connect(self.populate_postgis_combo)

        self.cmb_postgis_function.currentIndexChanged.connect(self.update_ui)
        self.cmb_postgis_function.currentIndexChanged.connect(self.display_result)

        # Buffer Signals
        self.sld_distance.valueChanged.connect(self.update_ui)
        self.sld_segments.valueChanged.connect(self.update_ui)
        self.sld_mitre.valueChanged.connect(self.update_ui)
        self.cmb_end_cap.currentIndexChanged.connect(self.update_ui)
        self.cmb_join.currentIndexChanged.connect(self.update_ui)

        # Scale Signals
        self.sld_scale_x.valueChanged.connect(self.update_ui)
        self.sld_scale_y.valueChanged.connect(self.update_ui)

        # Rotate Signals
        self.sld_rotate.valueChanged.connect(self.update_ui)

        # Interpolate Signals
        self.sld_interpolate.valueChanged.connect(self.update_ui)
        self.sld_start_fraction.valueChanged.connect(self.update_ui)
        self.sld_end_fraction.valueChanged.connect(self.update_ui)

        # Concave Signals
        self.sld_concave.valueChanged.connect(self.update_ui)
        self.chk_holes.stateChanged.connect(self.update_ui)

        self.sld_latitude.valueChanged.connect(self.update_ui)
        self.sld_longitude.valueChanged.connect(self.update_ui)
        self.spn_position.valueChanged.connect(self.update_ui)

        self.sld_max_segment_length.valueChanged.connect(self.update_ui)

        self.label_lyr = None
        self.polygon_lyr = None
        self.linestring_lyr = None
        self.point_lyr = None

        self.stk_params.hide()
        self.rubberbands = []

    @pyqtSlot()
    def single_geom_mode(self):
        self.stk_select_geoms.setCurrentIndex(0)
        self.btn_single_geom.setChecked(True)
        self.btn_predicates.setChecked(False)

    @pyqtSlot()
    def predicate_mode(self):
        self.stk_select_geoms.setCurrentIndex(1)
        self.btn_predicates.setChecked(True)
        self.btn_single_geom.setChecked(False)

    @pyqtSlot()
    def load_layers(self):
        self.reset_layers()

        self.translate_x = 0
        self.translate_y = 0
        self.label_lyr = self.prepare_memory_layer("Polygon", "Geosaurus Labels")
        self.add_memory_layer_to_map(self.label_lyr)

        if self.chk_point.isChecked():
            self.point_lyr = self.prepare_memory_layer("Point", "Geosaurus Point")
            self.add_memory_layer_to_map(self.point_lyr)
            self.add_features(self.point_lyr, "point_examples.wkt")
            qml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "point_default.qml")
            self.point_lyr.loadNamedStyle(qml_path)
        if self.chk_linestring.isChecked():
            self.linestring_lyr = self.prepare_memory_layer("LineString", "Geosaurus LineString")
            self.add_memory_layer_to_map(self.linestring_lyr)
            self.add_features(self.linestring_lyr, "linestring_examples.wkt")
            self.linestring_lyr.updateExtents()
            qml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "linestring_default.qml")
            self.linestring_lyr.loadNamedStyle(qml_path)
        if self.chk_polygon.isChecked():
            self.polygon_lyr = self.prepare_memory_layer("Polygon", "Geosaurus Polygon")
            self.add_memory_layer_to_map(self.polygon_lyr)
            self.add_features(self.polygon_lyr, "polygon_examples.wkt")
            self.polygon_lyr.updateExtents()
            qml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "polygon_default.qml")
            self.polygon_lyr.loadNamedStyle(qml_path)

        qml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "styles", "label_default.qml")
        self.label_lyr.loadNamedStyle(qml_path)
        self.label_lyr.updateExtents()

        iface.mapCanvas().zoomToFullExtent()

    def reset_layers(self):
        all_layers = [
            self.label_lyr,
            self.point_lyr, self.linestring_lyr, self.polygon_lyr
        ]

        for lyr in all_layers:
            if lyr:
                try:
                    QgsMapLayerRegistry.instance().removeMapLayers([lyr.id()])
                except RuntimeError:
                    pass
                lyr = None

    def populate_layer_combo(self, combo_box):
        """Not used"""
        for lyr in QgsMapLayerRegistry.instance().mapLayers().values():
            combo_box.addItem(lyr.name())

    def populate_postgis_combo(self):
        self.cmb_postgis_function.clear()
        self.cmb_postgis_function.addItems(
            SPATIAL_FUNCTION_CATEGORIES[self.cmb_function_filter.currentText()])

    def update_postgis_version(self):
        self.lbl_postgis_version.setText("PostGIS Version: {} - Docs".format(postgis_version()))

    @staticmethod
    def prepare_memory_layer(geometry_type, name):
        """Prepare memory layers that will be used to display tests"""
        lyr = QgsVectorLayer("{0}?crs=epsg:{1}".format(geometry_type, EPSG), name, "memory")
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

    def add_features(self, lyr, wkt_file_name):

        # If another geometry type has already been added to the map,
        # bump new features down a row
        if self.translate_x != 0 or self.translate_y != 0:
            self.translate_y += -0.002
            self.translate_x = 0

        wkt_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "wkt", wkt_file_name)

        with open(wkt_path, "rb") as f:
            reader = csv.reader(f, delimiter=";", quotechar='"')
            feature_attr_rows = list(reader)[1:]

        # Simultaneously add features to example layer and label layer
        with edit(lyr), edit(self.label_lyr):
            feats = []
            count_feats = 0

            label_feats = []
            label_poly = "POLYGON((0 0, 0.0008 0, 0.0008 -0.0006, 0 -0.0006, 0 0))"

            for row in feature_attr_rows:
                attrs = row[0:4]

                # Every 6th feature is the last on that row
                if count_feats == 6:
                    self.translate_x = 0
                    self.translate_y += -0.002
                    count_feats = 0

                feat = self.create_translated_feature(row[4], attrs)
                feats.append(feat)

                label_feat = self.create_translated_feature(label_poly, attrs)
                label_feats.append(label_feat)

                # Change vars to translate next feature along the row
                self.translate_x += 0.002
                count_feats += 1

            lyr.addFeatures(feats, False)
            self.label_lyr.addFeatures(label_feats, False)

    def create_translated_feature(self, wkt, attrs):

        geom = QgsGeometry.fromWkt(wkt)
        geom.translate(self.translate_x, self.translate_y)
        feat = QgsFeature()
        feat.setGeometry(geom)
        feat.setAttributes(attrs)
        return feat

    def update_ui(self):

        postgis_function = self.cmb_postgis_function.currentText()

        for x in self.rubberbands:
            x.reset()
        self.rubberbands = []

        kwargs = None
        if postgis_function == "ST_Buffer":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(0)
            self.cmb_end_cap.setEnabled(True)
            self.lbl_end_cap.setEnabled(True)
            kwargs = {
                "distance": self.sld_distance.value() * 0.00001,
                "quad_segs": self.sld_segments.value(),
                "endcap": self.cmb_end_cap.currentText(),
                "join": self.cmb_join.currentText(),
                "mitre_limit": "{0}.0".format(self.sld_mitre.value()),
            }
        elif postgis_function == "ST_OffsetCurve":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(0)
            self.cmb_end_cap.setEnabled(False)
            self.lbl_end_cap.setEnabled(False)
            kwargs = {
                "distance": self.sld_distance.value() * 0.00001,
                "quad_segs": self.sld_segments.value(),
                "join": self.cmb_join.currentText(),
                "mitre_limit": "{0}.0".format(self.sld_mitre.value()),
            }
        elif postgis_function == "ST_Scale":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(1)
            kwargs = {
                "xfactor": self.sld_scale_x.value() * 0.04,
                "yfactor": self.sld_scale_y.value() * 0.04,
            }
        elif postgis_function in ["ST_RotateX", "ST_RotateY"]:
            self.stk_params.show()
            self.stk_params.setCurrentIndex(2)
            kwargs = {
                "radians": math.radians(self.sld_rotate.value()),
            }
        elif postgis_function == "ST_LineInterpolatePoint":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(3)
            kwargs = {
                "fraction": self.sld_interpolate.value() * 0.04,
            }
        elif postgis_function == "ST_LineSubstring":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(4)
            kwargs = {
                "startfraction": self.sld_start_fraction.value() * 0.04,
                "endfraction": self.sld_end_fraction.value() * 0.04,
            }
        elif postgis_function == "ST_AddPoint":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(6)
            kwargs = {
                "point_x": self.sld_latitude.value() * 0.00001,
                "point_y": self.sld_longitude.value() * 0.00001,
                "position": self.spn_position.value(),
            }
        elif postgis_function == "ST_Segmentize":
            self.stk_params.show()
            self.stk_params.setCurrentIndex(7)
            kwargs = {
                "max_segment_length": self.sld_max_segment_length.value() * 0.00001
            }
        else:
            self.stk_params.hide()

        function = create_spatial_function(postgis_function, kwargs)

        # TODO: remove this if later when everything works through create_spatial_function()
        if function:
            lyrs = [self.point_lyr, self.linestring_lyr, self.polygon_lyr]
            for lyr in lyrs:
                if lyr:
                    for f in lyr.getFeatures():
                        wkt = f.geometry().exportToWkt()
                        self.txtb_query.setText(function.sample_query_as_text(wkt))
                        result = function.execute_query(wkt)[0]
                        self.txtb_result.setText(result)

                        new_g = QgsGeometry.fromWkt(result)

                        self.build_rubberbands(new_g, lyr)

    def display_result(self):
        postgis_function = self.cmb_postgis_function.currentText()
        if postgis_function in OTHER_SUPPORTED_FUNCTIONS:
            pass
        else:
            for x in self.rubberbands:
                x.reset()
            self.rubberbands = []

            self.txtb_result.setText("")

            with edit(self.label_lyr):
                for f in self.linestring_lyr.getFeatures():
                    g_wkt = f.geometry().exportToWkt()
                    postgis_function = self.cmb_postgis_function.currentText()
                    if postgis_function in GEOM_RETURNING_FUNCTIONS:
                        self.display_query(g_wkt, postgis_function)
                        out_geom_wkt = select_one_geom(postgis_function, g_wkt)[0]
                        self.txtb_result.setText(out_geom_wkt)
                    elif postgis_function in TEXT_RETURNING_FUNCTIONS:
                        text_result = select_one_geom_return_text(postgis_function, g_wkt)[0]
                        self.txtb_result.setText(text_result)
                        self.label_lyr.changeAttributeValue(f.id(), 3, text_result)
                        continue

                    out_geom = QgsGeometry.fromWkt(out_geom_wkt)
                    self.build_rubberbands(out_geom, self.linestring_lyr)

    def build_rubberbands(self, geometry, lyr):
        if geometry:
            if geometry.type() == 2:  # Polygon

                # Handle interior rings in polygons
                polygon_geometry = geometry.geometry()
                if polygon_geometry.numInteriorRings() > 0:
                    for ring in xrange(polygon_geometry.numInteriorRings()):
                        interior_geometry = QgsGeometry.fromWkt(
                            polygon_geometry.interiorRing(ring).asWkt())

                        outer_stroke = self.create_rubberband(
                            lyr, QGis.Line, interior_geometry, Qt.darkBlue, 5)
                        inner_stroke = self.create_rubberband(
                            lyr, QGis.Line, interior_geometry, Qt.white, 2)
                        self.rubberbands.append(outer_stroke)
                        self.rubberbands.append(inner_stroke)

            outer_stroke = self.create_rubberband(
                lyr, QGis.Polygon, geometry, Qt.darkBlue, 5)
            inner_stroke = self.create_rubberband(
                lyr, QGis.Polygon, geometry, Qt.white, 2)
            self.rubberbands.append(outer_stroke)
            self.rubberbands.append(inner_stroke)

    @staticmethod
    def create_rubberband(lyr, geometry_type, geometry, colour, width):
        r = QgsRubberBand(iface.mapCanvas(), geometry_type)
        r.setToGeometry(geometry, lyr)
        r.setBorderColor(colour)
        r.setWidth(width)
        r.show()
        return r

    def display_query(self, *args):
        wkt = args[0]
        function_name = args[1]
        self.txtb_query.setText("SELECT ST_AsText({1}(ST_GeomFromText('{0}')))".format(wkt, function_name))

    def closeEvent(self, event):
        self.closingDialog.emit()
        event.accept()
