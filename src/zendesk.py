"""
Zendesk Ticketing Module
Handles ticket creation, updates, and closure for the SLE automation pipeline
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

# Zendesk API Configuration
ZENDESK_SUBDOMAIN = os.getenv("ZENDESK_SUBDOMAIN")
ZENDESK_EMAIL = os.getenv("ZENDESK_EMAIL")
ZENDESK_API_TOKEN = os.getenv("ZENDESK_API_TOKEN")
ZENDESK_GROUP_ID = os.getenv("ZENDESK_GROUP_ID", "")

# Request headers
headers = {
    "Content-Type": "application/json"
}


def _get_zendesk_config():
    """Validate required Zendesk environment and return base URL + auth."""
    if not ZENDESK_SUBDOMAIN:
        raise ValueError("ZENDESK_SUBDOMAIN environment variable not set")
    if not ZENDESK_EMAIL:
        raise ValueError("ZENDESK_EMAIL environment variable not set")
    if not ZENDESK_API_TOKEN:
        raise ValueError("ZENDESK_API_TOKEN environment variable not set")

    api_base = f"https://{ZENDESK_SUBDOMAIN}.zendesk.com/api/v2"
    auth = (f"{ZENDESK_EMAIL}/token", ZENDESK_API_TOKEN)
    return api_base, auth


# SLE to Zendesk Priority Mapping
SLE_PRIORITY_MAP = {
    "critical": "urgent",
    "high": "high",
    "medium": "normal",
    "low": "normal"
}


def create_ticket(ap_id, sle, severity="high", description=""):
    """
    Create a new Zendesk ticket for SLE failure
    
    Args:
        ap_id (str): Access Point ID
        sle (str): SLE metric type
        severity (str): Severity level (critical, high, medium, low)
        description (str, optional): Additional description
        
    Returns:
        dict: Created ticket data including ticket ID
    """
    priority = SLE_PRIORITY_MAP.get(severity, "normal")
    
    subject = f"Mist SLE Failure: {sle} on AP {ap_id}"
    
    body = f"""
    **Automated SLE Detection Alert**
    
    - **Access Point**: {ap_id}
    - **SLE Metric**: {sle}
    - **Severity**: {severity}
    - **Detection Time**: {datetime.utcnow().isoformat()}
    - **Source**: Splunk → GitHub Actions → Automation Pipeline
    
    {description}
    
    Automated remediation workflow has been initiated.
    """
    
    payload = {
        "ticket": {
            "subject": subject,
            "comment": {"body": body},
            "priority": priority,
            "type": "incident",
            "tags": ["mist", "wireless", "sle", "automation", sle, ap_id]
        }
    }
    
    # Add group assignment if configured
    if ZENDESK_GROUP_ID:
        payload["ticket"]["group_id"] = ZENDESK_GROUP_ID
    
    logger.info(f"Creating Zendesk ticket for AP {ap_id}, SLE: {sle}")
    
    try:
        api_base, auth = _get_zendesk_config()
        url = f"{api_base}/tickets.json"
        response = requests.post(url, auth=auth, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        ticket_data = response.json()
        ticket_id = ticket_data["ticket"]["id"]
        logger.info(f"Successfully created Zendesk ticket #{ticket_id}")
        
        return ticket_data
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to create Zendesk ticket: {e}")
        raise


def update_ticket(ticket_id, comment, status=None, priority=None, tags=None):
    """
    Update an existing Zendesk ticket with remediation progress
    
    Args:
        ticket_id (str): Zendesk ticket ID
        comment (str): Comment to add to ticket
        status (str, optional): New status (open, pending, solved)
        priority (str, optional): New priority
        tags (list, optional): Additional tags to add
        
    Returns:
        dict: Updated ticket data
    """
    payload = {
        "ticket": {
            "comment": {"body": comment}
        }
    }
    
    if status:
        payload["ticket"]["status"] = status
    if priority:
        payload["ticket"]["priority"] = priority
    if tags:
        payload["ticket"]["additional_tags"] = tags
    
    logger.info(f"Updating Zendesk ticket #{ticket_id}")
    
    try:
        api_base, auth = _get_zendesk_config()
        url = f"{api_base}/tickets/{ticket_id}.json"
        response = requests.put(url, auth=auth, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Successfully updated ticket #{ticket_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update Zendesk ticket: {e}")
        raise


def close_ticket(ticket_id, resolution_comment):
    """
    Close a Zendesk ticket after successful remediation
    
    Args:
        ticket_id (str): Zendesk ticket ID
        resolution_comment (str): Final resolution details
        
    Returns:
        dict: Closed ticket data
    """
    final_comment = f"""
    **Automated Resolution**
    
    {resolution_comment}
    
    - **Resolution Time**: {datetime.utcnow().isoformat()}
    - **Status**: SLE restored to acceptable levels
    - **MTTR**: Reduced via automation
    
    This ticket has been automatically resolved by the Mist SLE automation pipeline.
    """
    
    payload = {
        "ticket": {
            "status": "solved",
            "comment": {"body": final_comment}
        }
    }
    
    logger.info(f"Closing Zendesk ticket #{ticket_id}")
    
    try:
        api_base, auth = _get_zendesk_config()
        url = f"{api_base}/tickets/{ticket_id}.json"
        response = requests.put(url, auth=auth, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        logger.info(f"Successfully closed ticket #{ticket_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to close Zendesk ticket: {e}")
        raise


def get_ticket(ticket_id):
    """
    Retrieve ticket details
    
    Args:
        ticket_id (str): Zendesk ticket ID
        
    Returns:
        dict: Ticket details
    """
    logger.info(f"Fetching Zendesk ticket #{ticket_id}")
    
    try:
        api_base, auth = _get_zendesk_config()
        url = f"{api_base}/tickets/{ticket_id}.json"
        response = requests.get(url, auth=auth, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get Zendesk ticket: {e}")
        raise


def main():
    """
    CLI interface for Zendesk operations
    Called from GitHub Actions workflow
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Zendesk Ticket Management")
    parser.add_argument("--ticket", help="Existing ticket ID", default=None)
    parser.add_argument("--ap_id", help="Access Point ID")
    parser.add_argument("--sle", help="SLE metric type")
    parser.add_argument("--severity", help="Severity level", default="high")
    parser.add_argument("--action", help="Action: create, update, close", default="update")
    parser.add_argument("--comment", help="Comment to add", default="")
    
    args = parser.parse_args()
    
    result = {}
    
    try:
        if args.action == "create":
            result = create_ticket(args.ap_id, args.sle, args.severity)
            print(f"ZENDESK_TICKET_ID={result['ticket']['id']}")
            
        elif args.action == "update":
            if not args.ticket:
                logger.error("Ticket ID required for update")
                sys.exit(1)
            
            comment = args.comment or f"Remediation in progress for {args.sle}"
            result = update_ticket(args.ticket, comment, status="pending")
            
        elif args.action == "close":
            if not args.ticket:
                logger.error("Ticket ID required for close")
                sys.exit(1)
            
            resolution = args.comment or "SLE metrics restored. Issue resolved via automation."
            result = close_ticket(args.ticket, resolution)
        
        # Output result as JSON
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        logger.error(f"Zendesk operation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
