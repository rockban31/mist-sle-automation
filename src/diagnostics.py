"""
Diagnostics Module
Collects detailed diagnostics from Mist API for troubleshooting SLE issues
"""
import sys
import json
import logging
from datetime import datetime
from mist import get_ap_stats, get_ap_details, get_sle_metrics, get_client_count, validate_credentials

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def collect_ap_diagnostics(ap_id):
    """
    Collect comprehensive diagnostics for an Access Point
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        dict: Diagnostic data including stats, details, and client info
    """
    logger.info(f"Starting diagnostics collection for AP {ap_id}")
    
    diagnostics = {
        "timestamp": datetime.utcnow().isoformat(),
        "ap_id": ap_id,
        "status": "success"
    }
    
    try:
        # Get AP statistics
        logger.info("Fetching AP statistics...")
        ap_stats = get_ap_stats(ap_id)
        diagnostics["ap_stats"] = ap_stats
        
        # Get AP details/configuration
        logger.info("Fetching AP details...")
        ap_details = get_ap_details(ap_id)
        diagnostics["ap_details"] = ap_details
        
        # Get client count
        logger.info("Fetching client count...")
        client_count = get_client_count(ap_id)
        diagnostics["client_count"] = client_count
        
        # Extract key metrics
        diagnostics["key_metrics"] = {
            "status": ap_stats.get("status", "unknown"),
            "uptime": ap_stats.get("uptime", 0),
            "clients": client_count,
            "cpu_util": ap_stats.get("cpu_util", 0),
            "mem_util": ap_stats.get("mem_util", 0),
            "ip": ap_stats.get("ip", "N/A"),
            "model": ap_details.get("model", "N/A"),
            "version": ap_stats.get("version", "N/A")
        }
        
        logger.info(f"Diagnostics collection complete for AP {ap_id}")
        
    except Exception as e:
        logger.error(f"Error collecting diagnostics: {e}")
        diagnostics["status"] = "error"
        diagnostics["error"] = str(e)
    
    return diagnostics


def collect_sle_diagnostics(sle_type=None):
    """
    Collect SLE metrics and identify issues
    
    Args:
        sle_type (str, optional): Specific SLE metric to focus on
        
    Returns:
        dict: SLE diagnostic data
    """
    logger.info("Collecting SLE diagnostics")
    
    diagnostics = {
        "timestamp": datetime.utcnow().isoformat(),
        "sle_type": sle_type,
        "status": "success"
    }
    
    try:
        # Get current SLE metrics
        sle_metrics = get_sle_metrics()
        diagnostics["sle_metrics"] = sle_metrics
        
        # Identify issues
        issues = []
        
        # Check throughput
        throughput_score = sle_metrics.get("client", {}).get("throughput", {}).get("score", 100)
        if throughput_score < 90:
            issues.append({
                "metric": "throughput",
                "score": throughput_score,
                "severity": "high" if throughput_score < 70 else "medium"
            })
        
        # Check successful connects
        connect_score = sle_metrics.get("client", {}).get("successful-connects", {}).get("score", 100)
        if connect_score < 90:
            issues.append({
                "metric": "successful-connects",
                "score": connect_score,
                "severity": "high" if connect_score < 70 else "medium"
            })
        
        diagnostics["issues"] = issues
        diagnostics["issue_count"] = len(issues)
        
        logger.info(f"SLE diagnostics complete. Found {len(issues)} issues")
        
    except Exception as e:
        logger.error(f"Error collecting SLE diagnostics: {e}")
        diagnostics["status"] = "error"
        diagnostics["error"] = str(e)
    
    return diagnostics


def generate_diagnostic_report(ap_id, sle_type):
    """
    Generate a comprehensive diagnostic report
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        
    Returns:
        dict: Complete diagnostic report
    """
    logger.info(f"Generating diagnostic report for AP {ap_id}, SLE: {sle_type}")
    
    report = {
        "report_timestamp": datetime.utcnow().isoformat(),
        "ap_id": ap_id,
        "sle_type": sle_type
    }
    
    # Collect AP diagnostics
    report["ap_diagnostics"] = collect_ap_diagnostics(ap_id)
    
    # Collect SLE diagnostics
    report["sle_diagnostics"] = collect_sle_diagnostics(sle_type)
    
    # Determine if remediation is needed
    ap_status = report["ap_diagnostics"].get("status")
    sle_issues = report["sle_diagnostics"].get("issue_count", 0)
    
    report["remediation_needed"] = (ap_status == "success" and sle_issues > 0)
    
    # Recommendations
    recommendations = []
    
    if report["ap_diagnostics"].get("client_count", 0) < 3:
        recommendations.append("Low client count - remediation may have limited impact")
    
    if report["ap_diagnostics"].get("key_metrics", {}).get("uptime", 0) < 1800:
        recommendations.append("AP recently rebooted - allow stabilization time")
    
    report["recommendations"] = recommendations
    
    return report


def main():
    """
    CLI interface for diagnostics
    Called from GitHub Actions workflow
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Mist AP Diagnostics")
    parser.add_argument("--ap_id", required=True, help="Access Point ID")
    parser.add_argument("--sle", required=True, help="SLE metric type")
    parser.add_argument("--output", default="diagnostics.json", help="Output file")
    
    args = parser.parse_args()
    
    try:
        # Validate credentials first
        validate_credentials()
        
        # Generate diagnostic report
        report = generate_diagnostic_report(args.ap_id, args.sle)
        
        # Save to file
        with open(args.output, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Diagnostic report saved to {args.output}")
        
        # Print summary to stdout
        print(json.dumps({
            "ap_id": args.ap_id,
            "sle": args.sle,
            "status": report["ap_diagnostics"]["status"],
            "remediation_needed": report["remediation_needed"],
            "client_count": report["ap_diagnostics"].get("client_count", 0)
        }, indent=2))
        
    except Exception as e:
        logger.error(f"Diagnostics failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
