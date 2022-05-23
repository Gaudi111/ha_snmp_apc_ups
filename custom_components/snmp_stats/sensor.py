from dataclasses import dataclass
from pysnmp import hlapi
from pysnmp.error import PySnmpError
import time
import traceback
from datetime import datetime, timedelta
import sys
# pylint: disable=unused-wildcard-import
from .const import * 
# pylint: enable=unused-wildcard-import
import threading
import time
from string import Formatter
from homeassistant.components.sensor import (
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.entity import Entity

from homeassistant.const import (
    CONF_IP_ADDRESS,
    EVENT_HOMEASSISTANT_STOP, 
    CONF_SCAN_INTERVAL,
)

from homeassistant.const import (
    DATA_KILOBYTES,
    PERCENTAGE,
    DATA_RATE_MEGABYTES_PER_SECOND,
    DATA_RATE_MEGABITS_PER_SECOND,
    DATA_MEGABYTES
)


async def async_setup_entry(hass, config_entry,async_add_entities):
    """Set up the sensor platform."""
    LOGGER.info('Setup snmp_stats')
    ipaddress=config_entry.data.get(CONF_IP_ADDRESS)
    community=config_entry.data.get(CONF_CUSTOMIZE_COMMUNITY)
    iface_list=config_entry.data.get(CONF_CUSTOMIZE_IFACE)
    updateIntervalSeconds=config_entry.options.get(CONF_SCAN_INTERVAL)
    maxretries=3
    
    for i in range(maxretries):
        try:
            monitor = SnmpStatisticsMonitor(ipaddress,community,iface_list,updateIntervalSeconds,async_add_entities)
            break
        except:
            if i==maxretries-1:
                raise


        
        
    hass.data[DOMAIN][config_entry.entry_id]={"monitor":monitor}
    
    
    monitor.start()
    def _stop_monitor(_event):
        monitor.stopped=True
    #hass.states.async_set
    hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, _stop_monitor)
    LOGGER.info('Init done')
    return True

def strfdelta(tdelta, fmt='{D:02}d {H:02}h {M:02}m {S:02}s', inputtype='timedelta'):
    """Convert a datetime.timedelta object or a regular number to a custom-
    formatted string, just like the stftime() method does for datetime.datetime
    objects.

    The fmt argument allows custom formatting to be specified.  Fields can 
    include seconds, minutes, hours, days, and weeks.  Each field is optional.

    Some examples:
        '{D:02}d {H:02}h {M:02}m {S:02}s' --> '05d 08h 04m 02s' (default)
        '{W}w {D}d {H}:{M:02}:{S:02}'     --> '4w 5d 8:04:02'
        '{D:2}d {H:2}:{M:02}:{S:02}'      --> ' 5d  8:04:02'
        '{H}h {S}s'                       --> '72h 800s'

    The inputtype argument allows tdelta to be a regular number instead of the  
    default, which is a datetime.timedelta object.  Valid inputtype strings: 
        's', 'seconds', 
        'm', 'minutes', 
        'h', 'hours', 
        'd', 'days', 
        'w', 'weeks'
    """

    # Convert tdelta to integer seconds.
    if inputtype == 'timedelta':
        remainder = int(tdelta.total_seconds())
    elif inputtype in ['s', 'seconds']:
        remainder = int(tdelta)
    elif inputtype in ['m', 'minutes']:
        remainder = int(tdelta)*60
    elif inputtype in ['h', 'hours']:
        remainder = int(tdelta)*3600
    elif inputtype in ['d', 'days']:
        remainder = int(tdelta)*86400
    elif inputtype in ['w', 'weeks']:
        remainder = int(tdelta)*604800

    f = Formatter()
    desired_fields = [field_tuple[1] for field_tuple in f.parse(fmt)]
    possible_fields = ('W', 'D', 'H', 'M', 'S')
    constants = {'W': 604800, 'D': 86400, 'H': 3600, 'M': 60, 'S': 1}
    values = {}
    for field in possible_fields:
        if field in desired_fields and field in constants:
            values[field], remainder = divmod(remainder, constants[field])
    return f.format(fmt, **values)

SENSOR_TYPES: dict[str, SensorEntityDescription] = {
    "memory": SensorEntityDescription(
        key="memory",
        native_unit_of_measurement=DATA_KILOBYTES,
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=DATA_KILOBYTES,
    ),
    "memory_percent": SensorEntityDescription(
        key="memory_percent",
        native_unit_of_measurement=PERCENTAGE,
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=PERCENTAGE,
    ),
    "cpu": SensorEntityDescription(
        key="memory_used",
        native_unit_of_measurement=DATA_KILOBYTES,
        icon="mdi:memory",
        state_class=SensorStateClass.MEASUREMENT,
        unit_of_measurement=DATA_KILOBYTES,
    ),
    "load_15m": SensorEntityDescription(
        key="load_15m",
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "load_1m": SensorEntityDescription(
        key="load_1m",
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "load_5m": SensorEntityDescription(
        key="load_5m",
        icon="mdi:cpu-64-bit",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "uptime": SensorEntityDescription(
        key="uptime",
        icon="mdi:clock",
        state_class=SensorStateClass.TOTAL,
    ),
    "throughput_network_out_mbit":SensorEntityDescription(
        key="throughput_network_out_mbit",
        native_unit_of_measurement=DATA_RATE_MEGABITS_PER_SECOND,
        unit_of_measurement=DATA_RATE_MEGABITS_PER_SECOND,
        icon="mdi:cloud-upload",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "throughput_network_in_mbit":SensorEntityDescription(
        key="throughput_network_in_mbit",
        native_unit_of_measurement=DATA_RATE_MEGABITS_PER_SECOND,
        unit_of_measurement=DATA_RATE_MEGABITS_PER_SECOND,
        icon="mdi:cloud-download",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "throughput_network_out_mbyte":SensorEntityDescription(
        key="throughput_network_out_mbyte",
        native_unit_of_measurement=DATA_RATE_MEGABYTES_PER_SECOND,
        unit_of_measurement=DATA_RATE_MEGABYTES_PER_SECOND,
        icon="mdi:cloud-upload",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "throughput_network_in_mbyte":SensorEntityDescription(
        key="throughput_network_in_mbyte",
        native_unit_of_measurement=DATA_RATE_MEGABYTES_PER_SECOND,
        unit_of_measurement=DATA_RATE_MEGABYTES_PER_SECOND,
        icon="mdi:cloud-download",
        state_class=SensorStateClass.MEASUREMENT,
    ),
    "throughput_total_network_out":SensorEntityDescription(
        key="throughput_network_out",
        native_unit_of_measurement=DATA_MEGABYTES,
        unit_of_measurement=DATA_MEGABYTES,
        icon="mdi:cloud-upload",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "throughput_total_network_in":SensorEntityDescription(
        key="throughput_network_in",
        native_unit_of_measurement=DATA_MEGABYTES,
        unit_of_measurement=DATA_MEGABYTES,
        icon="mdi:cloud-download",
        state_class=SensorStateClass.TOTAL_INCREASING,
    ),
    "total_tcp":SensorEntityDescription(
        key="total_tcp",
        icon="mdi:network",
        native_unit_of_measurement="",
        unit_of_measurement="",
        state_class=SensorStateClass.MEASUREMENT,
    ),
}

class SnmpStatisticsSensor(Entity):
    def __init__(self,id,entity_description,name=None):
        self._attributes = {}
        self._state ="NOTRUN"
        self.entity_id=id
        self.entity_description = entity_description
        if name is None:
            name=id
        self._name=name
        LOGGER.info("Create Sensor {0}".format(id))

    def set_state(self, state):
        """Set the state."""
        if self._state==state:
            return
        self._state = state
        if self.enabled:
            self.schedule_update_ha_state()


    def set_attributes(self, attributes):
        """Set the state attributes."""
        self._attributes = attributes

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this sensor."""
        return self.entity_id


    @property
    def should_poll(self):
        """Only poll to update phonebook, if defined."""
        return False
    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        return self._attributes
    @property
    def state(self):
        """Return the state of the device."""
        return self._state
    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name
    def update(self):
        LOGGER.info("update "+self.entity_id)

@dataclass
class SysMonitorSensorEntityDescription(SensorEntityDescription):
    """Description for System Monitor sensor entities."""

    mandatory_arg: bool = False

class SnmpStatisticsMonitor:

    def __init__(self,target_ip,community,iface_list,updateIntervalSeconds=1,async_add_entities=None):
        self.meterSensors={}
        self.stopped = False
        self.async_add_entities=async_add_entities
        self.updateIntervalSeconds=updateIntervalSeconds
        self.current_if_data={}
        self.current_if_data_time=0
        self.stat_time=0
        self.target_ip=target_ip
        self.community=community
        if isinstance(iface_list,str):
            self.iface_list=iface_list.split()
        else:
            self.iface_list=[]
        self.hostname=None
        self.cpuload1=None
        self.cpuload2=None
        self.cpuload3=None
        self.uptime=None
        self.memRealUsed=None
        self.memRealPercent=None
        self.memFree=None
        self.memBuffers=None
        self.memCached=None
        self.totalTcpEstablished=None
        self.update_stats()#try this to throw error if not working.
        if async_add_entities is not None:
            self.setupEntities()

    #region static methods
    @staticmethod
    def get(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        handler = hlapi.getCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            *__class__.construct_object_types(oids)
        )
        return __class__.fetch(handler, 1)[0]
    
    @staticmethod
    def construct_object_types(list_of_oids):
        object_types = []
        for oid in list_of_oids:
            object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
        return object_types

    @staticmethod
    def get_bulk(target, oids, credentials, count, start_from=0, port=161,
                engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        handler = hlapi.bulkCmd(
            engine,
            credentials,
            hlapi.UdpTransportTarget((target, port)),
            context,
            start_from, count,
            *__class__.construct_object_types(oids)
        )
        return __class__.fetch(handler, count)

    @staticmethod
    def get_bulk_auto(target, oids, credentials, count_oid, start_from=0, port=161,
                    engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
        count = __class__.get(target, [count_oid], credentials, port, engine, context)[count_oid]
        return __class__.get_bulk(target, oids, credentials, count, start_from, port, engine, context)
    @staticmethod
    def cast(value):
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                return float(value)
            except (ValueError, TypeError):
                try:
                    return str(value)
                except (ValueError, TypeError):
                    pass
        return value
    @staticmethod
    def fetch(handler, count):
        result = []
        for i in range(count):
            try:
                error_indication, error_status, error_index, var_binds = next(handler)
                if not error_indication and not error_status:
                    items = {}
                    for var_bind in var_binds:
                        items[str(var_bind[0])] = __class__.cast(var_bind[1])
                    result.append(items)
                else:
                    raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
            except StopIteration:
                break
        return result

    #endregion
    def update_stats(self):
        self.update_netif_stats()
        more_data=__class__.get(self.target_ip,[
            HOSTNAME_OID,
            CPU_LOAD_1M_OID,
            CPU_LOAD_5M_OID,
            CPU_LOAD_15M_OID,
            UPTIME_OID,
            MEM_REAL_TOTAL_OID,
            MEM_REAL_USED_OID,
            MEM_REAL_BUFFERED_OID,
            MEM_REAL_CACHED_OID,
            TCP_ESTABLISHED_OID
            ],hlapi.CommunityData(self.community))

        self.hostname=more_data[HOSTNAME_OID]
        self.cpuload1=more_data[CPU_LOAD_1M_OID]
        self.cpuload2=more_data[CPU_LOAD_5M_OID]
        self.cpuload3=more_data[CPU_LOAD_15M_OID]
        snmp_uptime_ticks = int(more_data[UPTIME_OID] or 0)
        uptime_seconds = snmp_uptime_ticks/100
        self.uptime= strfdelta(timedelta(seconds=uptime_seconds), '{D:2}d {H:2}h {M:2}m {S:2}s')
        self.totalTcpEstablished = int(more_data[TCP_ESTABLISHED_OID] or 0)
        memRealTotal = int(more_data[MEM_REAL_TOTAL_OID] or 0)
        self.memRealUsed = int(more_data[MEM_REAL_USED_OID] or 0)
        memRealBuffered = int(more_data[MEM_REAL_BUFFERED_OID] or 0)
        memCached = int(more_data[MEM_REAL_CACHED_OID] or 0)
        if memRealTotal:
            self.memRealPercent = round(( (self.memRealUsed - memRealBuffered - memCached) / memRealTotal ) * 100, 1)
        else:
            self.memRealPercent = 0
        self.memFree = memRealTotal - self.memRealUsed
        self.memBuffers = memRealBuffered
        self.memCached = memCached

    def update_netif_stats(self):
        if_data=self.current_if_data
        its = __class__.get_bulk_auto(self.target_ip, [
            IF_DESCR_OID,#v1, ifDescr
            #'1.3.6.1.2.1.2.2.1.16',#v1, ifOutOctets
            #'1.3.6.1.2.1.2.2.1.10',#v1, ifInOctets
            IF_NAME_OID,#v2, ifName
            IF_ALIAS_OID,#v2, ifAlias
            IF_HC_IN_OCTETS_OID, #v2, ifHCInOctets
            IF_HC_OUT_OCTETS_OID, #v2, ifHCOutOctets
        ], hlapi.CommunityData(self.community, mpModel=1),
            IF_COUNT_OID #v1, ifCount
        )

        for k in if_data:
            if_data[k]['rx_octets_prev']=if_data[k]['rx_octets']
            if_data[k]['tx_octets_prev']=if_data[k]['tx_octets']



        for it in its:
            for k, v in it.items():
                oidParts=k.split('.')
                ifId=oidParts[-1]
                infotype=oidParts[-2]
                if ifId not in if_data:
                    if_data[ifId]={
                        'name':'',
                        'name2':'',
                        'alias':'',
                        'rx_octets':-1,
                        'tx_octets':-1,
                        'rx_speed_octets':-1.0,
                        'tx_speed_octets':-1.0,
                        'rx_octets_prev':-1.0,
                        'tx_octets_prev':-1.0,
                        'last_stat_time':time.time(),
                        'rx_diff':-1,
                        'tx_diff':-1
                        }
                
                if infotype=='2':
                    if_data[ifId]['name']=v
                elif infotype=='1':
                    if_data[ifId]['name2']=v
                elif infotype=='18':
                    if_data[ifId]['alias']=v
                elif k.find('2.2.1.10')>-1:
                    if_data[ifId]['rx_octets']=v
                elif k.find('2.2.1.16')>-1:
                    if_data[ifId]['tx_octets']=v
                elif k.find('31.1.1.1.6')>-1:
                    if_data[ifId]['rx_octets']=v
                elif k.find('31.1.1.1.10')>-1:
                    if_data[ifId]['tx_octets']=v


        new_if_data_time=time.time()
        for k in self.current_if_data:
            cur_data=self.current_if_data[k]
            
            timediff_statistics=new_if_data_time-cur_data['last_stat_time']
            timediff_stat_seconds=timediff_statistics#/1000.0

            rx_diff=cur_data['rx_octets']-cur_data['rx_octets_prev']
            tx_diff=cur_data['tx_octets']-cur_data['tx_octets_prev']


            cur_data['rx_diff']=rx_diff
            cur_data['tx_diff']=tx_diff

            if timediff_stat_seconds<1:
                continue

            if rx_diff==0 and tx_diff==0 and timediff_stat_seconds<4:##wait until really going to 0
                continue

            rx_byte_s=rx_diff/timediff_stat_seconds
            tx_byte_s=tx_diff/timediff_stat_seconds
            cur_data['last_stat_time']=new_if_data_time

            cur_data['rx_speed_octets']=rx_byte_s
            cur_data['tx_speed_octets']=tx_byte_s


        self.current_if_data=if_data
        self.current_if_data_time=new_if_data_time

    def start(self):
        threading.Thread(target=self.watcher).start()
    def watcher(self):
        LOGGER.info(f'Start Watcher Thread - updateInterval:{self.updateIntervalSeconds}')

        while not self.stopped:
            try:
                #LOGGER.warning('Get PowerMeters: ')
                self.update_stats()
                if self.async_add_entities is not None:
                    self.AddOrUpdateEntities()
            except (KeyError,PySnmpError):
                time.sleep(1)#sleep a second for these errors
            except:#other errors get logged...
                e = traceback.format_exc()
                LOGGER.error(e)
            if self.updateIntervalSeconds is None:
                self.updateIntervalSeconds=5

            time.sleep(max(1,self.updateIntervalSeconds))

    #region HA
    def setupEntities(self):
        self.update_stats()
        if self.async_add_entities is not None:
            self.AddOrUpdateEntities()

    
    def _AddOrUpdateEntity(self,id,entity_description,friendlyname,value):
        if id in self.meterSensors:
            sensor=self.meterSensors[id]
            sensor.set_state(value)
        else:
            sensor=SnmpStatisticsSensor(id,entity_description,friendlyname)
            sensor._state=value
            self.async_add_entities([sensor])
            #time.sleep(.5)#sleep a moment and wait for async add
            self.meterSensors[id]=sensor
        
    def AddOrUpdateEntities(self):
        allSensorsPrefix="sensor."+DOMAIN+"_"+self.target_ip.replace('.','_')+"_"
        for k in self.current_if_data:
            cur_if_data=self.current_if_data[k]
            if_name=cur_if_data['name2']
            if_alias=cur_if_data['alias']
            if not self.iface_list or if_name in self.iface_list:

                if_rx_mbit=cur_if_data['rx_speed_octets']*8/1000/1000
                if_tx_mbit=cur_if_data['tx_speed_octets']*8/1000/1000
                if_rx_mbyte=cur_if_data['rx_speed_octets']/1000/1000
                if_tx_mbyte=cur_if_data['tx_speed_octets']/1000/1000

                if_rx_total_mbyte=round(cur_if_data['rx_octets']/1024/1024,2)
                if_tx_total_mbyte=round(cur_if_data['tx_octets']/1024/1024,2)

                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_out_mbit',SENSOR_TYPES["throughput_network_out_mbit"],self.target_ip.replace('.','_')+" "+if_name+" BW Out (mbit)",round(if_tx_mbit,2))
                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_in_mbit',SENSOR_TYPES["throughput_network_in_mbit"],self.target_ip.replace('.','_')+" "+if_name+" BW In (mbit)",round(if_rx_mbit,2))

                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_out_mbyte',SENSOR_TYPES["throughput_network_out_mbyte"],self.target_ip.replace('.','_')+" "+if_name+" BW Out (mbyte)",round(if_tx_mbyte,2))
                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_curbw_in_mbyte',SENSOR_TYPES["throughput_network_out_mbyte"],self.target_ip.replace('.','_')+" "+if_name+" BW In (mbyte)",round(if_rx_mbyte,2))

                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_total_out_mbyte',SENSOR_TYPES["throughput_total_network_out"],self.target_ip.replace('.','_')+" "+if_name+" Total Out (MBytes)",if_tx_total_mbyte)
                self._AddOrUpdateEntity(allSensorsPrefix+"netif_"+if_name+'_total_in_mbyte',SENSOR_TYPES["throughput_total_network_in"],self.target_ip.replace('.','_')+" "+if_name+" Total In (MBytes)",if_rx_total_mbyte)

        self._AddOrUpdateEntity(allSensorsPrefix+"cpu_load_1",SENSOR_TYPES["load_1m"],self.target_ip.replace('.','_')+" CPU Avg 1min",self.cpuload1*100)
        self._AddOrUpdateEntity(allSensorsPrefix+"cpu_load_5",SENSOR_TYPES["load_5m"],self.target_ip.replace('.','_')+" CPU Avg 5min",self.cpuload2*100)
        self._AddOrUpdateEntity(allSensorsPrefix+"cpu_load_15",SENSOR_TYPES["load_15m"],self.target_ip.replace('.','_')+" CPU Avg 15min",self.cpuload3*100)
        self._AddOrUpdateEntity(allSensorsPrefix+"uptime",SENSOR_TYPES["uptime"],self.target_ip.replace('.','_')+" Uptime",self.uptime)
        self._AddOrUpdateEntity(allSensorsPrefix+"memory_used",SENSOR_TYPES["memory"],self.target_ip.replace('.','_')+" Memory Used",self.memRealUsed)
        self._AddOrUpdateEntity(allSensorsPrefix+"memory_used_percent",SENSOR_TYPES["memory_percent"],self.target_ip.replace('.','_')+" Memory Used (%)",self.memRealPercent)
        self._AddOrUpdateEntity(allSensorsPrefix+"memory_free",SENSOR_TYPES["memory"],self.target_ip.replace('.','_')+" Memory Free",self.memFree)
        self._AddOrUpdateEntity(allSensorsPrefix+"memory_buffered",SENSOR_TYPES["memory"],self.target_ip.replace('.','_')+" Memory Buffered",self.memBuffers)
        self._AddOrUpdateEntity(allSensorsPrefix+"memory_cached",SENSOR_TYPES["memory"],self.target_ip.replace('.','_')+" Memory Cached",self.memCached)
        self._AddOrUpdateEntity(allSensorsPrefix+"total_tcp_established_conn",SENSOR_TYPES["total_tcp"],self.target_ip.replace('.','_')+" Total TCP Established",self.totalTcpEstablished)
