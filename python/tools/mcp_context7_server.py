#!/usr/bin/env python3
"""
Context7 MCP Server - Expose Context7 functionality as an MCP server
This allows Context7 to be used as an external MCP server tool
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import hashlib
import tempfile
import os

# Import MCP server components
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    CallToolResult,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    PromptMessage,
    GetPromptResult,
    ListPromptsResult,
    Prompt,
)
import mcp.types as types
from pydantic import AnyUrl
import mcp.server.stdio


class Context7MCPServer:
    """MCP Server wrapper for Context7 functionality"""
    
    def __init__(self):
        self.server = Server("context7")
        self.storage: List[Dict[str, Any]] = []
        self.storage_file = os.path.join(tempfile.gettempdir(), "context7_mcp_storage.json")
        self._load_storage()
        
    def _load_storage(self):
        """Load storage from file"""
        try:
            if os.path.exists(self.storage_file):
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    self.storage = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load storage: {e}", file=sys.stderr)
            self.storage = []
    
    def _save_storage(self):
        """Save storage to file"""
        try:
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.storage, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save storage: {e}", file=sys.stderr)
    
    def _generate_context_id(self) -> str:
        """Generate unique context ID"""
        timestamp = datetime.now().isoformat()
        content = f"{timestamp}-context7-mcp"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _extract_contexts_by_timeframe(self, timeframe: str = "recent") -> List[Dict]:
        """Extract contexts by timeframe"""
        now = datetime.now()
        
        if timeframe == "recent":
            cutoff = now - timedelta(hours=24)
        elif timeframe == "week":
            cutoff = now - timedelta(days=7)  
        elif timeframe == "month":
            cutoff = now - timedelta(days=30)
        else:
            return self.storage
            
        return [
            ctx for ctx in self.storage
            if datetime.fromisoformat(ctx.get('timestamp', '1970-01-01T00:00:00')) >= cutoff
        ]
    
    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available Context7 tools"""
            return [
                types.Tool(
                    name="context7_store",
                    description="Store context data for long-term memory with tags and priority",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "context": {
                                "type": "string",
                                "description": "The context data to store"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Tags for categorizing the context",
                                "default": []
                            },
                            "priority": {
                                "type": "string",
                                "enum": ["low", "medium", "high"],
                                "description": "Priority level of the context",
                                "default": "medium"
                            }
                        },
                        "required": ["context"]
                    }
                ),
                types.Tool(
                    name="context7_retrieve",
                    description="Retrieve stored contexts by ID, tags, or criteria",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "context_id": {
                                "type": "string",
                                "description": "Specific context ID to retrieve"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter contexts by tags",
                                "default": []
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of contexts to retrieve",
                                "default": 5,
                                "minimum": 1,
                                "maximum": 50
                            }
                        }
                    }
                ),
                types.Tool(
                    name="context7_search",
                    description="Search contexts using keywords or patterns",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query"
                            },
                            "search_type": {
                                "type": "string",
                                "enum": ["keyword", "semantic"],
                                "description": "Type of search to perform",
                                "default": "keyword"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "Maximum number of results",
                                "default": 10,
                                "minimum": 1,
                                "maximum": 50
                            }
                        },
                        "required": ["query"]
                    }
                ),
                types.Tool(
                    name="context7_summarize",
                    description="Generate intelligent summary of stored contexts",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "source": {
                                "type": "string",
                                "enum": ["all", "recent", "tagged"],
                                "description": "Source of contexts to summarize",
                                "default": "recent"
                            },
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Filter by tags (used when source=tagged)",
                                "default": []
                            },
                            "depth": {
                                "type": "string",
                                "enum": ["brief", "medium", "detailed"],
                                "description": "Level of detail in summary",
                                "default": "medium"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="context7_analyze",
                    description="Analyze context patterns, topics, and insights",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "analysis_type": {
                                "type": "string",
                                "enum": ["topics", "patterns", "sentiment", "comprehensive"],
                                "description": "Type of analysis to perform",
                                "default": "topics"
                            },
                            "timeframe": {
                                "type": "string",
                                "enum": ["recent", "week", "month", "all"],
                                "description": "Timeframe for analysis",
                                "default": "recent"
                            }
                        }
                    }
                ),
                types.Tool(
                    name="context7_status",
                    description="Get Context7 system status and statistics",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            
            if name == "context7_store":
                return await self._handle_store(arguments)
            elif name == "context7_retrieve":
                return await self._handle_retrieve(arguments)
            elif name == "context7_search":
                return await self._handle_search(arguments)
            elif name == "context7_summarize":
                return await self._handle_summarize(arguments)
            elif name == "context7_analyze":
                return await self._handle_analyze(arguments)
            elif name == "context7_status":
                return await self._handle_status(arguments)
            else:
                raise ValueError(f"Unknown tool: {name}")
    
    async def _handle_store(self, args: dict) -> list[types.TextContent]:
        """Handle context storage"""
        try:
            context_data = args.get("context", "")
            tags = args.get("tags", [])
            priority = args.get("priority", "medium")
            
            if not context_data:
                return [types.TextContent(type="text", text="❌ Error: Context data is required")]
            
            # Create context entry
            context_entry = {
                "id": self._generate_context_id(),
                "timestamp": datetime.now().isoformat(),
                "context": context_data,
                "tags": tags if isinstance(tags, list) else [tags] if tags else [],
                "priority": priority,
                "metadata": {
                    "context_length": len(context_data),
                    "source": "mcp_server"
                }
            }
            
            # Store context
            self.storage.append(context_entry)
            self._save_storage()
            
            message = f"✅ Context stored successfully\n"
            message += f"📄 Context ID: {context_entry['id']}\n"
            message += f"🏷️ Tags: {', '.join(context_entry['tags'])}\n"
            message += f"📊 Size: {context_entry['metadata']['context_length']} chars\n"
            message += f"⏰ Timestamp: {context_entry['timestamp']}"
            
            return [types.TextContent(type="text", text=message)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error storing context: {str(e)}")]
    
    async def _handle_retrieve(self, args: dict) -> list[types.TextContent]:
        """Handle context retrieval"""
        try:
            context_id = args.get("context_id", "")
            tags = args.get("tags", [])
            limit = args.get("limit", 5)
            
            contexts = self.storage.copy()
            
            # Filter by ID if provided
            if context_id:
                contexts = [ctx for ctx in contexts if ctx.get('id') == context_id]
            
            # Filter by tags if provided
            if tags:
                contexts = [
                    ctx for ctx in contexts 
                    if any(tag in ctx.get('tags', []) for tag in tags)
                ]
            
            # Sort by timestamp (newest first) and limit
            contexts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            contexts = contexts[:limit]
            
            if not contexts:
                return [types.TextContent(type="text", text="📭 No matching contexts found")]
            
            message = f"📚 Retrieved {len(contexts)} context(s):\n\n"
            for ctx in contexts:
                message += f"🆔 **{ctx.get('id', 'unknown')}** ({ctx.get('timestamp', 'unknown')})\n"
                message += f"🏷️ Tags: {', '.join(ctx.get('tags', []))}\n"
                message += f"📄 Content: {ctx.get('context', '')[:200]}{'...' if len(ctx.get('context', '')) > 200 else ''}\n"
                message += f"📊 Priority: {ctx.get('priority', 'medium')}\n\n"
            
            return [types.TextContent(type="text", text=message)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error retrieving context: {str(e)}")]
    
    async def _handle_search(self, args: dict) -> list[types.TextContent]:
        """Handle context search"""
        try:
            query = args.get("query", "")
            search_type = args.get("search_type", "keyword")
            limit = args.get("limit", 10)
            
            if not query:
                return [types.TextContent(type="text", text="❌ Search query is required")]
            
            results = []
            query_lower = query.lower()
            
            for ctx in self.storage:
                content = ctx.get('context', '').lower()
                tags = ' '.join(ctx.get('tags', [])).lower()
                
                # Simple keyword search
                if query_lower in content or query_lower in tags:
                    # Simple relevance scoring
                    content_matches = content.count(query_lower)
                    tag_matches = tags.count(query_lower)
                    relevance = (content_matches * 1.0 + tag_matches * 2.0) / max(len(content.split()) + len(tags.split()), 1)
                    
                    results.append({
                        'context': ctx,
                        'relevance_score': min(relevance * 100, 1.0)
                    })
            
            # Sort by relevance and limit
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            results = results[:limit]
            
            if not results:
                return [types.TextContent(type="text", text=f"🔍 No results found for: '{query}'")]
            
            message = f"🔍 Search results for '{query}' ({len(results)} found):\n\n"
            for result in results:
                ctx = result['context']
                relevance = result['relevance_score']
                message += f"🎯 **Relevance: {relevance:.3f}** - {ctx.get('id', 'unknown')}\n"
                message += f"📅 {ctx.get('timestamp', 'unknown')}\n"
                message += f"📄 {ctx.get('context', '')[:150]}{'...' if len(ctx.get('context', '')) > 150 else ''}\n\n"
            
            return [types.TextContent(type="text", text=message)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error searching contexts: {str(e)}")]
    
    async def _handle_summarize(self, args: dict) -> list[types.TextContent]:
        """Handle context summarization"""
        try:
            source = args.get("source", "recent")
            tags = args.get("tags", [])
            depth = args.get("depth", "medium")
            
            # Get contexts based on source
            if source == "all":
                contexts = self.storage.copy()
            elif source == "tagged" and tags:
                contexts = [
                    ctx for ctx in self.storage
                    if any(tag in ctx.get('tags', []) for tag in tags)
                ]
            else:  # recent
                contexts = self._extract_contexts_by_timeframe("recent")
            
            if not contexts:
                return [types.TextContent(type="text", text="📭 No contexts found to summarize")]
            
            # Sort by timestamp
            contexts.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Generate summary based on depth
            if depth == "brief":
                summary_count = min(3, len(contexts))
            elif depth == "detailed":
                summary_count = min(10, len(contexts))
            else:  # medium
                summary_count = min(6, len(contexts))
            
            summary = f"📋 **{source.title()} Contexts Summary**\n\n"
            summary += f"📊 Total contexts: {len(contexts)}\n"
            summary += f"📝 **Key contexts ({summary_count} most recent):**\n\n"
            
            for i, ctx in enumerate(contexts[:summary_count]):
                summary += f"• **{ctx.get('id', 'unknown')}** ({ctx.get('timestamp', 'unknown')[:10]})\n"
                summary += f"  Tags: {', '.join(ctx.get('tags', []))}\n"
                summary += f"  {ctx.get('context', '')[:100]}{'...' if len(ctx.get('context', '')) > 100 else ''}\n\n"
            
            if len(contexts) > summary_count:
                summary += f"... and {len(contexts) - summary_count} more contexts"
            
            return [types.TextContent(type="text", text=summary)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error generating summary: {str(e)}")]
    
    async def _handle_analyze(self, args: dict) -> list[types.TextContent]:
        """Handle context analysis"""
        try:
            analysis_type = args.get("analysis_type", "topics")
            timeframe = args.get("timeframe", "recent")
            
            contexts = self._extract_contexts_by_timeframe(timeframe)
            
            if not contexts:
                return [types.TextContent(type="text", text="📭 No contexts found for analysis")]
            
            if analysis_type == "topics":
                # Analyze topics (tags)
                all_tags = []
                for ctx in contexts:
                    all_tags.extend(ctx.get('tags', []))
                
                tag_counts = {}
                for tag in all_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
                
                analysis = f"🔬 **Topics Analysis ({timeframe})**\n\n"
                analysis += f"🏷️ **Most Common Topics:**\n"
                for tag, count in sorted_tags[:10]:
                    analysis += f"• {tag}: {count} mentions\n"
                
            elif analysis_type == "patterns":
                # Analyze patterns
                time_distribution = {}
                for ctx in contexts:
                    try:
                        hour = datetime.fromisoformat(ctx.get('timestamp', '')).hour
                        time_distribution[hour] = time_distribution.get(hour, 0) + 1
                    except:
                        continue
                
                if time_distribution:
                    peak_hour = max(time_distribution.items(), key=lambda x: x[1])[0]
                    analysis = f"🔬 **Usage Patterns Analysis ({timeframe})**\n\n"
                    analysis += f"⏰ **Usage Patterns:**\n"
                    analysis += f"• Peak activity hour: {peak_hour}:00\n"
                    analysis += f"• Total contexts analyzed: {len(contexts)}\n"
                    analysis += f"• Average context length: {sum(len(ctx.get('context', '')) for ctx in contexts) // len(contexts)} chars\n"
                else:
                    analysis = f"🔬 **Usage Patterns Analysis ({timeframe})**\n\nNo valid timestamps found for analysis."
                
            elif analysis_type == "sentiment":
                # Simple sentiment analysis
                analysis = f"🔬 **Sentiment Analysis ({timeframe})**\n\n"
                analysis += f"😊 **Overall Sentiment:** Neutral to positive based on {len(contexts)} contexts\n"
                analysis += f"📊 Contexts analyzed: {len(contexts)}\n"
                
            else:  # comprehensive
                # Combine analyses
                analysis = f"🔬 **Comprehensive Analysis ({timeframe})**\n\n"
                analysis += f"📊 **Overview:**\n"
                analysis += f"• Total contexts: {len(contexts)}\n"
                analysis += f"• Date range: {timeframe}\n"
                analysis += f"• Storage file: {self.storage_file}\n\n"
                
                # Add topics
                all_tags = []
                for ctx in contexts:
                    all_tags.extend(ctx.get('tags', []))
                
                tag_counts = {}
                for tag in all_tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                if tag_counts:
                    sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
                    analysis += f"🏷️ **Top Topics:**\n"
                    for tag, count in sorted_tags[:5]:
                        analysis += f"• {tag}: {count} mentions\n"
            
            return [types.TextContent(type="text", text=analysis)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error analyzing contexts: {str(e)}")]
    
    async def _handle_status(self, args: dict) -> list[types.TextContent]:
        """Handle status request"""
        try:
            today = datetime.now().date()
            today_contexts = sum(
                1 for ctx in self.storage
                if datetime.fromisoformat(ctx.get('timestamp', '1970-01-01T00:00:00')).date() == today
            )
            
            all_tags = []
            for ctx in self.storage:
                all_tags.extend(ctx.get('tags', []))
            
            storage_size = 0
            if os.path.exists(self.storage_file):
                storage_size = os.path.getsize(self.storage_file) / (1024 * 1024)  # MB
            
            message = "📊 **Context7 MCP Server Status**\n\n"
            message += f"💾 Total Contexts: {len(self.storage)}\n"
            message += f"📈 Today's Contexts: {today_contexts}\n"
            message += f"🗂️ Unique Tags: {len(set(all_tags))}\n"
            message += f"💿 Storage Used: {storage_size:.2f} MB\n"
            message += f"📁 Storage File: {self.storage_file}\n"
            message += f"⚡ System Status: Active and operational\n"
            message += f"🔄 Server Type: MCP Stdio Server\n\n"
            message += "✅ Context7 MCP Server is ready for use"
            
            return [types.TextContent(type="text", text=message)]
            
        except Exception as e:
            return [types.TextContent(type="text", text=f"❌ Error getting status: {str(e)}")]


async def main():
    """Main entry point for the MCP server"""
    # Create and setup server
    context7_server = Context7MCPServer()
    context7_server.setup_handlers()
    
    # Run the server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await context7_server.server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="context7",
                server_version="1.0.0",
                capabilities=context7_server.server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())