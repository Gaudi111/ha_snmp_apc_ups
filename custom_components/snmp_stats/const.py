from email.policy import default
import logging
import voluptuous as vol
from typing import Final
from datetime import timedelta
from homeassistant.helpers import config_validation as cv
from homeassistant.const import (
    CONF_IP_ADDRESS,
    Platform
)
LOGGER = logging.getLogger(__package__)

DOMAIN = "snmp_stats"
DEFAULT_SCAN_INTERVAL = 10

CONF_CUSTOMIZE_IFACE: Final = "customize_snmp_iface"
CONF_CUSTOMIZE_COMMUNITY: Final = "customize_snmp_community"

CONFIG_SCHEMA_A=vol.Schema(
            {
                vol.Required(CONF_IP_ADDRESS): str,
                vol.Optional(CONF_CUSTOMIZE_IFACE, default=""): str,
                vol.Required(CONF_CUSTOMIZE_COMMUNITY, default="public"): str,
            }
)

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: CONFIG_SCHEMA_A
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS: Final = [Platform.SENSOR]

HOSTNAME_OID = '1.3.6.1.2.1.1.5.0'
CPU_LOAD_1M_OID = '1.3.6.1.4.1.2021.10.1.3.1'
CPU_LOAD_5M_OID = '1.3.6.1.4.1.2021.10.1.3.2'
CPU_LOAD_15M_OID = '1.3.6.1.4.1.2021.10.1.3.3'
UPTIME_OID = '1.3.6.1.2.1.1.3.0'
TCP_ESTABLISHED_OID = '1.3.6.1.2.1.6.9.0'
MEM_REAL_TOTAL_OID = '1.3.6.1.2.1.25.2.3.1.5.1'
MEM_REAL_USED_OID = '1.3.6.1.2.1.25.2.3.1.6.1'
MEM_REAL_BUFFERED_OID = '1.3.6.1.2.1.25.2.3.1.6.6'
MEM_REAL_CACHED_OID = '1.3.6.1.2.1.25.2.3.1.6.7'
IF_DESCR_OID = '1.3.6.1.2.1.2.2.1.2'
IF_NAME_OID = '1.3.6.1.2.1.31.1.1.1.1'
IF_ALIAS_OID = '1.3.6.1.2.1.31.1.1.1.18'
IF_HC_IN_OCTETS_OID = '1.3.6.1.2.1.31.1.1.1.6'
IF_HC_OUT_OCTETS_OID = '1.3.6.1.2.1.31.1.1.1.10'
IF_COUNT_OID = '1.3.6.1.2.1.2.1.0'

def flattenObj(prefix,seperator,obj):
    result={}
    for field in obj:
        val=obj[field]
        valprefix=prefix+seperator+field
        if type(val) is dict:
            sub=flattenObj(valprefix,seperator,val)
            result.update(sub)
        else:
            result[valprefix]=val
    return result
