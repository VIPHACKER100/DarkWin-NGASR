"""DARKWIN Mesh Node Manager

Handles discovery and health monitoring of distributed scanning nodes
using Redis as a central registry.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

"""
DARKWIN Mesh Node Manager

Handles discovery and health monitoring of distributed scanning nodes
using Redis as a central registry with TTL-based heartbeats.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: MIT
"""

import time
import json
import uuid
import platform
import socket
from typing import List, Dict, Any, Optional

from redis import Redis
from redis.exceptions import RedisError
from datetime import datetime, timezone

from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("MeshManager")
config = get_config()

class MeshManager:
    """Manages distributed scanning nodes via a Redis registry."""

    def __init__(self) -> None:
        self.redis: Optional[Redis] = None
        self.node_id: str = str(uuid.uuid4())[:8]
        self.hostname: str = socket.gethostname()
        try:
            self.redis = Redis.from_url(config.redis.url)
            logger.info(f"Mesh Manager initialized (Node ID: {self.node_id})")
        except RedisError as e:
            logger.error(f"Failed to connect to Redis for Mesh management: {e}")

    def register_node(self) -> None:
        """Register this node in the global registry with a 60s TTL."""
        if not self.redis:
            return

        node_info: Dict[str, Any] = {
            "id": self.node_id,
            "hostname": self.hostname,
            "os": platform.system(),
            "last_seen": datetime.now(timezone.utc).isoformat(),
            "status": "online"
        }

        try:
            self.redis.setex(
                f"mesh:node:{self.node_id}",
                60,
                json.dumps(node_info)
            )
            logger.debug(f"Node {self.node_id} registered")
        except RedisError as e:
            logger.error(f"Failed to register node: {e}")

    def list_nodes(self) -> List[Dict[str, Any]]:
        """Retrieve all active nodes in the mesh."""
        if not self.redis:
            return []

        nodes: List[Dict[str, Any]] = []
        try:
            keys = self.redis.keys("mesh:node:*")
            for key in keys:
                data = self.redis.get(key)
                if data:
                    nodes.append(json.loads(data))
        except RedisError as e:
            logger.error(f"Failed to list nodes: {e}")

        return nodes

    def heartbeat_loop(self) -> None:
        """Continuous heartbeat to keep node registration alive."""
        logger.info(f"Starting heartbeat for node {self.node_id}")
        try:
            while True:
                self.register_node()
                time.sleep(30)
        except KeyboardInterrupt:
            self.unregister_node()

    def unregister_node(self) -> None:
        """Remove node from registry on shutdown."""
        if self.redis:
            self.redis.delete(f"mesh:node:{self.node_id}")
            logger.info(f"Node {self.node_id} unregistered")

if __name__ == "__main__":
    manager = MeshManager()
    manager.heartbeat_loop()
