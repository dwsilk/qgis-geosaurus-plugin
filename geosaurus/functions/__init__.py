# -*- coding: utf-8 -*-

from .editors.addpoint import AddPoint
from .editors.rotatex import RotateX
from .editors.rotatey import RotateY
from .editors.scale import Scale
from .editors.segmentize import Segmentize
from .linear_referencing.lineinterpolatepoint import LineInterpolatePoint
from .linear_referencing.linesubstring import LineSubstring
from .processing.buffer import Buffer
from .processing.offsetcurve import OffsetCurve

ACCESSORS = [
    "ST_Boundary",
    "ST_CoordDim",
    "ST_Dimension",
    "ST_EndPoint",
    "ST_Envelope",
    "ST_BoundingDiagonal",
    "ST_ExteriorRing",
    "ST_GeometryN",
    "ST_GeometryType",
    "ST_InteriorRingN",
    "ST_IsPolygonCCW",
    "ST_IsPolygonCW",
    "ST_IsClosed",
    "ST_IsCollection",
    "ST_IsEmpty",
    "ST_IsRing",
    "ST_IsSimple",
    "ST_IsValid",
    "ST_IsValidReason",
    "ST_IsValidDetail",
    "ST_M",
    "ST_NDims",
    "ST_NPoints",
    "ST_NRings",
    "ST_NumGeometries",
    "ST_NumInteriorRings",
    "ST_NumInteriorRing",
    "ST_NumPatches",
    "ST_NumPoints",
    "ST_PatchN",
    "ST_PointN",
    "ST_Points",
    "ST_SRID",
    "ST_StartPoint",
    "ST_Summary",
    "ST_X",
    "ST_XMax",
    "ST_XMin",
    "ST_Y",
    "ST_YMax",
    "ST_YMin",
    "ST_Z",
    "ST_ZMax",
    "ST_Zmflag",
    "ST_ZMin",
]


EDITORS = [
    "ST_AddPoint",
    "ST_Affine",
    "ST_Force2D",
    "ST_Force3D",
    "ST_Force3DZ",
    "ST_Force3DM",
    "ST_Force4D",
    "ST_ForcePolygonCCW",
    "ST_ForceCollection",
    "ST_ForcePolygonCW",
    "ST_ForceSFS",
    "ST_ForceRHR",
    "ST_ForceCurve",
    "ST_LineMerge",
    "ST_CollectionExtract",
    "ST_CollectionHomogenize",
    "ST_Multi",
    "ST_Normalize",
    "ST_RemovePoint",
    "ST_Reverse",
    "ST_Rotate",
    "ST_RotateX",
    "ST_RotateY",
    "ST_RotateZ",
    "ST_Scale",
    "ST_Segmentize",
    "ST_SetPoint",
    "ST_SetSRID",
    "ST_SnapToGrid",
    "ST_Snap",
    "ST_Transform",
    "ST_Translate",
    "ST_TransScale",
]

LINEAR_REFERENCING = [
    "ST_LineInterpolatePoint",
    "ST_LineLocatePoint",
    "ST_LineSubstring",
    "ST_LocateAlong",
    "ST_LocateBetween",
    "ST_LocateBetweenElevations",
    "ST_InterpolatePoint",
    "ST_AddMeasure",
]

MEASUREMENTS = [
    "ST_3DDistance",
    "ST_3DMaxDistance",
    "ST_Area",
    "ST_Azimuth",
    "ST_Distance",
    "ST_MinimumClearance",
    "ST_HausdorffDistance",
    "ST_FrechetDistance",
    "ST_MaxDistance",
    "ST_DistanceSphere",
    "ST_DistanceSpheroid",
    "ST_GeometricMedian",
    "ST_HasArc",
    "ST_Length",
    "ST_Length2D",
    "ST_3DLength",
    "ST_LengthSpheroid",
    "ST_Length2D_Spheroid",
    "ST_Perimeter",
    "ST_Perimeter2D",
    "ST_3DPerimeter",
    # Needs to be ordered
    "ST_3DClosestPoint",
    "ST_3DLongestLine",
    "ST_3DShortestLine",
    "ST_Centroid",
    "ST_ClosestPoint",
    "ST_LineCrossingDirection",
    "ST_MinimumClearanceLine",
    "ST_LongestLine",
    "ST_PointOnSurface",
    "ST_Project",    
    "ST_ShortestLine",
]

MISCELLANEOUS = [
    "ST_Accum",
    "Box2D",
    "Box3D",
    "ST_EstimatedExtent",
    "ST_Expand",
    "ST_Extent",
    "ST_3DExtent",
    "Find_SRID",
    "ST_MemSize",
    "ST_PointInsideCircle",
]

OUTPUTS = [
    "ST_AsBinary",
    "ST_AsEncodedPolyline",
    "ST_AsEWKB",
    "ST_AsEWKT",
    "ST_AsGeoJSON",
    "ST_AsGML",
    "ST_AsHEXEWKB",
    "ST_AsKML",
    "ST_AsLatLonText",
    "ST_AsSVG",
    "ST_AsText",
    "ST_AsTWKB",
    "ST_AsX3D",
    "ST_GeoHash",
    "ST_AsGeobuf",
    "ST_AsMVTGeom",
    "ST_AsMVT",
]

OPERATORS = [
    "&&",
    "&&&",
    "&<",
    "&<|",
    "&>",
    "<<",
    "<<|",
    "=",
    ">>",
    "@",
    "|&>",
    "|>>",
    "~",
    "~=",
    "<->",
    "|=|",
    "<#>",
    "<<->>",
    "<<#>>",
]

PROCESSING = [
    "ST_Buffer",
    "ST_BuildArea",
    "ST_ClipByBox2D",
    "ST_Collect",
    "ST_ConcaveHull",
    "ST_ConvexHull",
    "ST_CurveToLine",
    "ST_DelaunayTriangles",
    "ST_Difference",
    "ST_Dump",
    "ST_DumpPoints",
    "ST_DumpRings",
    "ST_FlipCoordinates",
    "ST_GeneratePoints",
    "ST_Intersection",
    "ST_LineToCurve",
    "ST_MakeValid",
    "ST_MemUnion",
    "ST_MinimumBoundingCircle",
    "ST_MinimumBoundingRadius",
    "ST_Polygonize",
    "ST_Node",
    "ST_OffsetCurve",
    "ST_RemoveRepeatedPoints",
    "ST_SharedPaths",
    "ST_ShiftLongitude",
    "ST_WrapX",
    "ST_Simplify",
    "ST_SimplifyPreserveTopology",
    "ST_SimplifyVW",
    "ST_SetEffectiveArea",
    "ST_Split",
    "ST_SymDifference",
    "ST_Subdivide",
    "ST_SwapOrdinates",
    "ST_Union",
    "ST_UnaryUnion",
    "ST_VoronoiLines",
    "ST_VoronoiPolygons",
]

RELATIONSHIPS = [
    "ST_3DDWithin",
    "ST_3DDFullyWithin",
    "ST_3DIntersects",
    "ST_ClusterDBSCAN",
    "ST_ClusterIntersecting",
    "ST_ClusterKMeans",
    "ST_ClusterWithin",
    "ST_Contains",
    "ST_ContainsProperly",
    "ST_Covers",
    "ST_CoveredBy",
    "ST_Crosses",
    "ST_Disjoint",
    "ST_DFullyWithin",
    "ST_DWithin",
    "ST_Equals",
    "ST_Intersects",
    "ST_OrderingEquals",
    "ST_Overlaps",
    "ST_Relate",
    "ST_RelateMatch",
    "ST_Touches",
    "ST_Within",
]

SPATIAL_FUNCTION_CATEGORIES = {
    "All":
        ACCESSORS + EDITORS + LINEAR_REFERENCING + MEASUREMENTS +
        MISCELLANEOUS + OUTPUTS + OPERATORS + PROCESSING +
        RELATIONSHIPS,
    "Accessors": ACCESSORS,
    "Editors": EDITORS,
    "Linear Referencing": LINEAR_REFERENCING,
    "Measurements": MEASUREMENTS,
    "Miscellaneous": MISCELLANEOUS,
    "Outputs": OUTPUTS,
    "Operators": OPERATORS,
    "Processing": PROCESSING,
    "Relationships": RELATIONSHIPS,
}
