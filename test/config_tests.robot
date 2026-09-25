*** Settings ***
Documentation    Example post-provision checks. Uses the demo NetBox lookup, which
...              returns the bundled example device so the suite can be read offline.
Library          Collections
Library          ../scripts/netbox.py

*** Variables ***
${mac_addr}      00:11:22:33:44:55

*** Test Cases ***
Get Device Data From NetBox
    [Documentation]    The device should be resolvable by its MAC address
    ${data}=       Get Data By Mac Addr    ${mac_addr}
    Should Not Be Equal    ${data}    ${None}
    ${name}=       Get From Dictionary     ${data}    name
    Set Suite Variable    ${name}

Expected Hostname Is Defined
    [Documentation]    NetBox should carry the target hostname for the device
    ${data}=       Get Data By Mac Addr    ${mac_addr}
    ${ctx}=        Get From Dictionary     ${data}    local_context_data
    ${hostname}=   Get From Dictionary     ${ctx}     new-hostname
    Should Not Be Empty    ${hostname}

# In a real run you would add a check that queries NSO over RESTCONF and confirms the
# hostname NSO applied matches ${hostname}, for example with a curl to:
#   http://[<nso-host>]:8080/restconf/data/tailf-ncs:devices/device=${name}/config
