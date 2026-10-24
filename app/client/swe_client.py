"""
Superwise AI API integration for advanced machine learning predictions.
"""
import requests
import json
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

# Import centralized logging and configuration
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.logger_config import get_logger
from config.app_config import config
logger = get_logger(__name__)

class SuperwiseAI:
    """Client for Superwise AI API integration."""
    
    def __init__(self):
        # Use configuration from centralized config
        superwise_config = config.get_superwise_config()
        self.base_url = superwise_config["base_url"]
        self.headers = superwise_config["headers"]
        self.timeout = superwise_config["timeout"]
        
        logger.info("SuperwiseAI client initialized with configuration")
    
    def ask_question(self, question: str, chat_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Send a question to Superwise AI and get a response.
        
        Args:
            question: The question to ask
            chat_history: Optional chat history for context
            
        Returns:
            Dictionary containing the AI response
        """
        if chat_history is None:
            chat_history = []
            
        payload = {
            "input": question,
            "chat_history": chat_history
        }
        
        try:
            logger.info(f"Sending request to Superwise AI: {self.base_url}/ask")
            logger.info(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(
                f"{self.base_url}/ask",
                headers=self.headers,
                data=json.dumps(payload),
                timeout=self.timeout
            )
            
            logger.info(f"Response status: {response.status_code}")
            logger.info(f"Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            
            response_data = response.json()
            logger.info(f"Response data: {response_data}")
            
            # Handle different response formats
            if 'output' in response_data:
                return {"response": response_data['output']}
            elif 'response' in response_data:
                return response_data
            else:
                return {"response": str(response_data)}
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Superwise AI API timeout: {str(e)}")
            return {"response": "API request timed out. Please try again later.", "error": "timeout"}
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Superwise AI API connection error: {str(e)}")
            return {"response": "Unable to connect to Superwise AI. Please check your network connection.", "error": "connection_error"}
        except requests.exceptions.HTTPError as e:
            logger.error(f"Superwise AI API HTTP error: {str(e)}")
            logger.error(f"Response content: {response.text}")
            return {"response": f"API returned error: {response.status_code}", "error": "http_error"}
        except requests.exceptions.RequestException as e:
            logger.error(f"Superwise AI API request failed: {str(e)}")
            return {"response": f"Request failed: {str(e)}", "error": "request_error"}
        except Exception as e:
            logger.error(f"Unexpected error in Superwise AI call: {str(e)}")
            return {"response": f"Unexpected error: {str(e)}", "error": "unexpected_error"}
    
    def analyze_machine_failure_risk(self, machine_id: str = None, machine_ids: List[str] = None) -> Dict[str, Any]:
        """
        Analyze machine failure risk using Superwise AI.
        
        Args:
            machine_id: ID of a single machine to analyze (for backward compatibility)
            machine_ids: List of machine IDs to analyze in batch
            
        Returns:
            Dictionary containing the failure risk assessment(s)
        """
        # Handle both single machine and batch analysis
        if machine_ids is not None:
            return self._analyze_multiple_machines(machine_ids)
        elif machine_id is not None:
            return self._analyze_single_machine(machine_id)
        else:
            raise ValueError("Either machine_id or machine_ids must be provided")
    
    def _analyze_single_machine(self, machine_id: str) -> Dict[str, Any]:
        """
        Analyze a single machine failure risk using Superwise AI.
        
        Args:
            machine_id: ID of the machine to analyze
            
        Returns:
            Dictionary containing the failure risk assessment
        """
        # Create a detailed question for the AI
        question = f"""
        Analyze the maintenance records and all sensor data for the CNC machine with machine_id {machine_id} and provide the Failure Risk Assessment. 
        The response must be only one of the following values: High, Medium, or Low.
        """
        
        try:
            response = self.ask_question(question)
            
            # Check if there was an error in the response
            if 'error' in response:
                logger.warning(f"Superwise AI returned error, using fallback analysis for machine {machine_id}")
                return self._get_fallback_analysis(machine_id)
            
            # Extract the assessment from the response
            ai_response = response.get('response', '')
            
            # Parse the response to extract risk level
            risk_level = self._extract_risk_level(ai_response)
            logger.info(f"Risk level for machine {machine_id}: {risk_level}")
            return {
                "risk_level": risk_level
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze machine {machine_id}: {str(e)}")
            return self._get_fallback_analysis(machine_id, error=str(e))
    
    def _analyze_multiple_machines(self, machine_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze multiple machines failure risk using Superwise AI in a single call.
        
        Args:
            machine_ids: List of machine IDs to analyze
            
        Returns:
            Dictionary containing risk assessments for all machines
        """
        # Create machine IDs string for the question
        machine_ids_str = '", "'.join(machine_ids)
        
        # Create a detailed question for batch analysis
        question = f"""
        Analyze the maintenance records and all sensor data for the CNC machines with machine_ids "{machine_ids_str}" and provide the Failure Risk Assessment. 
        The response must be in the following format: machine_id: <risk value> and no more details. 
        The risk value must be only one of the following values: High, Medium, or Low.
        """
        
        try:
            logger.info(f"Analyzing {len(machine_ids)} machines in batch: {machine_ids}")
            response = self.ask_question(question)
            
            # Check if there was an error in the response
            if 'error' in response:
                logger.warning(f"Superwise AI returned error, using fallback analysis for machines {machine_ids}")
                return self._get_fallback_batch_analysis(machine_ids)
            
            # Extract the assessment from the response
            ai_response = response.get('response', '')
            
            # Parse the response to extract risk levels for all machines
            risk_assessments = self._extract_batch_risk_levels(ai_response, machine_ids)
            logger.info(f"Batch risk assessment completed for {len(machine_ids)} machines")
            return risk_assessments
            
        except Exception as e:
            logger.error(f"Failed to analyze machines {machine_ids}: {str(e)}")
            return self._get_fallback_batch_analysis(machine_ids, error=str(e))
    
    def _extract_risk_level(self, response: str) -> str:
        """
        Extract risk level from AI response.
        
        Args:
            response: The AI response text
            
        Returns:
            Risk level: High, Medium, or Low
        """
        response_lower = response.lower()
        
        if "high" in response_lower:
            return "High"
        elif "medium" in response_lower:
            return "Medium"
        elif "low" in response_lower:
            return "Low"
        else:
            return "Unknown"
    
    def _extract_batch_risk_levels(self, response: str, machine_ids: List[str]) -> Dict[str, Any]:
        """
        Extract risk levels for multiple machines from AI response.
        
        Args:
            response: The AI response text
            machine_ids: List of machine IDs that were analyzed
            
        Returns:
            Dictionary with machine_id as key and risk_level as value
        """
        risk_assessments = {}
        response_lower = response.lower()
        
        # Try to parse the expected format: machine_id: <risk value>
        for machine_id in machine_ids:
            # Look for the machine_id in the response
            machine_pattern = f"{machine_id.lower()}:"
            if machine_pattern in response_lower:
                # Extract the risk level after the machine_id
                start_idx = response_lower.find(machine_pattern) + len(machine_pattern)
                # Find the next line break or end of string
                end_idx = response.find('\n', start_idx)
                if end_idx == -1:
                    end_idx = len(response)
                
                risk_text = response[start_idx:end_idx].strip().lower()
                
                if "high" in risk_text:
                    risk_assessments[machine_id] = "High"
                elif "medium" in risk_text:
                    risk_assessments[machine_id] = "Medium"
                elif "low" in risk_text:
                    risk_assessments[machine_id] = "Low"
                else:
                    risk_assessments[machine_id] = "Unknown"
            else:
                # If machine_id not found in specific format, try to extract from general response
                risk_assessments[machine_id] = self._extract_risk_level(response)
        
        return risk_assessments
    
    def _get_fallback_batch_analysis(self, machine_ids: List[str], error: str = None) -> Dict[str, Any]:
        """
        Provide fallback analysis when Superwise AI is not available for multiple machines.
        
        Args:
            machine_ids: List of machine IDs
            error: Optional error message
            
        Returns:
            Fallback analysis result for all machines
        """
        # Simple fallback analysis - assign medium risk to all machines
        risk_assessments = {}
        for machine_id in machine_ids:
            risk_assessments[machine_id] = "Medium"  # Default to medium risk when AI is unavailable
        
        logger.warning(f"Using fallback analysis for {len(machine_ids)} machines due to Superwise AI unavailability")
        if error:
            logger.warning(f"Error: {error}")
        
        return risk_assessments
    
    def _get_fallback_analysis(self, machine_id: str, error: str = None) -> Dict[str, Any]:
        """
        Provide fallback analysis when Superwise AI is not available.
        
        Args:
            machine_id: ID of the machine
            error: Optional error message
            
        Returns:
            Fallback analysis result
        """
        # Simple fallback analysis
        risk_level = "Medium"  # Default to medium risk when AI is unavailable
        
        assessment = f"Fallback analysis for {machine_id}: {risk_level} risk level. "
        assessment += "Unable to perform detailed analysis due to Superwise AI unavailability. "
        
        if error:
            assessment += f"Error: {error}. "
        
        assessment += "Please check machine status manually and consider using local monitoring systems."
        
        return {
            "risk_level": risk_level
        }
    
    def get_machine_insights(self, machine_id: str, question: str) -> Dict[str, Any]:
        """
        Get custom insights about a specific machine.
        
        Args:
            machine_id: ID of the machine
            question: Custom question about the machine
            
        Returns:
            Dictionary containing the AI response
        """
        formatted_question = f"For machine {machine_id}: {question}"
        
        try:
            response = self.ask_question(formatted_question)
            ai_response = response.get('response', '')
            risk_level = self._extract_risk_level(ai_response)
            return {
                "risk_level": risk_level
            }
        except Exception as e:
            logger.error(f"Failed to get insights for machine {machine_id}: {str(e)}")
            return {
                "risk_level": "Unknown"
            }


class SuperwiseRequest(BaseModel):
    """Pydantic model for Superwise AI requests."""
    question: str
    chat_history: Optional[List[Dict[str, Any]]] = []


class MachineAnalysisRequest(BaseModel):
    """Pydantic model for machine analysis requests."""
    machine_id: str


class SuperwiseResponse(BaseModel):
    """Pydantic model for Superwise AI responses."""
    risk_level: Optional[str] = None
    output: Optional[str] = None


# Initialize the Superwise AI client
superwise_client = SuperwiseAI()
