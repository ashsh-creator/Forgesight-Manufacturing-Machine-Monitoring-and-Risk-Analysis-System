"""Machine management using the existing local threshold-based predictor.

Missing readings are preserved as None; no external AI calls are made.
"""
import math
import os
import sys
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger_config import get_logger
from utils.predictor import MaintenancePredictor
from utils.data_loader import DataLoader
from client.swe_client import SuperwiseRequest, SuperwiseResponse

logger = get_logger(__name__)


class ServiceException(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class MachinesService:
    def __init__(self):
        self.predictor = MaintenancePredictor()
        self.data_loader = DataLoader()
        logger.info('MachinesService initialized with local prediction engine')

    @staticmethod
    def sanitize_float(value):
        """Convert non-finite or absent sensor readings to None, not zero."""
        if value is None:
            return None
        try:
            number = float(value)
            return number if math.isfinite(number) else None
        except (ValueError, TypeError, OverflowError):
            return None

    def get_root_info(self) -> Dict[str, Any]:
        return {
            'message': 'Manufacturing Predictive Maintenance Service',
            'version': '1.0.0',
            'endpoints': {
                'health': 'health_check', 'status': 'system_status',
                'machines': 'get_machines', 'machine_details': 'get_machine_details',
                'superwise_ask': 'ask_superwise_ai',
            },
        }

    def health_check(self) -> Dict[str, str]:
        return {'status': 'healthy', 'service': 'maintenance-ai-service'}

    def system_status(self) -> Dict[str, Any]:
        return {
            'status': 'operational', 'uptime': '99.9%',
            'last_check': '2024-01-01T12:00:00Z',
            'services': {'database': 'healthy', 'prediction_engine': 'healthy',
                         'data_loader': 'healthy'},
        }

    def get_machines(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            latest_data = self.data_loader.get_latest_sensor_data()
            machines = []
            for _, row in latest_data.iterrows():
                sensor = row.to_dict()
                prediction = self.predictor.calculate_failure_risk(sensor)
                timestamp = row['timestamp']
                machines.append({
                    'machine_id': row['machine_id'],
                    'status': prediction.get('failure_risk', 'Unknown'),
                    'last_reading': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
                    'vibration': self.sanitize_float(row['vibration']),
                    'temperature': self.sanitize_float(row['temperature']),
                    'current': self.sanitize_float(row['current']),
                    'pressure': self.sanitize_float(row['pressure']),
                    'operating_hours': self.sanitize_float(row['operating_hours']),
                })
            logger.info('Locally assessed %d machines', len(machines))
            return {'machines': machines}
        except Exception as exc:
            logger.exception('Failed to get machines')
            raise ServiceException(f'Failed to get machines: {exc}', 500) from exc

    def get_machine_details(self, machine_id: str) -> Dict[str, Any]:
        try:
            history = self.data_loader.get_machine_history(machine_id)
            if history.empty:
                raise ServiceException('Machine not found', 404)
            latest = history.iloc[-1].to_dict()
            prediction = self.predictor.calculate_failure_risk(latest)
            days = prediction.get('predicted_days_to_failure')
            cost_savings = (self.predictor.calculate_cost_savings(days)
                            if days is not None else {})
            status = {
                'machine_id': prediction.get('machine_id', machine_id),
                'failure_risk': prediction.get('failure_risk', 'Unknown'),
                'risk_score': self.sanitize_float(prediction.get('risk_score')),
                'reason': prediction.get('reason', ''),
                'predicted_days_to_failure': self.sanitize_float(days),
                'confidence': self.sanitize_float(prediction.get('confidence')),
                'recommendations': prediction.get('recommendations', []),
            }
            savings = {
                key: self.sanitize_float(cost_savings.get(key))
                for key in ('savings', 'planned_maintenance_cost',
                            'unplanned_downtime_cost', 'downtime_hours')
            }
            timestamp = latest['timestamp']
            return {
                'machine_id': machine_id, 'current_status': status,
                'cost_savings': savings, 'history_points': len(history),
                'latest_reading': timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp),
            }
        except ServiceException:
            raise
        except Exception as exc:
            logger.exception('Failed to get machine details for %s', machine_id)
            raise ServiceException(f'Failed to get machine details: {exc}', 500) from exc

    def ask_superwise_ai(self, request: SuperwiseRequest) -> SuperwiseResponse:
        raise ServiceException(
            'External Superwise AI is disabled. Use the local maintenance report on Machine Details.',
            503,
        )


machines_service = MachinesService()
