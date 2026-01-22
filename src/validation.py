"""
Validation Module
Validates that SLE metrics have been restored after remediation
"""
import sys
import json
import logging
import time
from datetime import datetime
from mist import get_sle_metrics, get_ap_stats, validate_credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Validation Configuration
VALIDATION_CONFIG = {
    "poll_interval": 60,  # Seconds between polls
    "max_attempts": 5,  # Maximum number of validation attempts
    "timeout": 300,  # Total timeout in seconds (5 minutes)
    "threshold_score": 90  # Minimum SLE score to consider restored
}


def extract_sle_score(sle_metrics, sle_type):
    """
    Extract the score for a specific SLE metric
    
    Args:
        sle_metrics (dict): SLE metrics data from Mist API
        sle_type (str): SLE metric type
        
    Returns:
        float: SLE score (0-100) or None if not found
    """
    try:
        # Navigate through the SLE metrics structure
        # Example path: client -> throughput -> score
        
        # Map common SLE types to their paths
        sle_paths = {
            "throughput": ["client", "throughput", "score"],
            "successful-connects": ["client", "successful-connects", "score"],
            "gateway-availability": ["infrastructure", "gateway-availability", "score"],
            "dhcp-performance": ["infrastructure", "dhcp-performance", "score"],
            "dns-performance": ["infrastructure", "dns-performance", "score"]
        }
        
        path = sle_paths.get(sle_type)
        if not path:
            logger.warning(f"Unknown SLE type: {sle_type}, using default path")
            return None
        
        # Navigate the nested dictionary
        value = sle_metrics
        for key in path:
            value = value.get(key, {})
        
        if isinstance(value, (int, float)):
            return float(value)
        
        logger.warning(f"Could not extract score for SLE type: {sle_type}")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting SLE score: {e}")
        return None


def check_sle_restored(sle_type, threshold=None):
    """
    Check if SLE metric has been restored to acceptable levels
    
    Args:
        sle_type (str): SLE metric type to check
        threshold (float, optional): Minimum acceptable score
        
    Returns:
        tuple: (bool: restored, float: current_score)
    """
    threshold = threshold or VALIDATION_CONFIG["threshold_score"]
    
    logger.info(f"Checking SLE status for {sle_type} (threshold: {threshold})")
    
    try:
        # Get current SLE metrics
        sle_metrics = get_sle_metrics()
        
        # Extract score for the specific SLE type
        score = extract_sle_score(sle_metrics, sle_type)
        
        if score is None:
            logger.warning("Could not determine SLE score")
            return False, 0.0
        
        restored = score >= threshold
        
        logger.info(f"SLE {sle_type} score: {score:.2f} - {'RESTORED' if restored else 'DEGRADED'}")
        
        return restored, score
        
    except Exception as e:
        logger.error(f"Error checking SLE status: {e}")
        return False, 0.0


def validate_remediation(ap_id, sle_type, threshold=None):
    """
    Validate that remediation was successful by polling SLE metrics
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        threshold (float, optional): Minimum acceptable score
        
    Returns:
        dict: Validation result
    """
    logger.info(f"Starting validation for AP {ap_id}, SLE: {sle_type}")
    
    threshold = threshold or VALIDATION_CONFIG["threshold_score"]
    poll_interval = VALIDATION_CONFIG["poll_interval"]
    max_attempts = VALIDATION_CONFIG["max_attempts"]
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "ap_id": ap_id,
        "sle_type": sle_type,
        "threshold": threshold,
        "status": "pending",
        "attempts": []
    }
    
    start_time = time.time()
    
    for attempt in range(1, max_attempts + 1):
        logger.info(f"Validation attempt {attempt}/{max_attempts}")
        
        # Check if SLE is restored
        restored, score = check_sle_restored(sle_type, threshold)
        
        attempt_data = {
            "attempt": attempt,
            "timestamp": datetime.utcnow().isoformat(),
            "score": score,
            "restored": restored
        }
        result["attempts"].append(attempt_data)
        
        if restored:
            result["status"] = "restored"
            result["final_score"] = score
            result["duration"] = time.time() - start_time
            logger.info(f"✓ SLE restored after {attempt} attempts ({result['duration']:.1f}s)")
            break
        
        # Wait before next attempt (unless it's the last one)
        if attempt < max_attempts:
            logger.info(f"SLE not restored yet (score: {score:.2f}). Waiting {poll_interval}s...")
            time.sleep(poll_interval)
    
    else:
        # Max attempts reached without restoration
        result["status"] = "failed"
        result["final_score"] = score
        result["duration"] = time.time() - start_time
        logger.warning(f"✗ SLE validation failed after {max_attempts} attempts ({result['duration']:.1f}s)")
    
    return result


def validate_ap_online(ap_id):
    """
    Verify that AP is online and responding
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        tuple: (bool: online, str: status)
    """
    logger.info(f"Checking if AP {ap_id} is online")
    
    try:
        ap_stats = get_ap_stats(ap_id)
        status = ap_stats.get("status", "unknown")
        
        online = status == "connected"
        
        logger.info(f"AP {ap_id} status: {status} - {'ONLINE' if online else 'OFFLINE'}")
        
        return online, status
        
    except Exception as e:
        logger.error(f"Error checking AP status: {e}")
        return False, "error"


def comprehensive_validation(ap_id, sle_type):
    """
    Perform comprehensive validation including AP status and SLE metrics
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        
    Returns:
        dict: Comprehensive validation result
    """
    logger.info(f"Starting comprehensive validation for AP {ap_id}")
    
    result = {
        "timestamp": datetime.utcnow().isoformat(),
        "ap_id": ap_id,
        "sle_type": sle_type,
        "overall_status": "pending"
    }
    
    # First, wait a short time for AP to stabilize after reboot
    stabilization_time = 60
    logger.info(f"Waiting {stabilization_time}s for AP stabilization...")
    time.sleep(stabilization_time)
    
    # Check AP online status
    online, ap_status = validate_ap_online(ap_id)
    result["ap_online"] = online
    result["ap_status"] = ap_status
    
    if not online:
        result["overall_status"] = "failed"
        result["reason"] = f"AP not online (status: {ap_status})"
        logger.error(result["reason"])
        return result
    
    # Validate SLE metrics
    sle_validation = validate_remediation(ap_id, sle_type)
    result["sle_validation"] = sle_validation
    
    # Determine overall status
    if sle_validation["status"] == "restored":
        result["overall_status"] = "success"
        result["message"] = f"SLE {sle_type} successfully restored to {sle_validation['final_score']:.2f}"
    else:
        result["overall_status"] = "failed"
        result["message"] = f"SLE {sle_type} validation failed (final score: {sle_validation.get('final_score', 0):.2f})"
    
    return result


def main():
    """
    CLI interface for validation
    Called from GitHub Actions workflow
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Mist SLE Validation")
    parser.add_argument("--ap_id", required=True, help="Access Point ID")
    parser.add_argument("--sle", required=True, help="SLE metric type")
    parser.add_argument("--threshold", type=float, help="Minimum acceptable score", default=None)
    parser.add_argument("--output", default="validation.json", help="Output file")
    
    args = parser.parse_args()
    
    try:
        # Validate credentials
        validate_credentials()
        
        # Perform comprehensive validation
        result = comprehensive_validation(args.ap_id, args.sle)
        
        # Save result
        with open(args.output, "w") as f:
            json.dump(result, f, indent=2)
        
        logger.info(f"Validation result saved to {args.output}")
        
        # Print summary
        print(json.dumps({
            "ap_id": args.ap_id,
            "sle": args.sle,
            "status": result["overall_status"],
            "message": result.get("message", "")
        }, indent=2))
        
        # Exit with appropriate code
        if result["overall_status"] != "success":
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
