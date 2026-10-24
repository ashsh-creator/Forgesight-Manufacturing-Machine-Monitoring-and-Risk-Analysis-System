
"""
Data loading utilities for historical synthetic sensor data
and maintenance records.
"""

import os
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime

import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_config import get_logger
from config.app_config import config

logger = get_logger(__name__)


class DataLoader:
    """Loads and processes sensor and maintenance records."""

    def __init__(self, data_dir: str = None):
        self.data_dir = data_dir or config.DATA_DIR
        self.sensor_data = None
        self.maintenance_data = None

        logger.info(
            f"DataLoader initialized with data directory: {self.data_dir}"
        )

    def load_sensor_data(self) -> pd.DataFrame:
        """Load historical synthetic sensor readings from CSV."""

        if self.sensor_data is None:
            file_path = os.path.join(
                self.data_dir,
                "synthetic_sensor_data.csv"
            )

            self.sensor_data = pd.read_csv(file_path)

            self.sensor_data["timestamp"] = pd.to_datetime(
                self.sensor_data["timestamp"],
                errors="coerce"
            )

            logger.info(
                f"Loaded {len(self.sensor_data)} sensor data records"
            )

        return self.sensor_data

    def load_maintenance_data(self) -> pd.DataFrame:
        """Load historical maintenance records from CSV."""

        if self.maintenance_data is None:
            file_path = os.path.join(
                self.data_dir,
                "synthetic_maintenance_records.csv"
            )

            self.maintenance_data = pd.read_csv(file_path)

            for column in [
                "last_service_date",
                "next_service_due"
            ]:
                self.maintenance_data[column] = pd.to_datetime(
                    self.maintenance_data[column],
                    errors="coerce"
                )

            logger.info(
                f"Loaded {len(self.maintenance_data)} maintenance records"
            )

        return self.maintenance_data

    def get_latest_sensor_data(self) -> pd.DataFrame:
        """
        Return the latest actual sensor record per machine.

        Missing values are preserved rather than replaced
        with values from older records.
        """

        sensor_data = self.load_sensor_data()

        if sensor_data.empty:
            return sensor_data.copy()

        latest_data = (
            sensor_data
            .sort_values("timestamp", kind="stable")
            .drop_duplicates(
                subset=["machine_id"],
                keep="last"
            )
            .sort_values("machine_id")
            .reset_index(drop=True)
        )

        return latest_data

    def get_machine_history(
        self,
        machine_id: str
    ) -> pd.DataFrame:
        """Get chronological sensor history for a machine."""

        sensor_data = self.load_sensor_data()

        machine_history = sensor_data[
            sensor_data["machine_id"] == machine_id
        ].copy()

        return machine_history.sort_values(
            "timestamp",
            kind="stable"
        ).reset_index(drop=True)

    def get_maintenance_schedule(self) -> pd.DataFrame:
        """Get maintenance records sorted by due date."""

        maintenance_data = self.load_maintenance_data()

        return maintenance_data.sort_values(
            "next_service_due"
        ).reset_index(drop=True)

    def get_machines_overdue(self) -> List[str]:
        """
        Return machine IDs with maintenance due dates
        earlier than today.

        Dates are interpreted as calendar dates.
        """

        maintenance_data = self.load_maintenance_data()

        today = pd.Timestamp(datetime.now().date())

        overdue = maintenance_data[
            maintenance_data["next_service_due"].notna()
            & (maintenance_data["next_service_due"] < today)
        ]

        return overdue["machine_id"].dropna().unique().tolist()

    def get_machine_maintenance_data(
        self,
        machine_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get the most recent service record for a machine."""

        maintenance_data = self.load_maintenance_data()

        machine_maintenance = maintenance_data[
            maintenance_data["machine_id"] == machine_id
        ]

        if machine_maintenance.empty:
            logger.warning(
                f"No maintenance data found for machine {machine_id}"
            )
            return None

        latest_maintenance = (
            machine_maintenance
            .sort_values("last_service_date", kind="stable")
            .iloc[-1]
            .to_dict()
        )

        return {
            "machine_id": machine_id,
            "last_service_date": latest_maintenance.get(
                "last_service_date"
            ),
            "service_notes": latest_maintenance.get(
                "service_notes"
            ),
            "next_service_due": latest_maintenance.get(
                "next_service_due"
            ),
            "service_cost": latest_maintenance.get(
                "service_cost"
            ),
        }
