"""
Logic Module
Contains decision logic and rules for SLE automation
"""
import logging
import yaml
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sle_rules(rules_file="rules/sle_rules.yaml"):
    """
    Load SLE rules configuration from YAML file
    
    Args:
        rules_file (str): Path to rules file
        
    Returns:
        dict: Rules configuration
    """
    try:
        rules_path = Path(rules_file)
        if not rules_path.exists():
            logger.warning(f"Rules file not found: {rules_file}, using defaults")
            return get_default_rules()
        
        with open(rules_path, 'r') as f:
            rules = yaml.safe_load(f)
        
        logger.info(f"Loaded SLE rules from {rules_file}")
        return rules
        
    except Exception as e:
        logger.error(f"Error loading rules: {e}")
        return get_default_rules()


def get_default_rules():
    """
    Get default rules if configuration file is not available
    
    Returns:
        dict: Default rules
    """
    return {
        "sle_thresholds": {
            "critical": 60,
            "high": 70,
            "medium": 80,
            "low": 90
        },
        "guardrails": {
            "min_clients": 3,
            "min_reboot_interval": 1800,
            "max_daily_reboots": 3
        },
        "validation": {
            "poll_interval": 60,
            "max_attempts": 5,
            "threshold_score": 90
        }
    }


def determine_severity(sle_score, sle_type="generic"):
    """
    Determine severity level based on SLE score
    
    Args:
        sle_score (float): SLE score (0-100)
        sle_type (str): SLE metric type
        
    Returns:
        str: Severity level (critical, high, medium, low)
    """
    rules = load_sle_rules()
    thresholds = rules.get("sle_thresholds", {})
    
    if sle_score < thresholds.get("critical", 60):
        return "critical"
    elif sle_score < thresholds.get("high", 70):
        return "high"
    elif sle_score < thresholds.get("medium", 80):
        return "medium"
    else:
        return "low"


def select_remediation_action(sle_type, ap_id=None):
    """
    Select appropriate remediation action based on SLE type and AP state
    
    Args:
        sle_type (str): SLE metric type
        ap_id (str, optional): AP ID for state-based decisions
        
    Returns:
        str: Recommended remediation action
    """
    rules = load_sle_rules()
    strategies = rules.get("remediation_strategies", {})
    
    # Get remediation strategy for this SLE type
    sle_strategy = strategies.get(sle_type, [])
    
    if not sle_strategy:
        logger.warning(f"No remediation strategy for SLE type: {sle_type}, defaulting to reboot")
        return "reboot"
    
    # For now, select highest priority action
    # Future: Implement more sophisticated logic based on AP state
    sorted_actions = sorted(sle_strategy, key=lambda x: x.get("priority", 99))
    
    if sorted_actions:
        action = sorted_actions[0].get("action", "reboot")
        logger.info(f"Selected remediation action '{action}' for SLE type '{sle_type}'")
        return action
    
    return "reboot"


def should_remediate(ap_id, sle_type, sle_score):
    """
    Determine if remediation should be attempted
    
    Args:
        ap_id (str): Access Point ID
        sle_type (str): SLE metric type
        sle_score (float): Current SLE score
        
    Returns:
        tuple: (bool: should_remediate, str: reason)
    """
    rules = load_sle_rules()
    
    # Check if score is below threshold
    threshold = rules.get("validation", {}).get("threshold_score", 90)
    
    if sle_score >= threshold:
        return False, f"SLE score {sle_score} is above threshold {threshold}"
    
    # Add more sophisticated logic here:
    # - Check AP history
    # - Check time of day
    # - Check site-wide issues
    # - etc.
    
    return True, "SLE score below threshold, remediation recommended"


def get_zendesk_priority(sle_type, severity):
    """
    Map SLE type and severity to Zendesk priority
    
    Args:
        sle_type (str): SLE metric type
        severity (str): Severity level
        
    Returns:
        str: Zendesk priority (urgent, high, normal, low)
    """
    rules = load_sle_rules()
    priority_map = rules.get("zendesk", {}).get("priority_map", {})
    
    # Get mapped priority
    priority = priority_map.get(severity, "normal")
    
    # Special cases for critical SLE types
    critical_sles = ["gateway-availability", "dhcp-performance"]
    if sle_type in critical_sles and priority != "urgent":
        priority = "high"
    
    return priority


def check_business_hours():
    """
    Check if current time is within business hours
    
    Returns:
        bool: True if within business hours
    """
    from datetime import datetime
    import pytz
    
    rules = load_sle_rules()
    guardrails = rules.get("guardrails", {})
    
    # Check if business hours enforcement is enabled
    if not guardrails.get("business_hours_only", False):
        return True  # Always allow if not enforcing
    
    # Get business hours configuration
    bh_config = guardrails.get("business_hours", {})
    start_time = bh_config.get("start", "08:00")
    end_time = bh_config.get("end", "18:00")
    timezone = bh_config.get("timezone", "UTC")
    
    # Get current time in configured timezone
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    current_time = now.strftime("%H:%M")
    
    # Simple time comparison
    within_hours = start_time <= current_time <= end_time
    
    logger.info(f"Business hours check: {within_hours} (current: {current_time}, hours: {start_time}-{end_time} {timezone})")
    
    return within_hours


def get_validation_config():
    """
    Get validation configuration
    
    Returns:
        dict: Validation configuration
    """
    rules = load_sle_rules()
    return rules.get("validation", {})


def get_guardrails_config():
    """
    Get guardrails configuration
    
    Returns:
        dict: Guardrails configuration
    """
    rules = load_sle_rules()
    return rules.get("guardrails", {})
