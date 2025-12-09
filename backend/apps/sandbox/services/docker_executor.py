"""
Docker-based code execution engine.
"""
import docker
import logging
import time
from typing import Dict, Any, Optional, Tuple
from django.conf import settings

logger = logging.getLogger(__name__)


class DockerExecutor:
    """
    Handles execution of Ansible code in isolated Docker containers.
    
    Provides methods to:
    - Create isolated sandbox containers
    - Execute Ansible playbooks
    - Manage container lifecycle
    - Enforce resource limits
    """
    
    def __init__(self):
        """Initialize Docker client."""
        try:
            self.client = docker.from_env()
            logger.info("Docker client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise
    
    def create_sandbox(self, user_id: int, session_name: str) -> Tuple[str, str]:
        """
        Create an isolated sandbox container.
        
        Args:
            user_id: User ID for container naming
            session_name: Unique session identifier
        
        Returns:
            Tuple of (container_id, container_name)
        """
        container_name = f"djarvis_sandbox_{user_id}_{session_name}"
        
        try:
            # Create managed nodes network
            network_name = f"djarvis_net_{user_id}_{session_name}"
            network = self.client.networks.create(
                network_name,
                driver="bridge",
                labels={"app": "djarvis", "user_id": str(user_id)}
            )
            
            # Create control node (Ansible controller)
            control_node = self.client.containers.run(
                image="ansible/ansible:latest",
                name=container_name,
                detach=True,
                remove=False,
                network=network_name,
                mem_limit=settings.SANDBOX_MEMORY_LIMIT,
                cpu_quota=int(settings.SANDBOX_CPU_LIMIT * 100000),
                cpu_period=100000,
                command="sleep infinity",  # Keep container running
                labels={
                    "app": "djarvis",
                    "user_id": str(user_id),
                    "type": "control_node"
                },
                working_dir="/ansible",
            )
            
            # Create managed nodes (target hosts)
            managed_nodes = []
            for i in range(2):  # 2 managed nodes
                node = self.client.containers.run(
                    image="ubuntu:22.04",
                    name=f"{container_name}_node{i+1}",
                    detach=True,
                    remove=False,
                    network=network_name,
                    mem_limit="256m",
                    command="sleep infinity",
                    labels={
                        "app": "djarvis",
                        "user_id": str(user_id),
                        "type": "managed_node",
                        "parent": container_name
                    },
                )
                managed_nodes.append(node)
            
            # Wait for containers to start
            time.sleep(2)
            
            # Setup SSH and Python on managed nodes
            for i, node in enumerate(managed_nodes):
                setup_commands = [
                    "apt-get update",
                    "apt-get install -y python3 python3-pip openssh-server sudo",
                    "service ssh start",
                    "useradd -m -s /bin/bash ansible",
                    "echo 'ansible:ansible' | chpasswd",
                    "echo 'ansible ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers"
                ]
                for cmd in setup_commands:
                    node.exec_run(cmd)
            
            # Create inventory file on control node
            inventory_content = "[managed_nodes]\n"
            for i in range(len(managed_nodes)):
                inventory_content += f"{container_name}_node{i+1} ansible_connection=ssh ansible_user=ansible ansible_password=ansible\n"
            
            control_node.exec_run(
                f"sh -c 'echo \"{inventory_content}\" > /ansible/inventory.ini'"
            )
            
            logger.info(f"Created sandbox: {container_name} with {len(managed_nodes)} managed nodes")
            return control_node.id, container_name
            
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise
    
    def execute_playbook(
        self,
        container_name: str,
        playbook_content: str,
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute Ansible playbook in container.
        
        Args:
            container_name: Name of the container
            playbook_content: YAML playbook content
            timeout: Execution timeout in seconds
        
        Returns:
            Dictionary with execution results
        """
        try:
            container = self.client.containers.get(container_name)
            
            # Write playbook to container
            playbook_path = "/ansible/playbook.yml"
            exec_result = container.exec_run(
                f"sh -c 'echo \"{playbook_content}\" > {playbook_path}'"
            )
            
            if exec_result.exit_code != 0:
                return {
                    "success": False,
                    "error": "Failed to write playbook to container",
                    "output": exec_result.output.decode('utf-8')
                }
            
            # Execute playbook
            start_time = time.time()
            exec_result = container.exec_run(
                f"ansible-playbook -i /ansible/inventory.ini {playbook_path} -v",
                demux=True,
                stream=False,
            )
            execution_time = time.time() - start_time
            
            stdout = exec_result.output[0].decode('utf-8') if exec_result.output[0] else ""
            stderr = exec_result.output[1].decode('utf-8') if exec_result.output[1] else ""
            
            return {
                "success": exec_result.exit_code == 0,
                "exit_code": exec_result.exit_code,
                "stdout": stdout,
                "stderr": stderr,
                "execution_time": execution_time,
            }
            
        except docker.errors.NotFound:
            logger.error(f"Container not found: {container_name}")
            return {
                "success": False,
                "error": "Container not found",
                "output": ""
            }
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": ""
            }
    
    def stop_container(self, container_name: str) -> bool:
        """Stop and remove container."""
        try:
            container = self.client.containers.get(container_name)
            
            # Stop and remove managed nodes
            for i in range(2):
                try:
                    node = self.client.containers.get(f"{container_name}_node{i+1}")
                    node.stop(timeout=5)
                    node.remove()
                except:
                    pass
            
            # Stop and remove control node
            container.stop(timeout=5)
            container.remove()
            
            # Remove network
            try:
                networks = self.client.networks.list(
                    filters={"label": f"parent={container_name}"}
                )
                for network in networks:
                    network.remove()
            except:
                pass
            
            logger.info(f"Stopped and removed container: {container_name}")
            return True
            
        except docker.errors.NotFound:
            logger.warning(f"Container not found: {container_name}")
            return False
        except Exception as e:
            logger.error(f"Failed to stop container: {e}")
            return False
    
    def cleanup_expired_containers(self) -> int:
        """Remove all expired Djarvis containers."""
        try:
            containers = self.client.containers.list(
                all=True,
                filters={"label": "app=djarvis"}
            )
            
            removed_count = 0
            for container in containers:
                try:
                    container.stop(timeout=5)
                    container.remove()
                    removed_count += 1
                except:
                    pass
            
            logger.info(f"Cleaned up {removed_count} expired containers")
            return removed_count
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
            return 0
