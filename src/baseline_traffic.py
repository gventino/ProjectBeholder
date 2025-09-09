import asyncio
import aiohttp
import aiodns
import aioftp
import random
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
import requests
import socket
import signal

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('traffic_generator.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class UserProfile:
    """Defines a user profile with behavioral patterns"""
    name: str
    browsing_sites_per_hour: int
    download_files_per_day: int
    email_checks_per_hour: int
    ftp_sessions_per_day: int
    social_media_time_minutes: int
    streaming_hours_per_day: float
    work_hours: tuple  # (start, end)
    peak_activity_hours: List[int]
    preferred_sites: List[str]
    device_type: str

"""
Realistic Home Network Traffic Generator v4 - Safe Shutdown + English logs and comments
Simulates realistic home user patterns with HTTP/S, DNS, FTP, and graceful shutdown.
"""
class HomeUserSimulator:
    """Simulates realistic behavior of home users"""

    def __init__(self, config_file: str = "traffic_config.json"):
        self.config = self.load_config(config_file)
        self.session = None
        self.dns_resolver = None
        self.user_profiles = self.create_user_profiles()
        self.shutdown_event = asyncio.Event()
        self.stats = {
            'requests_made': 0,
            'bytes_downloaded': 0,
            'bytes_uploaded': 0,
            'errors': 0,
            'start_time': None
        }

    def load_config(self, config_file: str) -> Dict:
        """Loads configuration from a JSON file"""
        default_config = {
            "target_servers": {
                "web": "192.168.1.10",
                "db": "192.168.1.11",
                "ftp": "192.168.1.12"
            },
            "dns_server": "192.168.1.1", # Router/gateway IP
            "external_sites": [
                "https://httpbin.org",
                "https://example.com",
                "https://jsonplaceholder.typicode.com"
            ],
            "simulation_duration_hours": 24,
            "concurrent_users": 3,
            "log_level": "INFO"
        }
        try:
            with open(config_file, 'r') as f: config = json.load(f)
            logger.info(f"Configuration loaded from {config_file}")
            merged_config = default_config.copy(); merged_config.update(config)
            return merged_config
        except FileNotFoundError:
            logger.warning(f"File {config_file} not found, using and saving default configuration")
            with open(config_file, 'w') as f: json.dump(default_config, f, indent=4)
            return default_config

    def create_user_profiles(self) -> List[UserProfile]:
        """Creates realistic user profiles"""
        return [
            UserProfile(name="heavy_user", browsing_sites_per_hour=15, download_files_per_day=5, email_checks_per_hour=4, ftp_sessions_per_day=3, social_media_time_minutes=120, streaming_hours_per_day=4.0, work_hours=(9, 17), peak_activity_hours=[19, 20, 21], preferred_sites=["youtube", "facebook", "netflix", "reddit"], device_type="desktop"),
            UserProfile(name="casual_user", browsing_sites_per_hour=8, download_files_per_day=1, email_checks_per_hour=2, ftp_sessions_per_day=1, social_media_time_minutes=60, streaming_hours_per_day=2.0, work_hours=(9, 17), peak_activity_hours=[20, 21], preferred_sites=["news", "weather", "email"], device_type="mobile"),
            UserProfile(name="work_user", browsing_sites_per_hour=12, download_files_per_day=3, email_checks_per_hour=6, ftp_sessions_per_day=5, social_media_time_minutes=30, streaming_hours_per_day=1.0, work_hours=(8, 18), peak_activity_hours=[9, 10, 14, 15], preferred_sites=["github", "stackoverflow", "docs"], device_type="laptop")
        ]

    async def initialize_session(self):
        """Initializes HTTP session with a custom DNS resolver to generate real DNS traffic."""
        loop = asyncio.get_running_loop()
        self.dns_resolver = aiodns.DNSResolver(loop=loop, nameservers=[self.config['dns_server']])
        class CustomResolver(aiohttp.abc.AbstractResolver):
            def __init__(self, resolver): self._resolver = resolver
            async def resolve(self, host, port, family=socket.AF_INET):
                try:
                    addrs = await self._resolver.query(host, 'A')
                    return [{'hostname': host, 'host': addr.host, 'port': port, 'family': family, 'proto': 0, 'flags': 0} for addr in addrs]
                except aiodns.error.DNSError as e: logger.warning(f"DNS lookup for {host} failed: {e}"); raise
            async def close(self): pass
        connector = aiohttp.TCPConnector(resolver=CustomResolver(self.dns_resolver), limit_per_host=10)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        self.session = aiohttp.ClientSession(timeout=timeout, connector=connector, headers={'User-Agent': self.get_random_user_agent(), 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 'Accept-Language': 'en-US,en;q=0.5', 'Connection': 'keep-alive'})
    
    def get_random_user_agent(self) -> str:
        return random.choice(['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0', 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1'])

    async def make_http_request(self, url: str, method: str = 'GET', data: Optional[Dict] = None) -> Optional[Dict]:
        try:
            headers = {'User-Agent': self.get_random_user_agent()}
            if method.upper() == 'GET':
                async with self.session.get(url, headers=headers) as response:
                    content_length = response.headers.get('content-length', 0)
                    self.stats['bytes_downloaded'] += int(content_length)
                    return {'status': response.status, 'size': content_length}
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data, headers=headers) as response:
                    return {'status': response.status}
        except Exception: self.stats['errors'] += 1; return None
        finally: self.stats['requests_made'] += 1

    async def simulate_web_browsing(self, profile: UserProfile):
        logger.info(f"Starting web browsing simulation for {profile.name}")
        sites_base = self.config['external_sites'] + [f"http://{self.config['target_servers']['web']}"]
        # Loop now checks the shutdown event
        while not self.shutdown_event.is_set():
            site = random.choice(sites_base)
            await self.make_http_request(site)
            await asyncio.sleep(random.uniform(1, 3))
            for _ in range(random.randint(2, 5)):
                if self.shutdown_event.is_set(): break
                sub_path = self.generate_realistic_path(profile)
                await self.make_http_request(f"{site.strip('/')}/{sub_path}")
                await asyncio.sleep(random.uniform(10, 25))
            
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=random.uniform(20, 60))
                break 
            except asyncio.TimeoutError:
                pass 


    def select_site_by_keyword(self, sites: List[str], keyword: Optional[str]) -> str:
        if not keyword: return random.choice(sites)
        keyword_mapping = {
            'youtube': 'https://httpbin.org/json', 'facebook': 'https://httpbin.org/user-agent',
            'netflix': 'https://httpbin.org/stream/20', 'reddit': 'https://jsonplaceholder.typicode.com/posts',
            'news': 'https://httpbin.org/html', 'email': f"http://{self.config['target_servers']['web']}/webmail",
        }
        return keyword_mapping.get(keyword, random.choice(sites))

    def generate_realistic_path(self, profile: UserProfile) -> str:
        paths = ['search?q=tutorial', 'downloads', 'contact', 'about']
        return random.choice(paths)

    async def simulate_file_downloads(self, profile: UserProfile):
        download_urls = ['https://httpbin.org/bytes/102400', 'https://httpbin.org/stream-bytes/1048576']
        files_today, last_download = 0, datetime.now().date()
        while not self.shutdown_event.is_set():
            if datetime.now().date() != last_download:
                files_today, last_download = 0, datetime.now().date()
            if files_today < profile.download_files_per_day:
                url = random.choice(download_urls)
                logger.info(f"{profile.name} is downloading a file from {url}")
                if await self.make_http_request(url): files_today += 1
                try:
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=random.uniform(300, 1800))
                    break
                except asyncio.TimeoutError:
                    pass
            else:
                try:
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=3600)
                    break
                except asyncio.TimeoutError:
                    pass

    async def simulate_ftp_activity(self, profile: UserProfile):
        ftp_server = self.config['target_servers']['ftp']
        ftp_user, ftp_pass = "admin", "admin"
        sessions_today, last_session_date = 0, datetime.now().date()
        while not self.shutdown_event.is_set():
            if datetime.now().date() != last_session_date:
                sessions_today, last_session_date = 0, datetime.now().date()
            if sessions_today < profile.ftp_sessions_per_day:
                try:
                    async with aioftp.Client.context(ftp_server, user=ftp_user, password=ftp_pass, timeout=20) as client:
                        content = os.urandom(random.randint(1024, 20480))
                        async with client.upload_stream("upload.tmp") as stream: await stream.write(content)
                        self.stats['bytes_uploaded'] += len(content)
                        sessions_today += 1
                except Exception as e:
                    logger.error(f"FTP error for {profile.name}: {e}"); self.stats['errors'] += 1
                try:
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=random.uniform(1800, 7200))
                    break
                except asyncio.TimeoutError:
                    pass
            else:
                try:
                    await asyncio.wait_for(self.shutdown_event.wait(), timeout=3600)
                    break
                except asyncio.TimeoutError:
                    pass

    async def simulate_email_activity(self, profile: UserProfile):
        webmail_server = self.config['target_servers']['web']
        while not self.shutdown_event.is_set():
            await self.make_http_request(f"http://{webmail_server}/webmail/login", method='POST', data={'user': profile.name})
            check_interval = 3600 / profile.email_checks_per_hour
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=random.uniform(check_interval * 0.5, check_interval * 1.5))
                break
            except asyncio.TimeoutError:
                pass

    async def simulate_streaming_activity(self, profile: UserProfile):
        streaming_server = self.config['target_servers']['web']
        while not self.shutdown_event.is_set():
            if datetime.now().hour in [19, 20, 21, 22]:
                stream_end = time.time() + (random.uniform(0.5, 2.0) * 3600)
                while time.time() < stream_end and not self.shutdown_event.is_set():
                    await self.make_http_request(f"http://{streaming_server}/video/chunk.ts")
                    try:
                        await asyncio.wait_for(self.shutdown_event.wait(), timeout=2)
                        break
                    except asyncio.TimeoutError:
                        pass
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), timeout=1800)
                break
            except asyncio.TimeoutError:
                pass
    
    def simulate_iot_devices(self):
        def iot_worker():
            while not self.shutdown_event.is_set():
                server = self.config['target_servers']['web']
                try: requests.get(f"http://{server}/api/status", timeout=5)
                except Exception as e: logger.debug(f"IoT error: {e}")
                self.shutdown_event.wait(timeout=120 + random.uniform(-10, 10))

        executor = ThreadPoolExecutor(max_workers=1)
        executor.submit(iot_worker)


    async def monitor_and_log(self):
        while not self.shutdown_event.is_set():
            try:
                await asyncio.wait_for(self.shutdown_event.wait(), 300)
            except asyncio.TimeoutError:
                uptime = datetime.now() - self.stats['start_time']
                logger.info(f"Stats - Uptime: {uptime}, Reqs: {self.stats['requests_made']}, "
                           f"DL: {self.stats['bytes_downloaded']/(1024*1024):.2f}MB, "
                           f"UL: {self.stats['bytes_uploaded']/1024:.2f}KB, Errors: {self.stats['errors']}")

    def print_final_stats(self):
        if not self.stats['start_time']: return
        duration = datetime.now() - self.stats['start_time']
        logger.info("=== FINAL STATISTICS ===")
        logger.info(f"Total duration: {duration}")
        logger.info(f"Total requests: {self.stats['requests_made']}")
        logger.info(f"Total data downloaded: {self.stats['bytes_downloaded']/(1024*1024):.2f} MB")
        logger.info(f"Total data uploaded: {self.stats['bytes_uploaded']/(1024*1024):.2f} MB")
        logger.info(f"Error rate: {self.stats['errors']/max(self.stats['requests_made'],1)*100:.1f}%")
    
    async def run(self):
        """Creates tasks and waits for the shutdown signal."""
        self.stats['start_time'] = datetime.now()
        await self.initialize_session()
        self.simulate_iot_devices()

        tasks = []
        for profile in self.user_profiles:
            tasks.extend([
                asyncio.create_task(self.simulate_web_browsing(profile)),
                asyncio.create_task(self.simulate_file_downloads(profile)),
                asyncio.create_task(self.simulate_email_activity(profile)),
                asyncio.create_task(self.simulate_streaming_activity(profile)),
                asyncio.create_task(self.simulate_ftp_activity(profile))
            ])
        tasks.append(asyncio.create_task(self.monitor_and_log()))

        logger.info(f"Simulation started with {len(tasks)} tasks. Press Ctrl+C to stop.")
        
        await self.shutdown_event.wait()

        logger.info("Shutdown signal received. Terminating tasks...")
        
        for task in tasks:
            task.cancel()
        
        await asyncio.gather(*tasks, return_exceptions=True)

        if self.session and not self.session.closed:
            await self.session.close()
        
        self.print_final_stats()

async def main():
    """Configures and runs the simulator."""
    simulator = HomeUserSimulator()
    
    loop = asyncio.get_running_loop()
    
    def signal_handler():
        logger.warning("Interrupt signal received!")
        simulator.shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)

    try:
        await simulator.run()
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)

if __name__ == "__main__":
    print("=== Traffic Generator v4 (Safe Shutdown) ===")
    print("Press Ctrl+C to stop the simulation safely.")
    
    asyncio.run(main())
