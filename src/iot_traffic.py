import os
import socket
import time
import random
import threading
import json
import logging
from datetime import datetime
import requests
import dns.resolver
from typing import Dict, List, Callable, Any
import struct
from dataclasses import dataclass, field

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('iot_simulator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class DeviceProfile:
    """Dataclass to define an IoT device's characteristics."""
    name: str
    device_type: str
    mac: str
    source_ip: str
    protocols: List[str]
    endpoints: List[str]
    user_agents: List[str]
    interval: int
    ports: Dict[str, int] = field(default_factory=dict)

"""
IoT Devices Traffic Simulator - v4 (Lock-Free Metrics)
Simulates IoT traffic and aggregates statistics at the end of the simulation.
"""
class IoTDeviceSimulator:
    """Simulates different types of IoT devices using a data-driven approach."""
    
    def __init__(self, target_server: str, ip_prefix: str = "192.168.1."):
        self.target_server = target_server
        self.ip_prefix = ip_prefix
        self.running = False
        self.devices: List[DeviceProfile] = []
        
        self.simulation_contexts: List[Dict[str, Any]] = []
        self.start_time = None

        self.protocol_simulators: Dict[str, Callable] = {
            'HTTP': self.simulate_http_traffic,
            'RTSP': self.simulate_rtsp_traffic,
            'CoAP': self.simulate_coap_traffic,
            'DNS': self.simulate_dns_queries,
            'NTP': self.simulate_ntp_traffic,
        }

    def initialize_devices(self):
        """Initializes all IoT device profiles."""
        self.devices = [
            DeviceProfile(name='Samsung_SmartTV_Living', device_type='SmartTV', mac='00:1A:2B:3C:4D:5E', source_ip=f'{self.ip_prefix}20', protocols=['HTTP', 'DNS', 'NTP'], endpoints=['/api/v1/tv/status', '/streaming/manifest.m3u8'], user_agents=['Mozilla/5.0 (SMART-TV; Linux; Tizen 5.5) TV Safari/537.36'], interval=120, ports={'HTTP': 80}),
            DeviceProfile(name='Hikvision_Camera_01', device_type='SecurityCamera', mac='00:2A:3B:4C:5D:6F', source_ip=f'{self.ip_prefix}21', protocols=['HTTP', 'RTSP', 'DNS', 'NTP'], endpoints=['/ISAPI/System/deviceInfo', '/ISAPI/Streaming/channels/101/picture'], user_agents=['Hikvision-Webs'], interval=30, ports={'HTTP': 80, 'RTSP': 554}),
            DeviceProfile(name='Nest_Thermostat_01', device_type='Thermostat', mac='00:3A:4B:5C:6D:7E', source_ip=f'{self.ip_prefix}22', protocols=['HTTP', 'CoAP', 'DNS', 'NTP'], endpoints=['/api/climate/current', '/api/sensors/temperature'], user_agents=['Nest/1.0'], interval=180, ports={'HTTP': 80, 'CoAP': 5683}),
        ]
        logger.info(f"Initialized {len(self.devices)} IoT devices.")

    def _sleep(self, duration: float):
        """Cancellable sleep that respects the running flag."""
        start = time.time()
        while self.running and time.time() - start < duration:
            time.sleep(0.5)

    # MODIFIED: All simulate_* methods now accept a 'stats_counter' dictionary
    def simulate_http_traffic(self, device: DeviceProfile, stats_counter: Dict):
        while self.running:
            try:
                endpoint = random.choice(device.endpoints)
                url = f"http://{self.target_server}{endpoint}"
                requests.get(url, timeout=5)
                stats_counter['actions'] += 1
            except Exception as e:
                logger.debug(f"[{device.name}] HTTP error: {e}")
                stats_counter['errors'] += 1
            self._sleep(device.interval + random.uniform(-device.interval * 0.1, device.interval * 0.1))

    def simulate_rtsp_traffic(self, device: DeviceProfile, stats_counter: Dict):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(5); sock.bind((device.source_ip, 0))
                    sock.connect((self.target_server, device.ports.get('RTSP', 554)))
                    sock.send(f"OPTIONS rtsp://{self.target_server}/stream1 RTSP/1.0\r\nCSeq: 1\r\n\r\n".encode())
                stats_counter['actions'] += 1
            except Exception as e:
                logger.debug(f"[{device.name}] RTSP error: {e}")
                stats_counter['errors'] += 1
            self._sleep(random.uniform(300, 900))

    def simulate_coap_traffic(self, device: DeviceProfile, stats_counter: Dict):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.bind((device.source_ip, 0))
                    header = struct.pack('!BBH', 0b01000100, 1, random.randint(1, 65535)); token = os.urandom(4)
                    sock.sendto(header + token, (self.target_server, device.ports.get('CoAP', 5683)))
                stats_counter['actions'] += 1
            except Exception as e:
                logger.debug(f"[{device.name}] CoAP error: {e}")
                stats_counter['errors'] += 1
            self._sleep(random.uniform(60, 300))
    
    def simulate_dns_queries(self, device: DeviceProfile, stats_counter: Dict):
        resolver = dns.resolver.Resolver(); resolver.nameservers = ['192.168.1.1']
        domains = {'SmartTV': ['samsungads.com', 'netflix.com'], 'SecurityCamera': ['hik-connect.com']}.get(device.device_type, ['google.com'])
        while self.running:
            try:
                resolver.resolve(random.choice(domains), 'A')
                stats_counter['actions'] += 1
            except Exception as e:
                logger.debug(f"[{device.name}] DNS error: {e}")
                stats_counter['errors'] += 1
            self._sleep(random.uniform(120, 600))
    
    def simulate_ntp_traffic(self, device: DeviceProfile, stats_counter: Dict):
        ntp_server = 'pool.ntp.org'
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                    sock.settimeout(5); sock.bind((device.source_ip, 0))
                    sock.sendto(b'\x1b' + 47 * b'\0', (ntp_server, 123)); sock.recvfrom(1024)
                stats_counter['actions'] += 1
            except Exception as e:
                logger.debug(f"[{device.name}] NTP error: {e}")
                stats_counter['errors'] += 1
            self._sleep(random.uniform(3600, 7200))

    def simulate_device_discovery(self, stats_counter: Dict):
        while self.running:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as ssdp_sock:
                    ssdp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    ssdp_msg = ('M-SEARCH * HTTP/1.1\r\n' 'HOST: 239.255.255.250:1900\r\n' 'MAN: "ssdp:discover"\r\n' 'ST: upnp:rootdevice\r\n' 'MX: 3\r\n\r\n').encode()
                    ssdp_sock.sendto(ssdp_msg, ('239.255.255.250', 1900))
                stats_counter['actions'] += 1
            except Exception as e:
                logger.debug(f"Device discovery error: {e}")
                stats_counter['errors'] += 1
            self._sleep(random.uniform(1800, 3600))
    
    def start_simulation(self):
        if not self.running:
            logger.info("Starting IoT device simulation...")
            self.running = True
            self.start_time = time.time()
            self.initialize_devices()
            threads = []
            
            # MODIFIED: Create a context for each thread to store its own stats
            for device in self.devices:
                for protocol in device.protocols:
                    if protocol in self.protocol_simulators:
                        stats_counter = {'actions': 0, 'errors': 0}
                        simulator_func = self.protocol_simulators[protocol]
                        thread = threading.Thread(target=simulator_func, args=(device, stats_counter), name=f"{device.name}-{protocol}", daemon=True)
                        threads.append(thread)
                        self.simulation_contexts.append({'device': device, 'protocol': protocol, 'stats': stats_counter})
            
            # Context for the discovery thread
            discovery_stats = {'actions': 0, 'errors': 0}
            discovery_thread = threading.Thread(target=self.simulate_device_discovery, args=(discovery_stats,), name="Discovery", daemon=True)
            threads.append(discovery_thread)
            self.simulation_contexts.append({'device': None, 'protocol': 'Discovery', 'stats': discovery_stats})

            for t in threads:
                t.start()
            
            logger.info(f"Started {len(threads)} threads for IoT devices.")
            return threads
        return []
    
    def stop_simulation(self):
        if self.running:
            logger.info("Stopping IoT device simulation...")
            self.running = False

    def calculate_and_print_metrics(self):
        """Aggregates stats from all contexts and prints a final summary."""
        if not self.start_time:
            logger.info("Simulation never started, no metrics to display.")
            return

        duration = time.time() - self.start_time
        
        # Aggregate stats
        total_actions = 0
        total_errors = 0
        by_protocol = {proto: 0 for proto in self.protocol_simulators.keys()}
        by_protocol['Discovery'] = 0
        by_device = {dev.name: {'actions': 0, 'errors': 0} for dev in self.devices}

        for context in self.simulation_contexts:
            actions = context['stats']['actions']
            errors = context['stats']['errors']
            total_actions += actions
            total_errors += errors
            by_protocol[context['protocol']] += actions
            if context['device']: # Discovery device is None
                by_device[context['device'].name]['actions'] += actions
                by_device[context['device'].name]['errors'] += errors
        
        print("\n" + "="*50)
        print(" F I N A L   S I M U L A T I O N   M E T R I C S")
        print("="*50)
        print(f"\n🕒 Total Execution Time: {duration:.2f} seconds")
        print(f"📈 Total Actions Sent:   {total_actions}")
        print(f"❌ Total Errors:         {total_errors}")
        print("\n--- Summary by Protocol ---")
        for protocol, count in sorted(by_protocol.items()):
            if count > 0:
                print(f"  - {protocol:<10}: {count} actions")
        print("\n--- Summary by Device ---")
        for device_name, device_stats in sorted(by_device.items()):
            if device_stats['actions'] > 0 or device_stats['errors'] > 0:
                print(f"  📱 {device_name:<25} - Actions: {device_stats['actions']}, Errors: {device_stats['errors']}")
        print("\n" + "="*50)

def main():
    target_server = "192.168.1.10"
    
    if os.geteuid() != 0:
        logger.error("This script requires root privileges. Please run with sudo.")
        return

    simulator = IoTDeviceSimulator(target_server=target_server, ip_prefix="192.168.1.")
    threads = []
    
    try:
        threads = simulator.start_simulation()
        for thread in threads:
            thread.join()
    except KeyboardInterrupt:
        logger.info("Interrupt received, stopping IoT simulator...")
    finally:
        simulator.stop_simulation()
        simulator.calculate_and_print_metrics()
        logger.info("IoT simulator finished.")

if __name__ == "__main__":
    print("=== IoT Device Simulator v4 (Lock-Free Metrics) ===")
    print("ATTENTION: This script must be run with sudo to function correctly.")
    print("Press Ctrl+C to stop and display metrics.")
    main()
