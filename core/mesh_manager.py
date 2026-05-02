"""DARKWIN Mesh Node Manager

Handles discovery and health monitoring of distributed scanning nodes
using Redis as a central registry.

Author: ARYAN AHIRWAR (VIPHACKER.100)
License: See LICENSE file
"""

import time
import json
import uuid
import platform
import socket
import redis
from datetime import datetime
from typing import List, Dict, Any

from core.config_manager import get_config
from core.logging_system import get_logger

logger = get_logger("MeshManager")
config = get_config()

class MeshManager:
    """Manages distributed scanning nodes."""
    
    def __init__(self):
        try:
            self.redis = redis.from_url(config.redis.url)
            self.node_id = str(uuid.uuid4())[:8]
            self.hostname = socket.gethostname()
            logger.info(f"Mesh Manager initialized (Node ID: {self.node_id})")
        except Exception as e:
            logger.error(f"Failed to connect to Redis for Mesh management: {e}")
            self.redis = None

    def register_node(self):
        """Register this node in the global registry."""
        if not self.redis: return
        
        node_info = {
            "id": self.node_id,
            "hostname": self.hostname,
            "os": platform.system(),
            "last_seen": datetime.utcnow().isoformat(),
            "status": "online"
        }
        
        try:
            # Set with 60s TTL, refreshed by heartbeat
            self.redis.setex(
                f"mesh:node:{self.node_id}",
                60,
                json.dumps(node_info)
            )
            logger.debug(f"Node {self.node_id} registered")
        except Exception as e:
            logger.error(f"Failed to register node: {e}")

    def list_nodes(self) -> List[Dict[str, Any]]:
        """Retrieve all active nodes in the mesh."""
        if not self.redis: return []
        
        nodes = []
        try:
            keys = self.redis.keys("mesh:node:*")
            for key in keys:
                data = self.redis.get(key)
                if data:
                    nodes.append(json.loads(data))
        except Exception as e:
            logger.error(f"Failed to list nodes: {e}")
        
        return nodes

    def heartbeat_loop(self):
        """Continuous heartbeat to keep node registration alive."""
        logger.info(f"Starting heartbeat for node {self.node_id}")
        try:
            while True:
                self.register_node()
                time.sleep(30)
        except KeyboardInterrupt:
            self.unregister_node()

    def unregister_node(self):
        """Remove node from registry on shutdown."""
        if self.redis:
            self.redis.delete(f"mesh:node:{self.node_id}")
            logger.info(f"Node {self.node_id} unregistered")

if __name__ == "__main__":
    manager = MeshManager()
    manager.heartbeat_loop()
