from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers.searxng import search
from dataclasses import dataclass
import json


@dataclass
class SearXNGTool(Tool):
    """
    SearXNG search engine integration for Pareng Boyong
    Provides privacy-focused web search capabilities
    """
    
    async def execute(self, **kwargs):
        await self.agent.handle_intervention()
        
        query = self.args.get("query", "").strip()
        if not query:
            return Response(
                message="Error: No search query provided. Please specify a 'query' parameter.",
                break_loop=False
            )
        
        try:
            PrintStyle(font_color="#00FF00", bold=True).print(
                f"Searching SearXNG for: {query}"
            )
            
            # Perform the search using the helper
            results = await search(query)
            
            # Process and format results
            if isinstance(results, dict) and "results" in results:
                search_results = results["results"]
                
                # Format results for display
                formatted_results = []
                for idx, result in enumerate(search_results[:10], 1):  # Limit to top 10
                    formatted_result = {
                        "position": idx,
                        "title": result.get("title", "No title"),
                        "url": result.get("url", ""),
                        "content": result.get("content", "No description available"),
                        "engine": result.get("engine", "Unknown")
                    }
                    formatted_results.append(formatted_result)
                
                # Create response message
                response_data = {
                    "query": query,
                    "total_results": len(search_results),
                    "displayed_results": len(formatted_results),
                    "results": formatted_results
                }
                
                # Also create a text summary
                text_summary = f"SearXNG Search Results for '{query}':\n\n"
                for result in formatted_results:
                    text_summary += f"{result['position']}. {result['title']}\n"
                    text_summary += f"   URL: {result['url']}\n"
                    text_summary += f"   {result['content'][:150]}...\n\n"
                
                return Response(
                    message=text_summary + "\n\nFull results:\n" + json.dumps(response_data, indent=2),
                    break_loop=False
                )
            else:
                return Response(
                    message=f"No results found for query: {query}",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"SearXNG search failed: {str(e)}")
            return Response(
                message=f"Error performing search: {str(e)}",
                break_loop=False
            )