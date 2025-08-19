**model_discovery** - Advanced AI model discovery system that finds and recommends models from 5+ providers (OpenAI, Anthropic, Groq, OpenRouter, Ollama). Use when users need model recommendations or want to explore available AI models. Parameters: operation (discover/search/recommend/validate), provider, query, use_case, budget_level.

**enhanced_model_configuration** - Comprehensive model management system with intelligent recommendations, backup/rollback, and real-time validation. Use for model configuration changes, performance testing, or when users want to optimize their AI setup. Parameters: operation (recommend/backup/rollback/validate/test_model/apply/status), provider, model, backup_id.

**Key Model Configuration Operations:**
- **discover**: Find all available models from providers
- **recommend**: Get AI-powered model suggestions based on use case and budget
- **backup**: Create safety backup before configuration changes
- **validate**: Test current model configuration
- **rollback**: Restore previous configuration if issues occur
- **apply**: Safely implement new model settings

**Usage Examples:**
- User wants better coding model → use model_discovery with use_case=coding
- User experiencing model issues → use enhanced_model_configuration with operation=rollback
- User wants maximum success rate → use model_discovery with budget_level=premium
- Testing new model → use enhanced_model_configuration with operation=test_model

**Success-First Model Recommendations:**
- **Primary Chat**: claude-3-5-sonnet (best reasoning and coding)
- **Vision Tasks**: claude-3-5-sonnet (superior image understanding)
- **Complex Analysis**: claude-3-5-sonnet (highest accuracy)
- **Multimodal**: gpt-4o (comprehensive multimedia support)
- **Backup**: claude-3-opus (premium fallback option)

**Success Philosophy**: Always choose the model most likely to complete the task successfully, regardless of cost difference.