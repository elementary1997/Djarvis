"""
Ansible playbook validation service.
"""
import yaml
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class AnsibleValidator:
    """
    Validates Ansible playbooks for syntax and security.
    """
    
    # Dangerous modules that should be restricted
    RESTRICTED_MODULES = [
        'shell',
        'command',
        'raw',
        'script',
    ]
    
    # Dangerous commands/patterns
    DANGEROUS_PATTERNS = [
        'rm -rf',
        'dd if=',
        'mkfs',
        ':(){ :|:& };:',  # Fork bomb
        '/dev/sda',
        'shutdown',
        'reboot',
        'halt',
    ]
    
    @staticmethod
    def validate_yaml(playbook_content: str) -> Dict[str, Any]:
        """
        Validate YAML syntax.
        
        Args:
            playbook_content: YAML content to validate
        
        Returns:
            Dictionary with validation results
        """
        try:
            data = yaml.safe_load(playbook_content)
            
            if not isinstance(data, list):
                return {
                    "valid": False,
                    "error": "Playbook must be a list of plays",
                    "data": None
                }
            
            return {
                "valid": True,
                "error": None,
                "data": data
            }
            
        except yaml.YAMLError as e:
            return {
                "valid": False,
                "error": f"YAML syntax error: {str(e)}",
                "data": None
            }
    
    @classmethod
    def check_security(cls, playbook_content: str) -> Dict[str, Any]:
        """
        Check for potentially dangerous operations.
        
        Args:
            playbook_content: Playbook content to check
        
        Returns:
            Dictionary with security check results
        """
        warnings = []
        
        # Check for dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern in playbook_content:
                warnings.append(f"Dangerous pattern detected: {pattern}")
        
        # Parse and check modules
        try:
            data = yaml.safe_load(playbook_content)
            if isinstance(data, list):
                for play in data:
                    if 'tasks' in play:
                        for task in play['tasks']:
                            # Check for restricted modules
                            for module in cls.RESTRICTED_MODULES:
                                if module in task:
                                    warnings.append(
                                        f"Restricted module '{module}' used in task: {task.get('name', 'unnamed')}"
                                    )
        except:
            pass  # YAML validation is done separately
        
        return {
            "safe": len(warnings) == 0,
            "warnings": warnings
        }
    
    @classmethod
    def validate_playbook(cls, playbook_content: str) -> Dict[str, Any]:
        """
        Perform complete playbook validation.
        
        Args:
            playbook_content: Playbook to validate
        
        Returns:
            Combined validation results
        """
        # Validate YAML syntax
        yaml_result = cls.validate_yaml(playbook_content)
        if not yaml_result['valid']:
            return {
                "valid": False,
                "errors": [yaml_result['error']],
                "warnings": [],
                "safe": False
            }
        
        # Check security
        security_result = cls.check_security(playbook_content)
        
        return {
            "valid": True,
            "errors": [],
            "warnings": security_result['warnings'],
            "safe": security_result['safe'],
            "data": yaml_result['data']
        }
