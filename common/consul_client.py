import consul
import random
from itertools import cycle
from typing import List, Dict, Any
from fastapi import HTTPException

from common.config_loader import GLOBAL_CONFIG
from common.utils import get_public_ip
from common.logger import logger

consul_config = GLOBAL_CONFIG['consul'] if 'consul' in GLOBAL_CONFIG else None
# global 关键字并不用于模块级别的变量声明
consul_client = None


class ConsulServiceDiscovery:
    def __init__(self, servers: List[Dict[str, Any]]):
        self.servers = servers
        self.service_iterators = {}
        self.service_id = ''
        self.clients = []

    def get_consul_client(self) -> consul.Consul:
        if len(self.clients) == 0:
            return None
        random_index = random.randint(0, len(self.clients) - 1)
        return self.clients[random_index]

    def init_consul_clients(self):
        for server in self.servers:
            try:
                client = consul.Consul(host=server['host'], port=server['port'])
                # 尝试进行一次简单的查询以验证连接
                client.agent.self()
                self.clients.append(client)
            except consul.ConsulException as e:
                logger.error(f"Failed to connect to Consul server {server['host']}:{server['port']}, error: {e}")
                continue
        if len(self.clients) == 0:
            raise HTTPException(status_code=503, detail="All Consul servers are unavailable")

    def discover_service(self, service_name: str, tag: str = None, strategy: str = 'random') -> str:
        consul_client = self.get_consul_client()
        # 从 Consul 中发现服务，仅列出正常状态服务
        # 如果你需要过滤多个标签，你需要进行多次请求并取services交集。
        index, services = consul_client.health.service(service_name, tag=tag, passing=True)
        if not services:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")

        if strategy == 'random':
            return self._random_choice(services)
        elif strategy == 'round_robin':
            return self._round_robin_choice(service_name, services)
        elif strategy == 'weighted':
            return self._weighted_choice(services)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    def _random_choice(self, services: List[Dict[str, Any]]) -> str:
        service = random.choice(services)
        address = service['Service']['Address']
        # address = service['ServiceAddress']
        port = service['Service']['Port']
        # port = service['ServicePort']
        return f"http://{address}:{port}"

    def _round_robin_choice(self, service_name: str, services: List[Dict[str, Any]]) -> str:
        if service_name not in self.service_iterators or len(self.service_iterators[service_name]) != len(services):
            self.service_iterators[service_name] = cycle(services)
        service = next(self.service_iterators[service_name])
        address = service['ServiceAddress']
        port = service['ServicePort']
        return f"http://{address}:{port}"

    def _weighted_choice(self, services: List[Dict[str, Any]]) -> str:
        weighted_services = [(service, service.get('Weight', 1)) for service in services]
        total = sum(weight for service, weight in weighted_services)
        r = random.uniform(0, total)
        upto = 0
        for service, weight in weighted_services:
            if upto + weight >= r:
                address = service['ServiceAddress']
                port = service['ServicePort']
                return f"http://{address}:{port}"
            upto += weight
        assert False, "Shouldn't get here"

    def register_service(self, name: str, service_id: str, address: str, port: int, tags: List[str] = None,
                         check: Dict[str, Any] = None):
        # 注册前先取消注册当前服务ID
        self.deregister_service()
        consul_client = self.get_consul_client()
        try:
            consul_client.agent.service.register(
                name=name,
                service_id=service_id,
                address=address,
                port=port,
                tags=tags,
                check=check
            )
            logger.info(f"Service {name} registered successfully with ID {service_id}")
        except consul.ConsulException as e:
            raise HTTPException(status_code=500, detail=f"Failed to register service {name}, error: {e}")

    def deregister_service(self):
        for consul_client in self.clients:
            try:
                consul_client.agent.service.deregister(self.service_id)
                logger.info(f"Service {self.service_id} deregistered successfully from {consul_client.http.base_uri}")
            except consul.ConsulException as e:
                raise HTTPException(status_code=500,
                                    detail=f"Failed to deregister service {self.service_id}, error: {e}")


def init_service_register_and_discovery():
    discovery_client = ConsulServiceDiscovery(consul_config['targets'])
    discovery_client.init_consul_clients()

    # 注册服务
    service_config = consul_config['service']
    service_name = service_config['name']
    service_port = GLOBAL_CONFIG['port']
    service_address = get_public_ip()
    service_tags = [service_name]
    if 'tags' in service_config:
        service_tags = service_config['tags']
    service_id = f'{service_name}_{service_address}'
    discovery_client.service_id = service_id
    if 'id' in service_config:
        service_id = service_config['id']
    check_interval = 10
    if 'check_interval' in service_config:
        check_interval = service_config['check_interval']
    service_check = {
        "http": f"http://{service_address}:{service_port}/health",
        "interval": f"{check_interval}s",
        # "deregister_critical_service_after": "2m"  # 自动剔除连续健康检查失败1m的节点
    }
    try:
        discovery_client.register_service(
            name=service_name,
            service_id=service_id,
            address=service_address,
            port=service_port,
            tags=service_tags,
            check=service_check
        )
        logger.info(f"Service {service_name} registered successfully.")
    except HTTPException as e:
        logger.error(f"Failed to register service: {e.detail}")


def service_register_and_discovery_enabled():
    return GLOBAL_CONFIG['consul']['enabled'] if 'consul' in GLOBAL_CONFIG else False


def deregister_service():
    consul_client.deregister_service()
    logger.info('deregister service success')
