"""
Review Packet Parser - Hard Gate Enforcement (Phase 1)
Validates REVIEW_PACKET.md against required sections and parses into structured object.
HARD REJECT if any required section is missing.
"""
import os
import re
import json
from typing import Dict, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger("review_packet_parser")

# Phase 1 required sections — exact spec
REQUIRED_SECTIONS = [
    "ENTRY POINT",
    "CORE FLOW",
    "LIVE FLOW",
    "OUTPUT SAMPLE",
]


@dataclass
class ReviewPacketData:
    """Structured parsed object from REVIEW_PACKET.md"""
    entry_point: str
    core_flow: str
    live_flow: str
    output_sample: Dict[str, Any]
    raw_content: str
    sections_found: list = field(default_factory=list)


class ReviewPacketParser:
    """
    Phase 1 Hard Gate — REVIEW_PACKET.md enforcement.
    Missing file or missing any required section = HARD REJECT, score 0.
    """

    def __init__(self, packet_path: str = "REVIEW_PACKET.md"):
        self.packet_path = packet_path
        self.required_sections = REQUIRED_SECTIONS

    def enforce_packet_requirement(self, project_root: str) -> Dict[str, Any]:
        """
        Hard gate check. Returns dict with valid=True/False.
        If valid=False the caller must immediately reject the submission.
        """
        packet_file = os.path.join(project_root, self.packet_path)

        # Gate 1: file exists
        if not os.path.exists(packet_file):
            logger.error(f"[PACKET] HARD REJECT — REVIEW_PACKET.md not found at {packet_file}")
            return {
                "valid": False,
                "reason": "REVIEW_PACKET.md file missing",
                "rejection_type": "HARD_GATE_FAILURE",
                "required_action": "Create REVIEW_PACKET.md with sections: " + ", ".join(REQUIRED_SECTIONS)
            }

        # Gate 2: readable + non-empty
        try:
            with open(packet_file, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.error(f"[PACKET] HARD REJECT — cannot read REVIEW_PACKET.md: {e}")
            return {
                "valid": False,
                "reason": f"REVIEW_PACKET.md unreadable: {e}",
                "rejection_type": "HARD_GATE_FAILURE"
            }

        if len(content.strip()) < 50:
            return {
                "valid": False,
                "reason": "REVIEW_PACKET.md is empty or too short",
                "rejection_type": "HARD_GATE_FAILURE"
            }

        # Gate 3: all required sections present
        missing = [s for s in self.required_sections if s not in content.upper()]
        if missing:
            logger.error(f"[PACKET] HARD REJECT — missing sections: {missing}")
            return {
                "valid": False,
                "reason": f"Missing required sections: {', '.join(missing)}",
                "rejection_type": "HARD_GATE_FAILURE",
                "missing_sections": missing
            }

        # Parse into structured object
        try:
            parsed = self._parse(content)
            logger.info("[PACKET] REVIEW_PACKET.md validated and parsed successfully")
            return {
                "valid": True,
                "parsed_data": parsed,
                "content_length": len(content),
                "sections_found": parsed.sections_found
            }
        except Exception as e:
            logger.error(f"[PACKET] Parse error: {e}")
            return {
                "valid": False,
                "reason": f"Packet parse failed: {e}",
                "rejection_type": "HARD_GATE_FAILURE"
            }

    def _parse(self, content: str) -> ReviewPacketData:
        upper = content.upper()

        entry_point = self._extract(content, upper, "ENTRY POINT", ["CORE FLOW", "LIVE FLOW", "OUTPUT SAMPLE"])
        core_flow   = self._extract(content, upper, "CORE FLOW",   ["LIVE FLOW", "OUTPUT SAMPLE", "ENTRY POINT"])
        live_flow   = self._extract(content, upper, "LIVE FLOW",   ["OUTPUT SAMPLE", "ENTRY POINT", "CORE FLOW"])
        output_raw  = self._extract(content, upper, "OUTPUT SAMPLE", ["ENTRY POINT", "CORE FLOW", "LIVE FLOW"])
        output_sample = self._parse_json_block(output_raw)

        found = [s for s in self.required_sections if s in upper]

        return ReviewPacketData(
            entry_point=entry_point.strip(),
            core_flow=core_flow.strip(),
            live_flow=live_flow.strip(),
            output_sample=output_sample,
            raw_content=content,
            sections_found=found
        )

    def _extract(self, content: str, upper: str, section: str, end_sections: list) -> str:
        """Extract text after a section header until the next known section."""
        # Find section header position (case-insensitive via upper)
        idx = upper.find(section)
        if idx == -1:
            return ""
        # Move past the header line
        start = content.find("\n", idx)
        if start == -1:
            return ""
        start += 1

        # Find earliest end section
        end = len(content)
        for es in end_sections:
            ei = upper.find(es, start)
            if ei != -1 and ei < end:
                end = ei

        return content[start:end]

    def _parse_json_block(self, text: str) -> Dict[str, Any]:
        """Extract first JSON code block from text."""
        match = re.search(r"```(?:json)?\s*\n(.*?)\n```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        # Try raw JSON object
        match2 = re.search(r"\{.*\}", text, re.DOTALL)
        if match2:
            try:
                return json.loads(match2.group(0))
            except json.JSONDecodeError:
                pass
        return {}


# Global instance
review_packet_parser = ReviewPacketParser()
