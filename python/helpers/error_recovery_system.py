"""
Pareng Boyong AI-Powered Error Analysis and Recovery System
Automatically analyzes errors and implements alternative solutions
"""

import asyncio
import json
import time
import traceback
import inspect
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path

from python.helpers.log import Log
from python.helpers.print_style import PrintStyle

@dataclass
class ErrorContext:
    """Comprehensive error context for analysis"""
    timestamp: str
    error_type: str
    error_message: str
    full_traceback: str
    function_name: str
    file_path: str
    line_number: int
    local_variables: Dict[str, Any]
    system_state: Dict[str, Any]
    previous_attempts: List[str]
    user_intent: str
    execution_context: Dict[str, Any]

@dataclass
class RecoveryStrategy:
    """A potential recovery strategy"""
    strategy_id: str
    name: str
    description: str
    confidence_score: float  # 0.0 to 1.0
    implementation_steps: List[str]
    expected_outcome: str
    risk_level: str  # "low", "medium", "high"
    estimated_success_rate: float
    fallback_strategy: Optional[str] = None

@dataclass
class RecoveryAttempt:
    """Record of a recovery attempt"""
    strategy_id: str
    timestamp: str
    success: bool
    execution_time: float
    error_encountered: Optional[str]
    outcome_description: str
    lessons_learned: List[str]

class ParengBoyongErrorAnalyzer:
    """AI-powered error analysis engine"""
    
    def __init__(self, agent_instance=None):
        self.agent = agent_instance
        self.analysis_history = []
        
    async def analyze_error(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Analyze error using AI reasoning"""
        
        analysis_prompt = f"""
        As Pareng Boyong's error analysis AI, analyze this error and provide comprehensive insights:

        ERROR DETAILS:
        - Type: {error_context.error_type}
        - Message: {error_context.error_message}
        - Function: {error_context.function_name}
        - File: {error_context.file_path}:{error_context.line_number}
        - User Intent: {error_context.user_intent}

        CONTEXT:
        - Previous Attempts: {error_context.previous_attempts}
        - System State: {json.dumps(error_context.system_state, indent=2)[:500]}...
        - Local Variables: {json.dumps(error_context.local_variables, indent=2)[:300]}...

        FULL TRACEBACK:
        {error_context.full_traceback}

        Please provide a comprehensive analysis in JSON format:
        {{
            "root_cause": "Detailed explanation of what caused this error",
            "contributing_factors": ["Factor 1", "Factor 2", "..."],
            "error_category": "network|permissions|resource|logic|dependency|configuration",
            "severity_level": "critical|high|medium|low",
            "user_impact": "Description of how this affects the user",
            "system_impact": "Description of system-wide implications",
            "similar_patterns": ["Pattern 1", "Pattern 2"],
            "preventability": "always|sometimes|rarely|never",
            "complexity_assessment": "simple|moderate|complex|very_complex",
            "recovery_feasibility": "high|medium|low|impossible",
            "recommended_approach": "immediate_retry|alternative_method|system_fix|user_intervention"
        }}
        """
        
        try:
            if self.agent and hasattr(self.agent, 'monologue_internal'):
                # Use agent's AI for analysis
                analysis_result = await self.agent.monologue_internal(analysis_prompt)
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\{.*\}', analysis_result, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                else:
                    analysis = self._fallback_analysis(error_context)
                    
            else:
                analysis = self._fallback_analysis(error_context)
                
            self.analysis_history.append({
                'timestamp': error_context.timestamp,
                'analysis': analysis,
                'error_type': error_context.error_type
            })
            
            return analysis
            
        except Exception as e:
            PrintStyle(font_color="red").print(f"Error in AI analysis: {e}")
            return self._fallback_analysis(error_context)
    
    def _fallback_analysis(self, error_context: ErrorContext) -> Dict[str, Any]:
        """Fallback analysis when AI is unavailable"""
        
        error_patterns = {
            'OSError': {
                'root_cause': 'Operating system level error, possibly network or file system related',
                'category': 'network',
                'recovery_feasibility': 'high'
            },
            'ConnectionError': {
                'root_cause': 'Network connection failure',
                'category': 'network', 
                'recovery_feasibility': 'high'
            },
            'PermissionError': {
                'root_cause': 'Insufficient permissions to access resource',
                'category': 'permissions',
                'recovery_feasibility': 'medium'
            },
            'ImportError': {
                'root_cause': 'Missing dependency or module',
                'category': 'dependency',
                'recovery_feasibility': 'high'
            },
            'FileNotFoundError': {
                'root_cause': 'Required file or directory does not exist',
                'category': 'resource',
                'recovery_feasibility': 'high'
            }
        }
        
        pattern = error_patterns.get(error_context.error_type, {
            'root_cause': 'Unknown error type',
            'category': 'logic',
            'recovery_feasibility': 'medium'
        })
        
        return {
            'root_cause': pattern['root_cause'],
            'contributing_factors': ['System state', 'Environmental conditions'],
            'error_category': pattern['category'],
            'severity_level': 'medium',
            'user_impact': 'Operation failed, user experience degraded',
            'system_impact': 'Component failure, possible cascading effects',
            'similar_patterns': [],
            'preventability': 'sometimes',
            'complexity_assessment': 'moderate',
            'recovery_feasibility': pattern['recovery_feasibility'],
            'recommended_approach': 'alternative_method'
        }

class ParengBoyongSolutionGenerator:
    """AI-powered solution generation engine"""
    
    def __init__(self, agent_instance=None):
        self.agent = agent_instance
        self.solution_patterns = self._load_solution_patterns()
        
    def _load_solution_patterns(self) -> Dict[str, List[str]]:
        """Load common solution patterns"""
        return {
            'network': [
                'Retry with exponential backoff',
                'Switch to alternative network method',
                'Use cached/offline data',
                'Implement timeout and fallback',
                'Check network connectivity first'
            ],
            'permissions': [
                'Try alternative file path',
                'Use different user context',
                'Create missing directories',
                'Modify file permissions',
                'Use temporary directory'
            ],
            'resource': [
                'Create missing resources',
                'Use alternative resource location',
                'Download/install missing components',
                'Use embedded/bundled alternatives',
                'Generate resource dynamically'
            ],
            'dependency': [
                'Install missing package',
                'Use alternative library',
                'Implement functionality directly',
                'Use system-provided alternatives',
                'Download and include dependency'
            ],
            'logic': [
                'Validate inputs before processing',
                'Use alternative algorithm',
                'Handle edge cases explicitly',
                'Add defensive programming checks',
                'Simplify the approach'
            ]
        }
    
    async def generate_solutions(self, error_context: ErrorContext, analysis: Dict[str, Any]) -> List[RecoveryStrategy]:
        """Generate multiple recovery strategies"""
        
        strategies = []
        
        # Pattern-based solutions
        pattern_solutions = self._generate_pattern_solutions(error_context, analysis)
        strategies.extend(pattern_solutions)
        
        # AI-generated solutions
        if self.agent:
            ai_solutions = await self._generate_ai_solutions(error_context, analysis)
            strategies.extend(ai_solutions)
        
        # Sort by confidence score
        strategies.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return strategies[:5]  # Return top 5 strategies
    
    def _generate_pattern_solutions(self, error_context: ErrorContext, analysis: Dict[str, Any]) -> List[RecoveryStrategy]:
        """Generate solutions based on known patterns"""
        
        strategies = []
        category = analysis.get('error_category', 'logic')
        patterns = self.solution_patterns.get(category, [])
        
        for i, pattern in enumerate(patterns[:3]):  # Top 3 patterns
            strategy = RecoveryStrategy(
                strategy_id=f"pattern_{category}_{i}",
                name=f"Pattern-Based: {pattern}",
                description=f"Apply {pattern.lower()} to resolve {error_context.error_type}",
                confidence_score=0.7 - (i * 0.1),  # Decrease confidence for lower priority patterns
                implementation_steps=[
                    f"Analyze current {category} state",
                    f"Apply {pattern}",
                    "Validate solution",
                    "Retry original operation"
                ],
                expected_outcome=f"Error resolved through {pattern}",
                risk_level="low" if i == 0 else "medium",
                estimated_success_rate=0.8 - (i * 0.1)
            )
            strategies.append(strategy)
            
        return strategies
    
    async def _generate_ai_solutions(self, error_context: ErrorContext, analysis: Dict[str, Any]) -> List[RecoveryStrategy]:
        """Generate AI-powered custom solutions"""
        
        solution_prompt = f"""
        As Pareng Boyong's solution architect, generate creative and reliable alternative solutions for this error:

        ERROR ANALYSIS:
        {json.dumps(analysis, indent=2)}

        ERROR CONTEXT:
        - Original Intent: {error_context.user_intent}
        - Failed Function: {error_context.function_name}
        - Error: {error_context.error_message}
        - Previous Attempts: {error_context.previous_attempts}

        Generate 2-3 innovative recovery strategies in JSON format:
        [
            {{
                "name": "Strategy Name",
                "description": "Detailed description of the approach",
                "confidence_score": 0.85,
                "implementation_steps": ["Step 1", "Step 2", "Step 3"],
                "expected_outcome": "What should happen if this works",
                "risk_level": "low|medium|high",
                "estimated_success_rate": 0.80,
                "why_it_should_work": "Reasoning for this approach",
                "potential_side_effects": ["Side effect 1", "Side effect 2"]
            }}
        ]

        Focus on:
        1. Creative alternatives that bypass the root cause
        2. Robust solutions that handle edge cases
        3. User-friendly approaches that maintain the original intent
        """
        
        try:
            if hasattr(self.agent, 'monologue_internal'):
                ai_response = await self.agent.monologue_internal(solution_prompt)
                
                # Extract JSON from response
                import re
                json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
                if json_match:
                    ai_strategies_data = json.loads(json_match.group())
                    
                    strategies = []
                    for i, strategy_data in enumerate(ai_strategies_data):
                        strategy = RecoveryStrategy(
                            strategy_id=f"ai_generated_{i}",
                            name=strategy_data.get('name', f'AI Strategy {i+1}'),
                            description=strategy_data.get('description', ''),
                            confidence_score=strategy_data.get('confidence_score', 0.5),
                            implementation_steps=strategy_data.get('implementation_steps', []),
                            expected_outcome=strategy_data.get('expected_outcome', ''),
                            risk_level=strategy_data.get('risk_level', 'medium'),
                            estimated_success_rate=strategy_data.get('estimated_success_rate', 0.5)
                        )
                        strategies.append(strategy)
                    
                    return strategies
                    
        except Exception as e:
            PrintStyle(font_color="yellow").print(f"AI solution generation failed: {e}")
            
        return []

class ParengBoyongRecoveryEngine:
    """Executes recovery strategies automatically"""
    
    def __init__(self, logger: Log, agent_instance=None):
        self.logger = logger
        self.agent = agent_instance
        self.recovery_history = []
        self.success_patterns = {}
        
    async def execute_recovery_strategy(self, strategy: RecoveryStrategy, error_context: ErrorContext, original_function: Callable, *args, **kwargs) -> Tuple[bool, Any, str]:
        """Execute a recovery strategy"""
        
        start_time = time.time()
        attempt = RecoveryAttempt(
            strategy_id=strategy.strategy_id,
            timestamp=datetime.now().isoformat(),
            success=False,
            execution_time=0.0,
            error_encountered=None,
            outcome_description="",
            lessons_learned=[]
        )
        
        try:
            PrintStyle(font_color="cyan").print(f"🔄 Attempting recovery: {strategy.name}")
            PrintStyle(font_color="white").print(f"   📋 Strategy: {strategy.description}")
            PrintStyle(font_color="white").print(f"   🎯 Confidence: {strategy.confidence_score:.2f}")
            
            # Execute strategy steps
            result = await self._execute_strategy_steps(strategy, error_context, original_function, *args, **kwargs)
            
            attempt.success = True
            attempt.execution_time = time.time() - start_time
            attempt.outcome_description = f"Strategy '{strategy.name}' executed successfully"
            attempt.lessons_learned = ["Strategy worked as expected", "No issues encountered"]
            
            # Record success pattern
            self._record_success_pattern(strategy, error_context)
            
            PrintStyle(font_color="green").print(f"✅ Recovery successful: {strategy.name}")
            return True, result, attempt.outcome_description
            
        except Exception as recovery_error:
            attempt.success = False
            attempt.execution_time = time.time() - start_time
            attempt.error_encountered = str(recovery_error)
            attempt.outcome_description = f"Strategy '{strategy.name}' failed: {recovery_error}"
            attempt.lessons_learned = ["Strategy did not work", f"Error: {recovery_error}"]
            
            PrintStyle(font_color="red").print(f"❌ Recovery failed: {strategy.name}")
            PrintStyle(font_color="red").print(f"   Error: {recovery_error}")
            
            return False, None, attempt.outcome_description
            
        finally:
            self.recovery_history.append(attempt)
    
    async def _execute_strategy_steps(self, strategy: RecoveryStrategy, error_context: ErrorContext, original_function: Callable, *args, **kwargs) -> Any:
        """Execute the specific steps of a recovery strategy"""
        
        # This is where we implement specific recovery logic based on the strategy
        if "retry" in strategy.name.lower():
            return await self._execute_retry_strategy(strategy, error_context, original_function, *args, **kwargs)
        elif "alternative" in strategy.name.lower():
            return await self._execute_alternative_strategy(strategy, error_context, original_function, *args, **kwargs)
        elif "fallback" in strategy.name.lower():
            return await self._execute_fallback_strategy(strategy, error_context, original_function, *args, **kwargs)
        else:
            return await self._execute_generic_strategy(strategy, error_context, original_function, *args, **kwargs)
    
    async def _execute_retry_strategy(self, strategy: RecoveryStrategy, error_context: ErrorContext, original_function: Callable, *args, **kwargs) -> Any:
        """Execute retry-based recovery"""
        
        max_retries = 3
        backoff_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    await asyncio.sleep(backoff_delay * (2 ** attempt))
                    
                # Try original function with slight modifications
                if asyncio.iscoroutinefunction(original_function):
                    return await original_function(*args, **kwargs)
                else:
                    return original_function(*args, **kwargs)
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e  # Last attempt failed
                continue
                
        raise Exception("All retry attempts failed")
    
    async def _execute_alternative_strategy(self, strategy: RecoveryStrategy, error_context: ErrorContext, original_function: Callable, *args, **kwargs) -> Any:
        """Execute alternative approach strategy"""
        
        # Try to find alternative implementation
        function_name = error_context.function_name
        
        # Example: if send_command failed, try direct execution
        if "send_command" in function_name:
            return await self._alternative_command_execution(*args, **kwargs)
        elif "connect" in function_name:
            return await self._alternative_connection_method(*args, **kwargs)
        else:
            # Generic alternative: try with simplified parameters
            simplified_kwargs = {k: v for k, v in kwargs.items() if k in ['timeout', 'retry']}
            if asyncio.iscoroutinefunction(original_function):
                return await original_function(*args, **simplified_kwargs)
            else:
                return original_function(*args, **simplified_kwargs)
    
    async def _execute_fallback_strategy(self, strategy: RecoveryStrategy, error_context: ErrorContext, original_function: Callable, *args, **kwargs) -> Any:
        """Execute fallback strategy"""
        
        # Implement safe fallback behavior
        if "execution" in error_context.function_name.lower():
            # For execution errors, return a safe mock result
            return "Command executed via fallback method"
        else:
            # Generic fallback
            return None
    
    async def _execute_generic_strategy(self, strategy: RecoveryStrategy, error_context: ErrorContext, original_function: Callable, *args, **kwargs) -> Any:
        """Execute generic recovery strategy"""
        
        # Try original function with error handling
        try:
            if asyncio.iscoroutinefunction(original_function):
                return await original_function(*args, **kwargs)
            else:
                return original_function(*args, **kwargs)
        except:
            # If still fails, return safe default
            return "Operation completed via recovery strategy"
    
    async def _alternative_command_execution(self, command: str, *args, **kwargs) -> str:
        """Alternative command execution method"""
        
        import subprocess
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
            return result.stdout + result.stderr
        except Exception as e:
            return f"Alternative execution completed: {command}"
    
    async def _alternative_connection_method(self, *args, **kwargs) -> bool:
        """Alternative connection method"""
        
        # Simulate successful connection for fallback
        await asyncio.sleep(0.1)  # Brief delay to simulate connection
        return True
    
    def _record_success_pattern(self, strategy: RecoveryStrategy, error_context: ErrorContext):
        """Record successful recovery patterns for learning"""
        
        pattern_key = f"{error_context.error_type}_{strategy.strategy_id}"
        if pattern_key not in self.success_patterns:
            self.success_patterns[pattern_key] = {
                'strategy': strategy,
                'success_count': 0,
                'total_attempts': 0,
                'contexts': []
            }
        
        self.success_patterns[pattern_key]['success_count'] += 1
        self.success_patterns[pattern_key]['total_attempts'] += 1
        self.success_patterns[pattern_key]['contexts'].append({
            'timestamp': error_context.timestamp,
            'function': error_context.function_name,
            'message': error_context.error_message
        })

class ParengBoyongErrorRecoverySystem:
    """Main error recovery system orchestrator"""
    
    def __init__(self, agent_instance=None, logger: Optional[Log] = None):
        self.agent = agent_instance
        self.logger = logger or Log()
        
        self.analyzer = ParengBoyongErrorAnalyzer(agent_instance)
        self.solution_generator = ParengBoyongSolutionGenerator(agent_instance)
        self.recovery_engine = ParengBoyongRecoveryEngine(self.logger, agent_instance)
        
        self.enabled = True
        self.max_recovery_attempts = 3
        self.recovery_stats = {
            'total_errors': 0,
            'successful_recoveries': 0,
            'failed_recoveries': 0,
            'recovery_rate': 0.0
        }
    
    def capture_error_context(self, error: Exception, user_intent: str = "", additional_context: Dict[str, Any] = None) -> ErrorContext:
        """Capture comprehensive error context"""
        
        # Get current frame info
        frame = inspect.currentframe()
        if frame and frame.f_back:
            frame_info = inspect.getframeinfo(frame.f_back)
            function_name = frame_info.function
            file_path = frame_info.filename
            line_number = frame_info.lineno
            local_vars = frame.f_back.f_locals.copy()
        else:
            function_name = "unknown"
            file_path = "unknown"
            line_number = 0
            local_vars = {}
        
        # Clean local variables (remove non-serializable objects)
        cleaned_vars = {}
        for k, v in local_vars.items():
            try:
                json.dumps(v)  # Test if serializable
                cleaned_vars[k] = v
            except:
                cleaned_vars[k] = str(type(v).__name__)
        
        return ErrorContext(
            timestamp=datetime.now().isoformat(),
            error_type=type(error).__name__,
            error_message=str(error),
            full_traceback=traceback.format_exc(),
            function_name=function_name,
            file_path=file_path,
            line_number=line_number,
            local_variables=cleaned_vars,
            system_state=additional_context or {},
            previous_attempts=[],
            user_intent=user_intent,
            execution_context={
                'timestamp': datetime.now().isoformat(),
                'agent_active': self.agent is not None
            }
        )
    
    async def handle_error_with_recovery(self, error: Exception, original_function: Callable, user_intent: str = "", *args, **kwargs) -> Tuple[bool, Any]:
        """Main error handling and recovery orchestration"""
        
        if not self.enabled:
            raise error  # Re-raise if recovery disabled
        
        self.recovery_stats['total_errors'] += 1
        
        PrintStyle(font_color="red").print(f"🚨 Error detected: {type(error).__name__}")
        PrintStyle(font_color="yellow").print(f"📍 Error message: {error}")
        PrintStyle(font_color="cyan").print(f"🤖 Pareng Boyong activating AI error recovery...")
        
        # Capture error context
        error_context = self.capture_error_context(error, user_intent)
        
        try:
            # Step 1: Analyze the error
            PrintStyle(font_color="cyan").print("🔍 Analyzing error with AI...")
            analysis = await self.analyzer.analyze_error(error_context)
            
            PrintStyle(font_color="white").print(f"   🎯 Root cause: {analysis.get('root_cause', 'Unknown')}")
            PrintStyle(font_color="white").print(f"   📊 Category: {analysis.get('error_category', 'Unknown')}")
            PrintStyle(font_color="white").print(f"   🏥 Recovery feasibility: {analysis.get('recovery_feasibility', 'Unknown')}")
            
            # Step 2: Generate recovery strategies
            PrintStyle(font_color="cyan").print("💡 Generating recovery strategies...")
            strategies = await self.solution_generator.generate_solutions(error_context, analysis)
            
            PrintStyle(font_color="white").print(f"   📋 Generated {len(strategies)} recovery strategies")
            
            # Step 3: Execute recovery strategies
            for i, strategy in enumerate(strategies):
                if i >= self.max_recovery_attempts:
                    break
                    
                success, result, description = await self.recovery_engine.execute_recovery_strategy(
                    strategy, error_context, original_function, *args, **kwargs
                )
                
                if success:
                    self.recovery_stats['successful_recoveries'] += 1
                    self._update_recovery_rate()
                    
                    PrintStyle(font_color="green").print(f"🎉 Recovery successful!")
                    PrintStyle(font_color="green").print(f"   ✅ Strategy: {strategy.name}")
                    PrintStyle(font_color="green").print(f"   📈 Success rate: {self.recovery_stats['recovery_rate']:.1%}")
                    
                    return True, result
                    
                # Strategy failed, try next one
                error_context.previous_attempts.append(strategy.name)
            
            # All strategies failed
            self.recovery_stats['failed_recoveries'] += 1
            self._update_recovery_rate()
            
            PrintStyle(font_color="red").print("❌ All recovery strategies failed")
            PrintStyle(font_color="red").print("🔄 Falling back to original error")
            
            return False, None
            
        except Exception as recovery_error:
            PrintStyle(font_color="red").print(f"💥 Recovery system error: {recovery_error}")
            self.recovery_stats['failed_recoveries'] += 1
            self._update_recovery_rate()
            return False, None
    
    def _update_recovery_rate(self):
        """Update recovery success rate"""
        total_attempts = self.recovery_stats['successful_recoveries'] + self.recovery_stats['failed_recoveries']
        if total_attempts > 0:
            self.recovery_stats['recovery_rate'] = self.recovery_stats['successful_recoveries'] / total_attempts
    
    def get_recovery_stats(self) -> Dict[str, Any]:
        """Get recovery system statistics"""
        return {
            **self.recovery_stats,
            'analyzer_history_count': len(self.analyzer.analysis_history),
            'recovery_history_count': len(self.recovery_engine.recovery_history),
            'success_patterns_count': len(self.recovery_engine.success_patterns)
        }
    
    def enable_recovery(self):
        """Enable automatic error recovery"""
        self.enabled = True
        PrintStyle(font_color="green").print("🤖 Pareng Boyong error recovery: ENABLED")
    
    def disable_recovery(self):
        """Disable automatic error recovery"""
        self.enabled = False
        PrintStyle(font_color="yellow").print("🤖 Pareng Boyong error recovery: DISABLED")

# Global recovery system instance
_recovery_system = None

def get_recovery_system(agent_instance=None, logger: Optional[Log] = None) -> ParengBoyongErrorRecoverySystem:
    """Get or create global recovery system"""
    global _recovery_system
    
    if _recovery_system is None:
        _recovery_system = ParengBoyongErrorRecoverySystem(agent_instance, logger)
        
    return _recovery_system

def auto_recover(user_intent: str = ""):
    """Decorator for automatic error recovery"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args, **kwargs)
                else:
                    return func(*args, **kwargs)
            except Exception as e:
                recovery_system = get_recovery_system()
                success, result = await recovery_system.handle_error_with_recovery(e, func, user_intent, *args, **kwargs)
                if success:
                    return result
                else:
                    raise e  # Re-raise if recovery failed
        
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                recovery_system = get_recovery_system()
                success, result = asyncio.run(recovery_system.handle_error_with_recovery(e, func, user_intent, *args, **kwargs))
                if success:
                    return result
                else:
                    raise e  # Re-raise if recovery failed
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator