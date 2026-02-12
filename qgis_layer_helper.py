import time
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import QVariant
from qgis.core import (
    QgsCoordinateReferenceSystem,
    QgsCoordinateTransform,
    QgsDataProvider,
    QgsFeature,
    QgsField,
    QgsGeometry,
    QgsPointXY,
    QgsProject,
    QgsVectorLayer,
)
from qgis.utils import iface

from .observation_parser import ObservationParser


class QgisLayerHelper:
    """Helper class for managing QGIS layers and adding observations."""

    def get_bounding_box(self) -> Dict[str, float]:
        """Returns the bounding box of the current map canvas."""
        canvas = iface.mapCanvas()
        extent = canvas.extent()
        map_crs = canvas.mapSettings().destinationCrs()

        if map_crs.authid() != "EPSG:4326":
            transform = QgsCoordinateTransform(
                map_crs,
                QgsCoordinateReferenceSystem("EPSG:4326"),
                QgsProject.instance(),
            )

            sw_point = transform.transform(extent.xMinimum(), extent.yMinimum())
            ne_point = transform.transform(extent.xMaximum(), extent.yMaximum())

            return {
                "swlat": sw_point.y(),
                "swlng": sw_point.x(),
                "nelat": ne_point.y(),
                "nelng": ne_point.x(),
            }

        return {
            "swlat": extent.yMinimum(),
            "swlng": extent.xMinimum(),
            "nelat": extent.yMaximum(),
            "nelng": extent.xMaximum(),
        }

    def create_layer_and_provider(self) -> Tuple[QgsVectorLayer, QgsDataProvider]:
        layer_name = "inat_observations_" + time.strftime("%Y-%m-%d_%H:%M:%S")
        layer = QgsVectorLayer("Point?crs=EPSG:4326", layer_name, "memory")
        provider = layer.dataProvider()
        provider.addAttributes(
            [
                QgsField("species", QVariant.String),
                QgsField("date", QVariant.String),
                QgsField("location", QVariant.String),
                QgsField("photo_url", QVariant.String),
                QgsField("observation_url", QVariant.String),
                QgsField("wikipedia_url", QVariant.String),
                QgsField("author_url", QVariant.String),
            ]
        )
        layer.updateFields()
        return layer, provider

    def add_layer_to_project(self, layer: QgsVectorLayer) -> None:
        QgsProject.instance().addMapLayer(layer)

    def add_observations_to_layer(
        self,
        observations: List[Dict],
        layer: QgsVectorLayer,
        provider: QgsDataProvider,
    ) -> Optional[List[QgsFeature]]:
        """
        Add observations to the layer and return the features.

        Args:
            observations: List of raw observation dictionaries from API
            layer: QGIS vector layer to add features to
            provider: Data provider for the layer

        Returns:
            List of added features, or None if no valid observations
        """
        features: List[QgsFeature] = []

        for observation in observations:
            parsed = ObservationParser.parse_observation(observation)
            if parsed is None:
                continue

            feature = QgsFeature()
            feature.setGeometry(
                QgsGeometry.fromPointXY(QgsPointXY(parsed["lon"], parsed["lat"]))
            )
            feature.setAttributes(
                [
                    parsed["species"],
                    parsed["date"],
                    parsed["location"],
                    parsed["photo_url"],
                    parsed["observation_url"],
                    parsed["wikipedia_url"],
                    parsed["author_url"],
                ]
            )
            features.append(feature)

        if features:
            provider.addFeatures(features)
            layer.updateExtents()
            layer.triggerRepaint()
            return features

        return None
