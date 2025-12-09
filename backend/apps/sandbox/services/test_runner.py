"""
Test runner for exercise validation.
"""
import logging
import json
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class TestRunner:
    """
    Runs test cases against Ansible playbook execution results.
    """
    
    @staticmethod
    def run_tests(
        test_cases: List[Dict[str, Any]],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute test cases against playbook results.
        
        Args:
            test_cases: List of test case definitions
            execution_result: Results from playbook execution
        
        Returns:
            Test execution results
        """
        if not execution_result.get('success'):
            return {
                "passed": False,
                "total_tests": len(test_cases),
                "passed_tests": 0,
                "failed_tests": len(test_cases),
                "test_results": [],
                "error": "Playbook execution failed"
            }
        
        test_results = []
        passed_count = 0
        
        for i, test_case in enumerate(test_cases):
            result = TestRunner._run_single_test(
                test_case,
                execution_result
            )
            test_results.append(result)
            if result['passed']:
                passed_count += 1
        
        return {
            "passed": passed_count == len(test_cases),
            "total_tests": len(test_cases),
            "passed_tests": passed_count,
            "failed_tests": len(test_cases) - passed_count,
            "test_results": test_results
        }
    
    @staticmethod
    def _run_single_test(
        test_case: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run a single test case.
        
        Args:
            test_case: Test case definition
            execution_result: Execution results
        
        Returns:
            Single test result
        """
        test_type = test_case.get('type', 'output_contains')
        
        try:
            if test_type == 'output_contains':
                return TestRunner._test_output_contains(test_case, execution_result)
            elif test_type == 'exit_code':
                return TestRunner._test_exit_code(test_case, execution_result)
            elif test_type == 'task_changed':
                return TestRunner._test_task_changed(test_case, execution_result)
            elif test_type == 'no_errors':
                return TestRunner._test_no_errors(test_case, execution_result)
            else:
                return {
                    "passed": False,
                    "name": test_case.get('name', 'Unknown test'),
                    "error": f"Unknown test type: {test_type}"
                }
        except Exception as e:
            logger.error(f"Test execution error: {e}")
            return {
                "passed": False,
                "name": test_case.get('name', 'Unknown test'),
                "error": str(e)
            }
    
    @staticmethod
    def _test_output_contains(
        test_case: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test if output contains expected string."""
        expected = test_case.get('expected', '')
        stdout = execution_result.get('stdout', '')
        passed = expected in stdout
        
        return {
            "passed": passed,
            "name": test_case.get('name', 'Output contains test'),
            "expected": expected,
            "actual": stdout[:200]  # Limit output length
        }
    
    @staticmethod
    def _test_exit_code(
        test_case: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test if exit code matches expected."""
        expected_code = test_case.get('expected', 0)
        actual_code = execution_result.get('exit_code', -1)
        passed = actual_code == expected_code
        
        return {
            "passed": passed,
            "name": test_case.get('name', 'Exit code test'),
            "expected": expected_code,
            "actual": actual_code
        }
    
    @staticmethod
    def _test_task_changed(
        test_case: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test if tasks made changes."""
        stdout = execution_result.get('stdout', '')
        # Check for 'changed=' in Ansible output
        passed = 'changed=' in stdout and 'changed=0' not in stdout
        
        return {
            "passed": passed,
            "name": test_case.get('name', 'Task changed test'),
            "message": "Tasks should make changes" if not passed else "Tasks made changes"
        }
    
    @staticmethod
    def _test_no_errors(
        test_case: Dict[str, Any],
        execution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Test that execution completed without errors."""
        stderr = execution_result.get('stderr', '')
        exit_code = execution_result.get('exit_code', -1)
        passed = exit_code == 0 and 'FAILED' not in stderr
        
        return {
            "passed": passed,
            "name": test_case.get('name', 'No errors test'),
            "message": "Execution completed without errors" if passed else "Errors detected"
        }
