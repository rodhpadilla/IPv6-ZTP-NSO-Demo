"""Onboard a device into Cisco NSO over RESTCONF.

Steps:
  1. Look up the device in NetBox by MAC.
  2. Add it to NSO (name, IPv6 address, authgroup, NED).
  3. Fetch its SSH host keys.
  4. sync-from to read its running config into NSO.

All connection values come from environment variables so nothing sensitive lives in
source control. See config.example.env.
"""

import os
import sys

import requests
from requests.auth import HTTPBasicAuth

from netbox import get_data_by_mac_addr, get_ned_by_model

NSO_HOST = os.environ.get("NSO_HOST", "<nso-host>")
NSO_USER = os.environ.get("NSO_USER", "<nso-user>")
NSO_PASS = os.environ.get("NSO_PASS", "<nso-pass>")
NSO_AUTHGROUP = os.environ.get("NSO_AUTHGROUP", "default")

NSO = f"http://[{NSO_HOST}]:8080/restconf"
AUTH = HTTPBasicAuth(NSO_USER, NSO_PASS)
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json",
}


def add_device(name, ipv6_address, authgroup, ned_id):
    payload = {
        "tailf-ncs:device": [
            {
                "name": name,
                "address": ipv6_address,
                "authgroup": authgroup,
                "device-type": {"cli": {"ned-id": f"{ned_id}:{ned_id}"}},
                "state": {"admin-state": "unlocked"},
            }
        ]
    }
    r = requests.post(f"{NSO}/data/tailf-ncs:devices",
                      json=payload, headers=HEADERS, auth=AUTH)
    return r.ok


def fetch_host_keys(name):
    r = requests.post(f"{NSO}/data/tailf-ncs:devices/device={name}/ssh/fetch-host-keys",
                      headers=HEADERS, auth=AUTH)
    return r.ok


def sync_from(name):
    r = requests.post(f"{NSO}/data/tailf-ncs:devices/device={name}/sync-from",
                      headers=HEADERS, auth=AUTH)
    return r.ok


def onboard(mac_addr):
    device = get_data_by_mac_addr(mac_addr)
    if not device:
        print(f"MAC {mac_addr} not found")
        return False

    name = device["name"]
    ipv6 = device["primary_ip6"]["address"].split("/")[0]
    ned_id = get_ned_by_model(device["device_type"]["model"])

    if not add_device(name, ipv6, NSO_AUTHGROUP, ned_id):
        print(f"{name}: add-device failed")
        return False
    print(f"{name}: added to NSO")

    if not fetch_host_keys(name):
        print(f"{name}: fetch-host-keys failed")
        return False
    print(f"{name}: host keys fetched")

    if not sync_from(name):
        print(f"{name}: sync-from failed")
        return False
    print(f"{name}: synced")
    return True


if __name__ == "__main__":
    mac = sys.argv[1] if len(sys.argv) > 1 else "00:11:22:33:44:55"
    sys.exit(0 if onboard(mac) else 1)
