# app/agent/tools/web_search_tool.py
# ─────────────────────────────────────────────────────────────────
# Tool 4: web_search_tool
# Built-in OpenAI Agents SDK web search tool instance.
# ─────────────────────────────────────────────────────────────────

from agents import WebSearchTool

"""
This module provides a singleton instance of the WebSearchTool from the
OpenAI Agents SDK. The Risk Analysis Agent uses this tool to autonomously
fill data gaps not available in the ClimaSync collection database, such as
real-time media reports, current NGO presence, and localized demographic details.
"""

web_search_tool = WebSearchTool()
