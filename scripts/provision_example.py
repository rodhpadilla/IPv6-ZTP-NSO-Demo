"""Apply a golden configuration to a device through Cisco NSO over RESTCONF.

The device model decides which NSO service package (golden config) to apply. The
service reads a few variables (hostname, IPv6 prefix) and NSO renders and pushes the
device configuration.

Connection values come from environment variables. See config.example.env.
"""

import os
import sys

import requests
from requests.auth import HTTPBasicAuth

from netbox import get_data_by_mac_addr

NSO_HOST = os.environ.get("NSO_HOST", "<nso-host>")
NSO_USER = os.environ.get("NSO_USER", "<nso-user>")
NSO_PASS = os.environ.get("NSO_PASS", "<nso-pass>")

NSO = f"http://[{NSO_HOST}]:8080/restconf"
AUTH = HTTPBasicAuth(NSO_USER, NSO_PASS)
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}

# Map a device model to the NSO service package that holds its golden config.
MODEL_TO_SERVICE = {
    "Catalyst 9300-24UX": "cisco-9300-std-conf",
    "Catalyst 9300L-48P-4X": "cisco-9300l-std-conf",
}


def push_golden_config(service, activity, device, hostname, ipv6_prefix):
    payload = {
        f"{service}:{service}": [
            {
                "name": activity,
                "device": device,
                "hostname": hostname,
                "ipv6-prefix": ipv6_prefix,
            }
        ]
    }
    r = requests.post(f"{NSO}/data/", json=payload, headers=HEADERS, auth=AUTH)
    return r.ok


def provision(mac_addr):
    device = get_data_by_mac_addr(mac_addr)
    if not device:
        print(f"MAC {mac_addr} not found")
        return False

    model = device["device_type"]["model"]
    service = MODEL_TO_SERVICE.get(model)
    if not service:
        print(f"No service package mapped for model '{model}'")
        return False

    ctx = device["local_context_data"]
    ok = push_golden_config(
        service=service,
        activity=ctx["activity-name"],
        device=device["name"],
        hostname=ctx["new-hostname"],
        ipv6_prefix=ctx["ipv6-prefix"],
    )
    print(f"{device['name']}: provision {'ok' if ok else 'failed'}")
    return ok


if __name__ == "__main__":
    mac = sys.argv[1] if len(sys.argv) > 1 else "00:11:22:33:44:55"
    sys.exit(0 if provision(mac) else 1)
