"""
Mist API Client Module
Handles all interactions with Mist Cloud API for AP management and SLE metrics
"""
import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mist API Configuration
API_BASE = "https://api.mist.com/api/v1"
TOKEN = os.getenv("MIST_API_TOKEN")
SITE_ID = os.getenv("SITE_ID")

# Request headers
headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json"
}


def get_ap_stats(ap_id):
    """
    Retrieve detailed statistics for a specific Access Point
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        dict: AP statistics including health, clients, and performance metrics
    """
    url = f"{API_BASE}/sites/{SITE_ID}/stats/aps/{ap_id}"
    logger.info(f"Fetching AP stats for {ap_id}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully retrieved stats for AP {ap_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get AP stats: {e}")
        raise


def get_ap_details(ap_id):
    """
    Get AP configuration details
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        dict: AP configuration and metadata
    """
    url = f"{API_BASE}/sites/{SITE_ID}/devices/{ap_id}"
    logger.info(f"Fetching AP details for {ap_id}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get AP details: {e}")
        raise


def reboot_ap(ap_id):
    """
    Issue a reboot command to a specific Access Point
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        dict: Status of reboot command
    """
    url = f"{API_BASE}/sites/{SITE_ID}/devices/{ap_id}/restart"
    logger.warning(f"Issuing reboot command to AP {ap_id}")
    
    try:
        response = requests.post(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Reboot command successfully issued to AP {ap_id}")
        return {"status": "reboot_issued", "ap_id": ap_id}
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to reboot AP: {e}")
        raise


def get_sle_metrics(site_id=None):
    """
    Retrieve Service Level Expectation (SLE) metrics for the site
    
    Args:
        site_id (str, optional): Site ID. Defaults to SITE_ID from env.
        
    Returns:
        dict: SLE metrics including scores for various service categories
    """
    site = site_id or SITE_ID
    url = f"{API_BASE}/sites/{site}/sle"
    logger.info(f"Fetching SLE metrics for site {site}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully retrieved SLE metrics")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get SLE metrics: {e}")
        raise


def get_sle_history(metric, start=None, end=None, site_id=None):
    """
    Get historical SLE data for a specific metric
    
    Args:
        metric (str): SLE metric name (e.g., 'throughput', 'successful-connects')
        start (int, optional): Start timestamp
        end (int, optional): End timestamp
        site_id (str, optional): Site ID
        
    Returns:
        dict: Historical SLE data
    """
    site = site_id or SITE_ID
    url = f"{API_BASE}/sites/{site}/sle/{metric}/metrics"
    
    params = {}
    if start:
        params['start'] = start
    if end:
        params['end'] = end
    
    logger.info(f"Fetching SLE history for {metric}")
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get SLE history: {e}")
        raise


def get_wlan_list(site_id=None):
    """
    Get list of WLANs configured on the site
    
    Args:
        site_id (str, optional): Site ID
        
    Returns:
        list: List of WLAN configurations
    """
    site = site_id or SITE_ID
    url = f"{API_BASE}/sites/{site}/wlans"
    logger.info(f"Fetching WLAN list for site {site}")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to get WLAN list: {e}")
        raise


def update_wlan(wlan_id, config, site_id=None):
    """
    Update WLAN configuration (used for WLAN reset/reconfiguration)
    
    Args:
        wlan_id (str): WLAN ID
        config (dict): WLAN configuration changes
        site_id (str, optional): Site ID
        
    Returns:
        dict: Updated WLAN configuration
    """
    site = site_id or SITE_ID
    url = f"{API_BASE}/sites/{site}/wlans/{wlan_id}"
    logger.info(f"Updating WLAN {wlan_id}")
    
    try:
        response = requests.put(url, headers=headers, json=config, timeout=30)
        response.raise_for_status()
        logger.info(f"Successfully updated WLAN {wlan_id}")
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to update WLAN: {e}")
        raise


def get_client_count(ap_id):
    """
    Get current client count for an Access Point
    
    Args:
        ap_id (str): Access Point ID
        
    Returns:
        int: Number of connected clients
    """
    stats = get_ap_stats(ap_id)
    client_count = stats.get('num_clients', 0)
    logger.info(f"AP {ap_id} has {client_count} clients")
    return client_count


def validate_credentials():
    """
    Validate that Mist API credentials are properly configured
    
    Returns:
        bool: True if credentials are valid
        
    Raises:
        ValueError: If credentials are missing or invalid
    """
    if not TOKEN:
        raise ValueError("MIST_API_TOKEN environment variable not set")
    if not SITE_ID:
        raise ValueError("SITE_ID environment variable not set")
    
    # Test credentials with a simple API call
    try:
        url = f"{API_BASE}/self"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        logger.info("Mist API credentials validated successfully")
        return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Credential validation failed: {e}")
        raise ValueError(f"Invalid Mist API credentials: {e}")
