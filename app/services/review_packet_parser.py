"""
Review Packet Parser - Hard Gate Enforcement
Implements strict check for REVIEW_PACKET.md and parses it into structured input
"""
import os
import re
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("review_packet_parser")

@dataclass
class ReviewPacketData:
    """Structured data extracted from REVIEW_PACKET.md"""
    entry_point: str
    core_flow: Dict[str, str]
    execution_flow: str
    real_output: Dict[str, Any]
    integration_points: Dict[str, str]
    determinism_proof: Dict[str, Any]
    contract_validation: Dict[str, Any]
    convergence_proof: Dict[str, Any]

class ReviewPacketParser:
    """
    Hard gate enforcement for REVIEW_PACKET.md
    Rejects submissions if packet is missing or invalid
    """
    
    def __init__(self, packet_path: str = "REVIEW_PACKET.md"):
        self.packet_path = packet_path
        self.required_sections = [
            "ENTRY POINT",
            "CORE EXECUTION FLOW",
            "FINAL CONVERGENCE EXECUTION FLOW", 
            "REAL OUTPUT",
            "INTEGRATION POINTS",
            "DETERMINISM PROOF",
            "CONTRACT VALIDATION",
            "PROOF OF CONVERGENCE"
        ]
    
    def enforce_packet_requirement(self, project_root: str) -> Dict[str, Any]:
        """
        Hard gate: Check for REVIEW_PACKET.md existence and validity
        
        Returns:
            Dict with validation result and parsed data if valid
        """
        packet_file = os.path.join(project_root, self.packet_path)
        
        # Hard gate check 1: File exists
        if not os.path.exists(packet_file):
            logger.error(f"REVIEW_PACKET.md not found at {packet_file}")
            return {
                "valid": False,
                "reason": "REVIEW_PACKET.md file missing",
                "rejection_type": "HARD_GATE_FAILURE",
                "required_action": "Create REVIEW_PACKET.md with system documentation"
            }
        
        # Hard gate check 2: File readable and has content
        try:
            with open(packet_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Cannot read REVIEW_PACKET.md: {e}")
            return {
                "valid": False,
                "reason": f"REVIEW_PACKET.md unreadable: {str(e)}",
                "rejection_type": "HARD_GATE_FAILURE"
            }
        
        if len(content.strip()) < 100:
            return {
                "valid": False,
                "reason": "REVIEW_PACKET.md too short (< 100 chars)",
                "rejection_type": "HARD_GATE_FAILURE"
            }
        
        # Hard gate check 3: Required sections present
        missing_sections = []
        for section in self.required_sections:
            if section not in content:
                missing_sections.append(section)
        
        if missing_sections:
            return {
                "valid": False,
                "reason": f"Missing required sections: {', '.join(missing_sections)}",
                "rejection_type": "HARD_GATE_FAILURE",
                "missing_sections": missing_sections
            }
        
        # Parse packet into structured data
        try:
            parsed_data = self._parse_packet_content(content)
            logger.info("REVIEW_PACKET.md successfully parsed and validated")
            return {
                "valid": True,
                "parsed_data": parsed_data,
                "content_length": len(content),
                "sections_found": len(self.required_sections)
            }
        except Exception as e:
            logger.error(f"Failed to parse REVIEW_PACKET.md: {e}")
            return {
                "valid": False,
                "reason": f"Packet parsing failed: {str(e)}",
                "rejection_type": "HARD_GATE_FAILURE"
            }
    
    def _parse_packet_content(self, content: str) -> ReviewPacketData:
        """Parse REVIEW_PACKET.md content into structured data"""
        
        # Extract entry point
        entry_point = self._extract_section(content, "ENTRY POINT", "CORE EXECUTION FLOW")
        
        # Extract core flow
        core_flow_text = self._extract_section(content, "CORE EXECUTION FLOW", "FINAL CONVERGENCE EXECUTION FLOW")
        core_flow = self._parse_core_flow(core_flow_text)
        
        # Extract execution flow
        execution_flow = self._extract_section(content, "FINAL CONVERGENCE EXECUTION FLOW", "REAL OUTPUT")
        
        # Extract and parse real output JSON
        real_output_text = self._extract_section(content, "REAL OUTPUT", "WHAT WAS CONVERGED")
        real_output = self._parse_json_from_text(real_output_text)
        
        # Extract integration points
        integration_text = self._extract_section(content, "INTEGRATION POINTS", "FAILURE CASES")
        integration_points = self._parse_integration_points(integration_text)
        
        # Extract determinism proof
        determinism_text = self._extract_section(content, "DETERMINISM PROOF", "CONTRACT VALIDATION")
        determinism_proof = self._parse_determinism_proof(determinism_text)
        
        # Extract contract validation
        contract_text = self._extract_section(content, "CONTRACT VALIDATION", "PROOF OF CONVERGENCE")
        contract_validation = self._parse_contract_validation(contract_text)
        
        # Extract convergence proof
        convergence_text = self._extract_section(content, "PROOF OF CONVERGENCE", "FINAL DETERMINISTIC")
        convergence_proof = self._parse_convergence_proof(convergence_text)
        
        return ReviewPacketData(
            entry_point=entry_point.strip(),
            core_flow=core_flow,
            execution_flow=execution_flow.strip(),
            real_output=real_output,
            integration_points=integration_points,
            determinism_proof=determinism_proof,
            contract_validation=contract_validation,
            convergence_proof=convergence_proof
        )
    
    def _extract_section(self, content: str, start_marker: str, end_marker: str) -> str:
        """Extract text between two section markers"""
        start_pattern = f"## \\d+\\. {re.escape(start_marker)}"
        end_pattern = f"## \\d+\\. {re.escape(end_marker)}"
        
        start_match = re.search(start_pattern, content)
        end_match = re.search(end_pattern, content)
        
        if not start_match:
            return ""
        
        start_pos = start_match.end()
        end_pos = end_match.start() if end_match else len(content)
        
        return content[start_pos:end_pos].strip()
    
    def _parse_core_flow(self, text: str) -> Dict[str, str]:
        """Parse core execution flow components"""
        components = {}
        
        # Extract engine descriptions
        engine_pattern = r"### (.+?): `(.+?)`\n\*\*Purpose\*\*: (.+?)\n"
        matches = re.findall(engine_pattern, text, re.DOTALL)
        
        for match in matches:
            engine_name = match[0].strip()
            file_path = match[1].strip()
            purpose = match[2].strip()
            components[engine_name] = {
                "file": file_path,
                "purpose": purpose
            }
        
        return components
    
    def _parse_json_from_text(self, text: str) -> Dict[str, Any]:
        """Extract and parse JSON from text section"""
        import json
        
        # Find JSON block
        json_pattern = r"```json\n(.*?)\n```"
        match = re.search(json_pattern, text, re.DOTALL)
        
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                return {}
        
        return {}
    
    def _parse_integration_points(self, text: str) -> Dict[str, str]:
        """Parse integration points section"""
        points = {}
        
        # Extract code blocks with file references
        code_pattern = r"\*\*File\*\*: `(.+?)` \(Line (.+?)\)\n```python\n(.*?)\n```"
        matches = re.findall(code_pattern, text, re.DOTALL)
        
        for match in matches:
            file_path = match[0]
            line_ref = match[1]
            code = match[2].strip()
            points[f"{file_path}:{line_ref}"] = code
        
        return points
    
    def _parse_determinism_proof(self, text: str) -> Dict[str, Any]:
        """Parse determinism proof section"""
        proof = {}
        
        # Extract test results
        if "Run 1 Result" in text and "Run 2 Result" in text:
            proof["deterministic"] = True
            proof["test_runs"] = 3
        
        # Extract verification file
        if "Verification File" in text:
            file_match = re.search(r"Verification File.*?`(.+?)`", text)
            if file_match:
                proof["verification_file"] = file_match.group(1)
        
        return proof
    
    def _parse_contract_validation(self, text: str) -> Dict[str, Any]:
        """Parse contract validation section"""
        validation = {}
        
        # Check for validation enforcement
        if "Validation Gate Enforcement" in text:
            validation["enforced"] = True
        
        # Extract schema validation details
        if "Schema Validation" in text:
            validation["schema_validated"] = True
        
        return validation
    
    def _parse_convergence_proof(self, text: str) -> Dict[str, Any]:
        """Parse convergence proof section"""
        proof = {}
        
        # Extract console logs
        if "Console Logs" in text:
            proof["has_console_logs"] = True
        
        # Extract system health check
        if "System Health Check" in text:
            proof["health_check_passed"] = True
        
        # Extract test results
        if "ALL TESTS PASSED" in text:
            proof["all_tests_passed"] = True
        
        return proof

# Global parser instance
review_packet_parser = ReviewPacketParser()