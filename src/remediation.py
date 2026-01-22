"""
Remediation Module
Performs automated remediation actions for SLE failures
"""
import sys
import json
import logging
import time
from datetime import datetime
from mist import reboot_ap, get_client_count, get_ap_stats, validate_credentials
from logic import get_guardrails_config, check_business_hours

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Default guardrails in case rules file is missing
DEFAULT_GUARDRAILS = {
    "min_clients": 3,
    "min_reboot_interval": 1800,
    "max_daily_reboots": 3,
    "business_hours_only": False,
}


def check_guardrails(ap_id):
    """
    Verify that guardrails are satisfied before remediation
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        tuple: (bool: passed, str: reason if failed)
    """
    logger.info(f"Checking guardrails for AP {ap_id}")
    
    try:
        guardrails = get_guardrails_config() or DEFAULT_GUARDRAILS

        # Optional business-hours enforcement
        if guardrails.get("business_hours_only") and not check_business_hours():
            reason = "Outside configured business hours"
            logger.warning(f"Guardrail check failed: {reason}")
            return False, reason

        # Check client count
        client_count = get_client_count(ap_id)
        min_clients = guardrails.get("min_clients", DEFAULT_GUARDRAILS["min_clients"])
        if client_count < min_clients:
            reason = f"Client count ({client_count}) below minimum threshold ({min_clients})"
            logger.warning(f"Guardrail check failed: {reason}")
            return False, reason
        
        # Check AP uptime (proxy for last reboot time)
        ap_stats = get_ap_stats(ap_id)
        uptime = ap_stats.get("uptime", 0)
        
        min_reboot_interval = guardrails.get("min_reboot_interval", DEFAULT_GUARDRAILS["min_reboot_interval"])
        if uptime < min_reboot_interval:
            reason = f"AP uptime ({uptime}s) below minimum reboot interval ({min_reboot_interval}s)"
            logger.warning(f"Guardrail check failed: {reason}")
            return False, reason
        
        logger.info("All guardrails passed")
        return True, "All checks passed"
        
    except Exception as e:
        logger.error(f"Error checking guardrails: {e}")
        return False, f"Error: {str(e)}"


def execute_ap_reboot(ap_id, force=False):
    """
    Execute AP reboot with guardrail checks
    
    Args:
        ap_id (str): Access Point ID
        force (bool): Skip guardrail checks if True
        
    Returns:
        dict: Remediation result
    """
    logger.info(f"Initiating AP reboot for {ap_id} (force={force})")
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "ap_id": ap_id,
        "action": "reboot",
        "status": "pending"
    }
    
    try:
        # Check guardrails unless forced
        if not force:
            passed, reason = check_guardrails(ap_id)
            if not passed:
                result["status"] = "blocked"
                result["reason"] = reason
                logger.warning(f"Reboot blocked by guardrails: {reason}")
                return result
        
        # Execute reboot
        logger.warning(f"Executing reboot for AP {ap_id}")
        reboot_response = reboot_ap(ap_id)
        
        result["status"] = "success"
        result["response"] = reboot_response
        result["message"] = f"Reboot command issued successfully for AP {ap_id}"
        
        logger.info(f"Reboot completed successfully for AP {ap_id}")
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error(f"Reboot failed: {e}")
    
    return result


def execute_wlan_reset(ap_id):
    """
    Execute WLAN reset (placeholder for future implementation)
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        dict: Remediation result
    """
    logger.info(f"WLAN reset requested for AP {ap_id}")
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "ap_id": ap_id,
        "action": "wlan_reset",
        "status": "not_implemented"
    }
    
    # Placeholder for WLAN reset logic
    logger.warning("WLAN reset not yet implemented")
    result["message"] = "WLAN reset functionality pending implementation"
    
    return result


def execute_rrm_adjustment(ap_id):
    """
    Execute RRM (Radio Resource Management) adjustment (placeholder)
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        dict: Remediation result
    """
    logger.info(f"RRM adjustment requested for AP {ap_id}")
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "ap_id": ap_id,
        "action": "rrm_adjustment",
        "status": "not_implemented"
    }
    
    # Placeholder for RRM logic
    logger.warning("RRM adjustment not yet implemented")
    result["message"] = "RRM adjustment functionality pending implementation"
    
    return result


def select_remediation_action(ap_id, sle_type):
    """
    Select appropriate remediation action based on SLE type
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        
    Returns:
        str: Remediation action to perform
    """
    # Simple mapping - can be enhanced with more sophisticated logic
    action_map = {
        "throughput": "reboot",
        "successful-connects": "reboot",
        "gateway-availability": "reboot",
        "dhcp-performance": "reboot",
        "dns-performance": "reboot"
    }
    
    action = action_map.get(sle_type, "reboot")
    logger.info(f"Selected remediation action '{action}' for SLE type '{sle_type}'")
    
    return action


def main():
    """
    CLI interface for remediation
    Called from GitHub Actions workflow
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Mist AP Remediation")
    parser.add_argument("--ap_id", required=True, help="Access Point ID")
    parser.add_argument("--sle", help="SLE metric type")
    parser.add_argument("--action", help="Remediation action (reboot, wlan_reset, rrm)", default=None)
    parser.add_argument("--force", action="store_true", help="Skip guardrail checks")
    parser.add_argument("--output", default="remediation.json", help="Output file")
    
    args = parser.parse_args()
    
    try:
        # Validate credentials
        validate_credentials()
        
        # Determine action
        if args.action:
            action = args.action
        elif args.sle:
            action = select_remediation_action(args.ap_id, args.sle)
        else:
            action = "reboot"  # Default
        
        # Execute remediation
        logger.info(f"Executing remediation action: {action}")
        
        if action == "reboot":
            result = execute_ap_reboot(args.ap_id, force=args.force)
        elif action == "wlan_reset":
            result = execute_wlan_reset(args.ap_id)
        elif action == "rrm":
            result = execute_rrm_adjustment(args.ap_id)
        else:
            raise ValueError(f"Unknown remediation action: {action}")
        
        # Save result
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Remediation result saved to {args.output}")
        
        # Print summary
        print(json.dumps({
            "ap_id": args.ap_id,
            "action": action,
            "status": result["status"],
            "message": result.get("message", "")
        }, indent=2))
        
        # Exit with error code if remediation failed
        if result["status"] in ["error", "blocked"]:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Remediation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
