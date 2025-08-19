"""
Success-First Optimizer Extension
Prioritizes task completion over cost efficiency
"""

from typing import Any, List
from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle
from agent import LoopData

class SuccessOptimizer(Extension):
    """Optimizes for success rate over cost efficiency"""
    
    def __init__(self, agent, *args, **kwargs):
        super().__init__(agent, *args, **kwargs)
        
    async def execute(self, prompts: List[str] = [], loop_data: LoopData = LoopData(), **kwargs: Any):
        """Enhance prompts for maximum success rate"""
        
        # Add success-focused system prompt
        success_prompt = """
🎯 **SUCCESS-FIRST MODE ACTIVATED**

**PRIMARY OBJECTIVE: Complete the task successfully, regardless of cost**

**Success Guidelines:**
- Use the best available models for maximum accuracy
- Provide comprehensive, detailed responses
- Don't truncate or abbreviate critical information
- Retry failed operations with enhanced context
- Use premium tools and models when needed
- Preserve all relevant context for task completion
- Explain your reasoning thoroughly
- Validate solutions before presenting them

**Resource Usage Philosophy:**
- Success > Cost efficiency
- Quality > Speed (when in conflict)
- Completeness > Brevity
- Accuracy > Everything else

**When facing resource limits:**
1. Request more context if needed
2. Use backup premium models
3. Break complex tasks into smaller successful pieces
4. Never compromise on task completion

**Remember: A successful expensive solution is infinitely better than a failed cheap attempt.**
"""
        
        prompts.append(success_prompt)
        
        # Log success mode activation
        PrintStyle(font_color="green", padding=False).print("🎯 Success-First Mode: Prioritizing task completion over cost")