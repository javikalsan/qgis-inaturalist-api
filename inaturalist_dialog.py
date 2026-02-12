import os
from typing import Any, Dict, List, Optional

from iso3166 import countries
from PyQt5 import uic
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QDialog, QMessageBox

from .form_data import FormData
from .observations import Observations
from .places import Places
from .qgis_layer_helper import QgisLayerHelper


class InaturalistDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()

        ui_path = os.path.join(
            os.path.dirname(__file__), "ui/inaturalist_dialog_base.ui"
        )
        uic.loadUi(ui_path, self)

        self.populate_countries()
        self.pushButton.clicked.connect(self.request_handler)
        self.pushButton_stop.clicked.connect(self.stop_handler)

        self.observations_api: Observations = Observations()
        self.places_api: Places = Places()
        self.qgis_layer_helper = QgisLayerHelper()

        self.layer = None

    def request_handler(self) -> None:
        try:
            form_data = FormData(
                username=self.lineEdit_username.text().strip(),
                species=self.lineEdit_species.text().strip(),
                date_from=self.dateEdit_date_from.date().toString("yyyy-MM-dd"),
                date_to=self.dateEdit_date_to.date().toString("yyyy-MM-dd"),
                country_id=self.set_country_id(self.comboBox_countries.currentText()),
                bbox=(
                    self.qgis_layer_helper.get_bounding_box()
                    if self.checkBox_map_extent.isChecked()
                    else None
                ),
            )

            api_params = self.set_api_params(form_data)

            self.observations_api.fetch(
                api_params,
                on_batch_fetched=self.add_batch_to_layer,
                on_progress_updated=self.progressBar.setValue,
                on_fetch_completed=self.on_fetch_completed,
                on_fetch_failed=self.on_fetch_failed,
            )

        except Exception as exc:
            QMessageBox.critical(self, "Error", str(exc))
            self.observations_api.stop_fetching()
            self.reset_form()
            self.close()
            return

    def reset_form(self) -> None:
        self.progressBar.setValue(0)
        self.comboBox_countries.setCurrentIndex(0)
        self.dateEdit_date_from.setDate(QDate(1900, 1, 1))
        self.dateEdit_date_to.setDate(QDate(2200, 1, 1))
        self.checkBox_date_range.setChecked(False)
        self.checkBox_map_extent.setChecked(False)
        self.layer = None

    def on_fetch_completed(self):
        self.reset_form()
        self.close()

    def add_batch_to_layer(self, batch_results: List[Dict[str, Any]]) -> None:
        if self.layer is None:
            self.layer, _ = self.qgis_layer_helper.create_layer_and_provider()
            self.qgis_layer_helper.add_layer_to_project(self.layer)

        provider = self.layer.dataProvider()  # type: ignore
        self.qgis_layer_helper.add_observations_to_layer(
            batch_results, self.layer, provider
        )

    def on_fetch_failed(self, error_message):
        QMessageBox.critical(self, "Error", error_message)
        self.observations_api.stop_fetching()
        self.reset_form()
        self.close()

    def populate_countries(self) -> None:
        self.comboBox_countries.clear()

        country_names = sorted([country.name for country in countries])

        self.comboBox_countries.addItem("Select a Country")
        self.comboBox_countries.addItems(country_names)

    def set_country_id(self, country: str) -> Optional[int]:
        if country:
            return self.places_api.get_place_id(country)
        return None

    def set_api_params(self, form_data: FormData) -> Dict[str, Any]:
        """Build API parameters from form data."""
        return form_data.build()

    def stop_handler(self) -> None:
        self.observations_api.stop_fetching()
        self.reset_form()
