"""Look up a device by MAC address.

In a real deployment this queries the NetBox API. To keep the demo runnable offline
and free of any real endpoint, it returns the example device shipped in data/.
Replace `get_data_by_mac_addr` with a real NetBox call when you wire this up.
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
EXAMPLE_DEVICE = os.path.join(DATA_DIR, "example_netbox_device.json")


def get_data_by_mac_addr(mac_addr):
    """Return device data for a MAC address.

    Demo behaviour: ignores the MAC and returns the bundled example device so the
    scripts can be read and traced without a live NetBox.
    """
    if not mac_addr or len(mac_addr.replace(":", "")) < 12:
        return None
    with open(EXAMPLE_DEVICE) as f:
        return json.load(f)


def get_ned_by_model(device_model):
    """Map a device model to an NSO NED id.

    In this design the NED id is stored as a NetBox tag on the device type. Here we
    return a common IOS NED id as an example.
    """
    if not device_model:
        return None
    return "cisco-ios-cli-6.85"


# Example NetBox call (commented out — fill in your own base URL and token):
#
# import requests
# NETBOX_URL = os.environ["NETBOX_URL"]          # e.g. https://netbox.example.net
# NETBOX_TOKEN = os.environ["NETBOX_TOKEN"]      # keep this out of source control
# HEADERS = {"Authorization": f"Token {NETBOX_TOKEN}"}
#
# def get_data_by_mac_addr(mac_addr):
#     r = requests.get(f"{NETBOX_URL}/api/dcim/interfaces/",
#                      params={"mac_address": mac_addr}, headers=HEADERS)
#     results = r.json().get("results", [])
#     if not results:
#         return None
#     device_url = results[0]["device"]["url"]
#     return requests.get(device_url, headers=HEADERS).json()


if __name__ == "__main__":
    print(json.dumps(get_data_by_mac_addr("00:11:22:33:44:55"), indent=2))
