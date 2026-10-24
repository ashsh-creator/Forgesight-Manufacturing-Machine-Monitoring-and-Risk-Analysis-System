
"""Local, threshold-based predictive maintenance assessment.

This is a rule-based demonstration, not a trained ML failure model.
Missing sensor readings produce an Unknown assessment.
"""

import math
import os
import sys
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.logger_config import get_logger
from config.app_config import config

logger = get_logger(__name__)


class MaintenancePredictor:
    REQUIRED_SENSORS = (
        "vibration",
        "temperature",
        "current",
        "pressure",
    )

    SENSOR_LABELS = {
        "vibration": ("Vibration", "g"),
        "temperature": ("Temperature", "°C"),
        "current": ("Current", "A"),
        "pressure": ("Pressure", "bar"),
    }

    def __init__(self):
        self.thresholds = config.RISK_THRESHOLDS
        logger.info(
            "MaintenancePredictor initialized with configuration thresholds"
        )

    @staticmethod
    def _valid_number(value):
        try:
            if value is None or isinstance(value, bool):
                return False
            return math.isfinite(float(value))
        except (TypeError, ValueError, OverflowError):
            return False

    def calculate_failure_risk(
        self, sensor_data: Dict[str, Any]
    ) -> Dict[str, Any]:

        machine_id = sensor_data.get("machine_id", "Unknown")

        missing = [
            name
            for name in self.REQUIRED_SENSORS
            if not self._valid_number(sensor_data.get(name))
        ]

        if missing:
            return {
                "machine_id": machine_id,
                "failure_risk": "Unknown",
                "risk_score": None,
                "reason": (
                    "Insufficient sensor data: missing "
                    + ", ".join(missing)
                    + "."
                ),
                "predicted_days_to_failure": None,
                "confidence": None,
                "recommendations": [
                    "Restore or verify sensor connectivity",
                    "Collect complete sensor readings before assessing failure risk",
                ],
            }

        readings = {
            name: float(sensor_data[name])
            for name in self.REQUIRED_SENSORS
        }

        risks = {
            name: self._calculate_parameter_risk(value, name)
            for name, value in readings.items()
        }

        overall_risk = (
            risks["vibration"] * 0.30
            + risks["temperature"] * 0.25
            + risks["current"] * 0.25
            + risks["pressure"] * 0.20
        )

        if overall_risk >= 0.8:
            risk_level = "High"
            days_to_failure = max(
                1, int(10 * (1 - overall_risk))
            )
        elif overall_risk >= 0.5:
            risk_level = "Medium"
            days_to_failure = max(
                5, int(30 * (1 - overall_risk))
            )
        else:
            risk_level = "Low"
            days_to_failure = max(
                30, int(90 * (1 - overall_risk))
            )

        return {
            "machine_id": machine_id,
            "failure_risk": risk_level,
            "risk_score": round(overall_risk, 2),
            "reason": self._generate_reason(readings),
            # Illustrative heuristic, not a validated failure forecast.
            "predicted_days_to_failure": days_to_failure,
            # No statistically calibrated confidence is available.
            "confidence": None,
            "recommendations": self._generate_recommendations(
                risk_level, sensor_data
            ),
        }

    def _calculate_parameter_risk(
        self, value: float, parameter: str
    ) -> float:

        thresholds = self.thresholds[parameter]

        if value <= thresholds["low"]:
            return 0.2
        if value <= thresholds["medium"]:
            return 0.5
        if value <= thresholds["high"]:
            return 0.8

        return 1.0

    def _generate_reason(self, readings: Dict[str, float]) -> str:
        reasons = []

        for parameter in self.REQUIRED_SENSORS:
            value = readings[parameter]
            thresholds = self.thresholds[parameter]
            label, unit = self.SENSOR_LABELS[parameter]

            if value > thresholds["high"]:
                reasons.append(
                    f"{label} is {value:g} {unit}, above the "
                    f"high threshold of {thresholds['high']:g} {unit}"
                )
            elif value > thresholds["medium"]:
                reasons.append(
                    f"{label} is {value:g} {unit}, above the "
                    f"medium threshold of {thresholds['medium']:g} {unit}"
                )
            elif value > thresholds["low"]:
                reasons.append(
                    f"{label} is {value:g} {unit}, above the "
                    f"low threshold of {thresholds['low']:g} {unit}"
                )

        if reasons:
            return "; ".join(reasons) + "."

        return "All monitored parameters are within configured low thresholds."

    def _generate_recommendations(
        self,
        risk_level: str,
        sensor_data: Dict[str, Any],
    ) -> List[str]:

        if risk_level == "High":
            return [
                "Schedule immediate maintenance inspection",
                "Consider reducing machine load",
                "Increase monitoring frequency",
            ]

        if risk_level == "Medium":
            return [
                "Schedule a maintenance inspection",
                "Increase monitoring frequency",
                "Check for unusual operating patterns",
            ]

        return [
            "Continue regular monitoring",
            "Schedule routine maintenance as planned",
        ]

    def calculate_cost_savings(
        self,
        predicted_failure_days: int,
        unplanned_downtime_cost: float = 10000,
    ) -> Dict[str, float]:

        if (
            predicted_failure_days is None
            or predicted_failure_days <= 0
        ):
            return {
                "savings": 0,
                "planned_maintenance_cost": 0,
                "unplanned_downtime_cost": unplanned_downtime_cost,
                "downtime_hours": 0,
            }

        # Illustrative assumptions, not observed financial savings.
        planned_maintenance_cost = 2000
        downtime_hours = 24

        return {
            "savings": (
                unplanned_downtime_cost - planned_maintenance_cost
            ),
            "planned_maintenance_cost": planned_maintenance_cost,
            "unplanned_downtime_cost": unplanned_downtime_cost,
            "downtime_hours": downtime_hours,
        }
