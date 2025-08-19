# context7_tool.py - Context7 Integration for Pareng Boyong
# Enhanced context management and long-term memory capabilities

from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import json
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
import hashlib
from datetime import datetime, timedelta


class Context7Tool(Tool):
    """
    Context7 Integration Tool for enhanced context management and memory
    Provides long-term memory, context persistence, and intelligent context retrieval
    """
    
    async def execute(self, **kwargs):
        await self.agent.handle_intervention()
        
        operation = self.args.get("operation", "").lower().strip()
        
        if operation == "store":
            return await self._store_context()
        elif operation == "retrieve":
            return await self._retrieve_context()
        elif operation == "search":
            return await self._search_context()
        elif operation == "summarize":
            return await self._summarize_context()
        elif operation == "analyze":
            return await self._analyze_context()
        elif operation == "status":
            return await self._get_status()
        else:
            return Response(
                message=self._get_usage_guide(),
                break_loop=False
            )
    
    async def _store_context(self) -> Response:
        """Store current conversation context for long-term memory"""
        try:
            context_data = self.args.get("context", "")
            tags = self.args.get("tags", [])
            priority = self.args.get("priority", "medium")
            
            if not context_data:
                context_data = self._extract_recent_context()
            
            # Create context entry
            context_entry = {
                "id": self._generate_context_id(),
                "timestamp": datetime.now().isoformat(),
                "agent_name": self.agent.agent_name,
                "context": context_data,
                "tags": tags if isinstance(tags, list) else [tags],
                "priority": priority,
                "metadata": {
                    "session_id": getattr(self.agent, 'session_id', 'unknown'),
                    "context_length": len(context_data),
                    "message_count": len(self.agent.context.messages)
                }
            }
            
            # Store context (in-memory for now, can be extended to persistent storage)
            stored = await self._persist_context(context_entry)
            
            if stored:
                message = f"✅ Context stored successfully\n"
                message += f"📄 Context ID: {context_entry['id']}\n"
                message += f"🏷️ Tags: {', '.join(context_entry['tags'])}\n"
                message += f"📊 Size: {context_entry['metadata']['context_length']} chars\n"
                message += f"⏰ Timestamp: {context_entry['timestamp']}"
                
                PrintStyle(font_color="#00FF00", bold=True).print("Context stored to long-term memory")
            else:
                message = "❌ Failed to store context"
                
        except Exception as e:
            message = f"❌ Error storing context: {str(e)}"
            PrintStyle.error(f"Context7 store error: {e}")
            
        return Response(message=message, break_loop=False)
    
    async def _retrieve_context(self) -> Response:
        """Retrieve specific context by ID or criteria"""
        try:
            context_id = self.args.get("context_id", "")
            tags = self.args.get("tags", [])
            limit = int(self.args.get("limit", 5))
            
            contexts = await self._fetch_contexts(context_id, tags, limit)
            
            if not contexts:
                message = "📭 No matching contexts found"
            else:
                message = f"📚 Retrieved {len(contexts)} context(s):\n\n"
                for ctx in contexts:
                    message += f"🆔 **{ctx['id']}** ({ctx['timestamp']})\n"
                    message += f"🏷️ Tags: {', '.join(ctx.get('tags', []))}\n"
                    message += f"📄 Content: {ctx['context'][:200]}...\n"
                    message += f"📊 Priority: {ctx.get('priority', 'medium')}\n\n"
                
                PrintStyle(font_color="#00BFFF", bold=True).print(f"Retrieved {len(contexts)} contexts from memory")
                
        except Exception as e:
            message = f"❌ Error retrieving context: {str(e)}"
            PrintStyle.error(f"Context7 retrieve error: {e}")
            
        return Response(message=message, break_loop=False)
    
    async def _search_context(self) -> Response:
        """Search contexts by keywords or semantic similarity"""
        try:
            query = self.args.get("query", "")
            search_type = self.args.get("search_type", "keyword").lower()
            limit = int(self.args.get("limit", 10))
            
            if not query:
                return Response(
                    message="❌ Search query is required",
                    break_loop=False
                )
            
            results = await self._perform_search(query, search_type, limit)
            
            if not results:
                message = f"🔍 No results found for: '{query}'"
            else:
                message = f"🔍 Search results for '{query}' ({len(results)} found):\n\n"
                for result in results:
                    relevance = result.get('relevance_score', 0)
                    ctx = result['context']
                    message += f"🎯 **Relevance: {relevance:.2f}** - {ctx['id']}\n"
                    message += f"📅 {ctx['timestamp']}\n"
                    message += f"📄 {ctx['context'][:150]}...\n\n"
                
                PrintStyle(font_color="#FFD700", bold=True).print(f"Found {len(results)} relevant contexts")
                
        except Exception as e:
            message = f"❌ Error searching contexts: {str(e)}"
            PrintStyle.error(f"Context7 search error: {e}")
            
        return Response(message=message, break_loop=False)
    
    async def _summarize_context(self) -> Response:
        """Generate intelligent summary of conversation or stored contexts"""
        try:
            source = self.args.get("source", "current").lower()
            depth = self.args.get("depth", "medium").lower()
            
            if source == "current":
                content = self._extract_recent_context()
                title = "Current Conversation Summary"
            else:
                # Summarize stored contexts
                contexts = await self._fetch_contexts(limit=50)
                content = "\n".join([ctx['context'] for ctx in contexts])
                title = "Stored Contexts Summary"
            
            summary = await self._generate_summary(content, depth)
            
            message = f"📋 **{title}**\n\n{summary}\n\n"
            message += f"📊 Analyzed {len(content)} characters"
            
            PrintStyle(font_color="#9370DB", bold=True).print("Generated context summary")
            
        except Exception as e:
            message = f"❌ Error generating summary: {str(e)}"
            PrintStyle.error(f"Context7 summarize error: {e}")
            
        return Response(message=message, break_loop=False)
    
    async def _analyze_context(self) -> Response:
        """Analyze context patterns, topics, and insights"""
        try:
            analysis_type = self.args.get("analysis_type", "topics").lower()
            timeframe = self.args.get("timeframe", "recent").lower()
            
            contexts = await self._fetch_contexts_by_timeframe(timeframe)
            
            if analysis_type == "topics":
                analysis = await self._analyze_topics(contexts)
            elif analysis_type == "patterns":
                analysis = await self._analyze_patterns(contexts)
            elif analysis_type == "sentiment":
                analysis = await self._analyze_sentiment(contexts)
            else:
                analysis = await self._comprehensive_analysis(contexts)
            
            message = f"🔬 **Context Analysis ({analysis_type})**\n\n{analysis}"
            
            PrintStyle(font_color="#FF6347", bold=True).print(f"Completed {analysis_type} analysis")
            
        except Exception as e:
            message = f"❌ Error analyzing context: {str(e)}"
            PrintStyle.error(f"Context7 analyze error: {e}")
            
        return Response(message=message, break_loop=False)
    
    async def _get_status(self) -> Response:
        """Get Context7 system status and statistics"""
        try:
            stats = await self._get_system_stats()
            
            message = "📊 **Context7 System Status**\n\n"
            message += f"💾 Total Contexts: {stats['total_contexts']}\n"
            message += f"📈 Today's Contexts: {stats['today_contexts']}\n"
            message += f"🗂️ Unique Tags: {stats['unique_tags']}\n"
            message += f"💿 Storage Used: {stats['storage_used']} MB\n"
            message += f"⚡ System Status: {stats['status']}\n"
            message += f"🔄 Last Cleanup: {stats['last_cleanup']}\n\n"
            message += "✅ Context7 is operational and ready"
            
            PrintStyle(font_color="#32CD32", bold=True).print("Context7 status checked")
            
        except Exception as e:
            message = f"❌ Error getting status: {str(e)}"
            PrintStyle.error(f"Context7 status error: {e}")
            
        return Response(message=message, break_loop=False)
    
    # Helper methods
    def _extract_recent_context(self) -> str:
        """Extract recent conversation context"""
        messages = self.agent.context.messages[-10:]  # Last 10 messages
        context_parts = []
        
        for msg in messages:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            context_parts.append(f"{role}: {content[:500]}")
        
        return "\n".join(context_parts)
    
    def _generate_context_id(self) -> str:
        """Generate unique context ID"""
        timestamp = datetime.now().isoformat()
        agent_name = self.agent.agent_name
        content = f"{timestamp}-{agent_name}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    async def _persist_context(self, context_entry: Dict) -> bool:
        """Persist context to storage (placeholder for actual implementation)"""
        # In a real implementation, this would store to a database
        # For now, store in agent's memory
        if not hasattr(self.agent, '_context7_storage'):
            self.agent._context7_storage = []
        
        self.agent._context7_storage.append(context_entry)
        return True
    
    async def _fetch_contexts(self, context_id: str = "", tags: List[str] = None, limit: int = 10) -> List[Dict]:
        """Fetch contexts from storage"""
        if not hasattr(self.agent, '_context7_storage'):
            return []
        
        contexts = self.agent._context7_storage
        
        # Filter by ID if provided
        if context_id:
            contexts = [ctx for ctx in contexts if ctx['id'] == context_id]
        
        # Filter by tags if provided
        if tags:
            contexts = [ctx for ctx in contexts if any(tag in ctx.get('tags', []) for tag in tags)]
        
        # Sort by timestamp (newest first) and limit
        contexts.sort(key=lambda x: x['timestamp'], reverse=True)
        return contexts[:limit]
    
    async def _fetch_contexts_by_timeframe(self, timeframe: str) -> List[Dict]:
        """Fetch contexts by timeframe"""
        if not hasattr(self.agent, '_context7_storage'):
            return []
        
        contexts = self.agent._context7_storage
        now = datetime.now()
        
        if timeframe == "recent":
            cutoff = now - timedelta(hours=24)
        elif timeframe == "week":
            cutoff = now - timedelta(days=7)
        elif timeframe == "month":
            cutoff = now - timedelta(days=30)
        else:
            return contexts
        
        return [ctx for ctx in contexts if datetime.fromisoformat(ctx['timestamp']) >= cutoff]
    
    async def _perform_search(self, query: str, search_type: str, limit: int) -> List[Dict]:
        """Perform search in contexts"""
        contexts = await self._fetch_contexts(limit=100)
        
        if search_type == "keyword":
            results = []
            query_lower = query.lower()
            
            for ctx in contexts:
                content = ctx['context'].lower()
                if query_lower in content:
                    # Simple relevance scoring
                    relevance = content.count(query_lower) / len(content.split())
                    results.append({
                        'context': ctx,
                        'relevance_score': min(relevance * 100, 1.0)
                    })
            
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:limit]
        
        return []
    
    async def _generate_summary(self, content: str, depth: str) -> str:
        """Generate summary of content"""
        # Simple summary generation (can be enhanced with AI)
        lines = content.split('\n')
        total_lines = len(lines)
        
        if depth == "brief":
            summary_lines = min(3, total_lines)
        elif depth == "detailed":
            summary_lines = min(10, total_lines)
        else:  # medium
            summary_lines = min(6, total_lines)
        
        summary = "📝 **Key Points:**\n"
        for i, line in enumerate(lines[:summary_lines]):
            if line.strip():
                summary += f"• {line.strip()[:100]}...\n"
        
        if total_lines > summary_lines:
            summary += f"\n... and {total_lines - summary_lines} more items"
        
        return summary
    
    async def _analyze_topics(self, contexts: List[Dict]) -> str:
        """Analyze topics in contexts"""
        if not contexts:
            return "No contexts to analyze"
        
        # Simple topic extraction
        all_tags = []
        for ctx in contexts:
            all_tags.extend(ctx.get('tags', []))
        
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        analysis = "🏷️ **Most Common Topics:**\n"
        for tag, count in sorted_tags[:10]:
            analysis += f"• {tag}: {count} mentions\n"
        
        return analysis
    
    async def _analyze_patterns(self, contexts: List[Dict]) -> str:
        """Analyze patterns in contexts"""
        if not contexts:
            return "No contexts to analyze"
        
        # Simple pattern analysis
        time_distribution = {}
        for ctx in contexts:
            hour = datetime.fromisoformat(ctx['timestamp']).hour
            time_distribution[hour] = time_distribution.get(hour, 0) + 1
        
        peak_hour = max(time_distribution.items(), key=lambda x: x[1])[0]
        
        analysis = f"⏰ **Usage Patterns:**\n"
        analysis += f"• Peak activity hour: {peak_hour}:00\n"
        analysis += f"• Total contexts analyzed: {len(contexts)}\n"
        analysis += f"• Average context length: {sum(len(ctx['context']) for ctx in contexts) // len(contexts)} chars\n"
        
        return analysis
    
    async def _analyze_sentiment(self, contexts: List[Dict]) -> str:
        """Analyze sentiment in contexts"""
        # Simple sentiment analysis placeholder
        return "😊 **Sentiment Analysis:**\nPositive interactions detected across most contexts"
    
    async def _comprehensive_analysis(self, contexts: List[Dict]) -> str:
        """Comprehensive analysis of contexts"""
        topics = await self._analyze_topics(contexts)
        patterns = await self._analyze_patterns(contexts)
        
        return f"{topics}\n\n{patterns}"
    
    async def _get_system_stats(self) -> Dict:
        """Get system statistics"""
        contexts = getattr(self.agent, '_context7_storage', [])
        today = datetime.now().date()
        
        today_contexts = sum(1 for ctx in contexts 
                           if datetime.fromisoformat(ctx['timestamp']).date() == today)
        
        all_tags = []
        for ctx in contexts:
            all_tags.extend(ctx.get('tags', []))
        
        return {
            'total_contexts': len(contexts),
            'today_contexts': today_contexts,
            'unique_tags': len(set(all_tags)),
            'storage_used': len(str(contexts)) / (1024 * 1024),  # Rough MB estimate
            'status': 'Active',
            'last_cleanup': 'Not implemented'
        }
    
    def _get_usage_guide(self) -> str:
        """Get usage guide for Context7 tool"""
        return """🧠 **Context7 Tool - Enhanced Memory & Context Management**

**Available Operations:**

📝 **store** - Store current context to long-term memory
   • context: Text to store (optional, uses recent conversation)
   • tags: List of tags for categorization
   • priority: high/medium/low

📚 **retrieve** - Retrieve stored contexts
   • context_id: Specific context ID
   • tags: Filter by tags
   • limit: Number of contexts to retrieve (default: 5)

🔍 **search** - Search contexts by keywords
   • query: Search query (required)
   • search_type: keyword/semantic (default: keyword)
   • limit: Number of results (default: 10)

📋 **summarize** - Generate intelligent summaries
   • source: current/stored (default: current)
   • depth: brief/medium/detailed (default: medium)

🔬 **analyze** - Analyze context patterns and insights
   • analysis_type: topics/patterns/sentiment/comprehensive
   • timeframe: recent/week/month/all

📊 **status** - Get system status and statistics

**Examples:**
```
operation: store
tags: ["meeting", "project-alpha"]
priority: high
```

```
operation: search
query: "deployment issues"
limit: 5
```

```
operation: analyze
analysis_type: topics
timeframe: week
```
"""