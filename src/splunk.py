"""
Splunk Audit Module
Sends audit events and remediation results to Splunk HEC
"""
import requests
import os
import sys
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Splunk HEC Configuration
SPLUNK_HEC_ENDPOINT = os.getenv("SPLUNK_HEC_ENDPOINT")
SPLUNK_HEC_TOKEN = os.getenv("SPLUNK_HEC_TOKEN")

# Request headers
headers = {
    "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
    "Content-Type": "application/json"
}


def send_to_splunk(event_data, source="mist_automation", sourcetype="mist:sle:automation"):
    """
    Send event data to Splunk HEC
    
    Args:
        event_data (dict): Event data to send
        source (str): Splunk source field
        sourcetype (str): Splunk sourcetype field
        
    Returns:
        dict: Response from Splunk HEC
    """
    if not SPLUNK_HEC_ENDPOINT or not SPLUNK_HEC_TOKEN:
        logger.warning("Splunk HEC not configured - skipping audit")
        return {"status": "skipped", "reason": "HEC not configured"}
    
    payload = {
        "time": int(datetime.utcnow().timestamp()),
        "host": "github-actions",
        "source": source,
        "sourcetype": sourcetype,
        "event": event_data
    }
    
    logger.info(f"Sending event to Splunk HEC: {SPLUNK_HEC_ENDPOINT}")
    
    try:
        response = requests.post(
            SPLUNK_HEC_ENDPOINT,
            headers=headers,
            json=payload,
            timeout=10
        )
        response.raise_for_status()
        
        logger.info("Event successfully sent to Splunk")
        return response.json()
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send event to Splunk: {e}")
        raise


def audit_detection(ap_id, sle_type, severity, source="splunk"):
    """
    Audit SLE detection event
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        severity (str): Severity level
        source (str): Detection source
        
    Returns:
        dict: Audit result
    """
    event = {
        "event_type": "sle_detection",
        "ap_id": ap_id,
        "sle": sle_type,
        "severity": severity,
        "source": source,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Auditing SLE detection for AP {ap_id}")
    
    try:
        result = send_to_splunk(event, sourcetype="mist:sle:detection")
        return {"status": "success", "response": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def audit_diagnostics(ap_id, diagnostics_result):
    """
    Audit diagnostics execution
    
    Args:
        ap_id (str): Access Point ID
        diagnostics_result (dict): Diagnostics data
        
    Returns:
        dict: Audit result
    """
    event = {
        "event_type": "diagnostics",
        "ap_id": ap_id,
        "diagnostics": diagnostics_result,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Auditing diagnostics for AP {ap_id}")
    
    try:
        result = send_to_splunk(event, sourcetype="mist:sle:diagnostics")
        return {"status": "success", "response": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def audit_remediation(ap_id, action, remediation_result):
    """
    Audit remediation execution
    
    Args:
        ap_id (str): Access Point ID
        action (str): Remediation action performed
        remediation_result (dict): Remediation result data
        
    Returns:
        dict: Audit result
    """
    event = {
        "event_type": "remediation",
        "ap_id": ap_id,
        "action": action,
        "result": remediation_result,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Auditing remediation ({action}) for AP {ap_id}")
    
    try:
        result = send_to_splunk(event, sourcetype="mist:sle:remediation")
        return {"status": "success", "response": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def audit_validation(ap_id, sle_type, validation_result):
    """
    Audit validation execution
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        validation_result (dict): Validation result data
        
    Returns:
        dict: Audit result
    """
    event = {
        "event_type": "validation",
        "ap_id": ap_id,
        "sle": sle_type,
        "result": validation_result,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Auditing validation for AP {ap_id}, SLE: {sle_type}")
    
    try:
        result = send_to_splunk(event, sourcetype="mist:sle:validation")
        return {"status": "success", "response": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def audit_ticket_action(ticket_id, action, ap_id, sle_type):
    """
    Audit Zendesk ticket actions
    
    Args:
        ticket_id (str): Zendesk ticket ID
        action (str): Action performed (create, update, close)
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        
    Returns:
        dict: Audit result
    """
    event = {
        "event_type": "ticket_action",
        "ticket_id": ticket_id,
        "action": action,
        "ap_id": ap_id,
        "sle": sle_type,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Auditing ticket action: {action} for ticket #{ticket_id}")
    
    try:
        result = send_to_splunk(event, sourcetype="mist:sle:ticketing")
        return {"status": "success", "response": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def audit_workflow_complete(ap_id, sle_type, overall_status, metrics):
    """
    Audit complete workflow execution with MTTR metrics
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        overall_status (str): Final workflow status
        metrics (dict): Workflow metrics (MTTR, etc.)
        
    Returns:
        dict: Audit result
    """
    event = {
        "event_type": "workflow_complete",
        "ap_id": ap_id,
        "sle": sle_type,
        "status": overall_status,
        "metrics": metrics,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    logger.info(f"Auditing workflow completion for AP {ap_id}")
    
    try:
        result = send_to_splunk(event, sourcetype="mist:sle:workflow")
        return {"status": "success", "response": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}


def main():
    """
    CLI interface for Splunk audit operations
    Called from GitHub Actions workflow
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Splunk Audit Operations")
    parser.add_argument("--ap_id", required=True, help="Access Point ID")
    parser.add_argument("--sle", required=True, help="SLE metric type")
    parser.add_argument("--event_type", help="Event type to audit", default="workflow_complete")
    parser.add_argument("--status", help="Workflow status", default="unknown")
    
    args = parser.parse_args()
    
    try:
        # Simple workflow completion audit
        metrics = {
            "mttr": "auto-calculated",
            "automation_success": args.status == "success"
        }
        
        result = audit_workflow_complete(
            args.ap_id,
            args.sle,
            args.status,
            metrics
        )
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Audit operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
