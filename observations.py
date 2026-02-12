import random
import time
from typing import Any, Dict, List, Optional

from PyQt5.QtCore import QThread, pyqtSignal

from .constants import (
    API_BATCH_SIZE,
    API_MAX_TOTAL_RECORDS,
    API_OBSERVATIONS_BASE_URL,
)
from .exceptions import ObservationsFetchError
from .http_client import HTTPClient


class FetchObservationsThread(QThread):
    progress_updated = pyqtSignal(int)
    fetch_completed = pyqtSignal(list)
    fetch_failed = pyqtSignal(str)
    batch_fetched = pyqtSignal(list)

    def __init__(self, form_params: Dict[str, Any]) -> None:
        super().__init__()
        self.form_params: Dict[str, Any] = form_params
        self._is_running = True

    def run(self) -> None:
        try:
            total_files: int = self.get_total_files(self.form_params)
            if total_files == 0:
                self.fetch_failed.emit("No observations found for the given criteria.")
                return
            if total_files >= API_MAX_TOTAL_RECORDS:
                self.fetch_failed.emit(
                    f"Total records exceed the maximum limit of {API_MAX_TOTAL_RECORDS}. "
                    "Please refine your search criteria."
                )
                return
            results: List[Dict[str, Any]] = []
            total_pages: int = self.calculate_batches(total_files)
            downloaded_size: int = 0

            with HTTPClient() as client:
                for page in range(1, total_pages + 1):
                    if not self._is_running:
                        self.fetch_failed.emit(
                            "You stopped the data fetch from the API."
                        )
                        return

                    params = {
                        **self.form_params,
                        "page": page,
                        "per_page": API_BATCH_SIZE,
                    }

                    chunk_results: List[Dict[str, Any]] = self.fetch_page(
                        client, params, page
                    )
                    results.extend(chunk_results)

                    downloaded_size += len(chunk_results)
                    self.update_progress(total_files, downloaded_size)
                    self.batch_fetched.emit(chunk_results)

                    time.sleep(1.1 + (0.4 * random.random()))  # nosec B311

                self.progress_updated.emit(100)
                self.fetch_completed.emit(results)

        except Exception as e:
            self.fetch_failed.emit(f"Error: {str(e)}")

    def fetch_page(
        self, client: HTTPClient, params: Dict[str, Any], page: int
    ) -> List[Dict[str, Any]]:
        """Fetch a single page of observations."""
        try:
            response_data = client.get(API_OBSERVATIONS_BASE_URL, params=params)
            return response_data.get("results", [])
        except Exception as e:
            raise ObservationsFetchError(f"API request failed on page {page}: {e}")

    def get_total_files(self, params: Dict[str, Any]) -> int:
        """Get the total number of observations available."""
        try:
            with HTTPClient() as client:
                response_data = client.get(API_OBSERVATIONS_BASE_URL, params=params)
                return response_data.get("total_results", 0)
        except Exception as e:
            raise ObservationsFetchError(
                f"Failed to fetch total observation count: {e}"
            )

    def calculate_batches(self, total_files: int) -> int:
        num_requests = (
            total_files + API_BATCH_SIZE - 1
        ) // API_BATCH_SIZE  # Ceiling division
        return num_requests

    def update_progress(self, total_files: int, downloaded_size: int) -> None:
        progress = int((downloaded_size / total_files) * 100)
        self.progress_updated.emit(min(progress, 100))

    def stop(self):
        self._is_running = False


class Observations:
    def __init__(self) -> None:
        self.thread: Optional[FetchObservationsThread] = None

    def fetch(
        self,
        form_params: Dict[str, Any],
        on_batch_fetched,
        on_progress_updated,
        on_fetch_completed,
        on_fetch_failed,
    ) -> None:
        """Fetch observations with provided callbacks.

        Args:
            form_params: Parameters for the API request
            on_batch_fetched: Callback for when a batch is fetched
            on_progress_updated: Callback for progress updates
            on_fetch_completed: Callback for when fetch completes
            on_fetch_failed: Callback for when fetch fails
        """
        self.thread = FetchObservationsThread(form_params)
        self.thread.batch_fetched.connect(on_batch_fetched)
        self.thread.progress_updated.connect(on_progress_updated)
        self.thread.fetch_completed.connect(on_fetch_completed)
        self.thread.fetch_failed.connect(on_fetch_failed)
        self.thread.start()

    def stop_fetching(self) -> None:
        if self.thread:
            self.thread.stop()
