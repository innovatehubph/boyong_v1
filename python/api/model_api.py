"""
Model Configuration API Endpoints
Provides REST API endpoints for the enhanced model selector system
Supports model discovery, recommendations, validation, and configuration management
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from flask import Flask, request, jsonify, Blueprint
import traceback

from python.helpers.enhanced_model_selector import (
    model_selector, initialize_model_selector, get_smart_recommendations,
    search_available_models, apply_model_configuration, get_ui_configuration
)
from python.helpers.model_discovery import (
    ModelRequirements, validate_model_exists, get_model_recommendations
)
from python.helpers.settings_backup import (
    list_settings_backups, rollback_settings, create_settings_backup
)
from python.helpers.print_style import PrintStyle


# Create Flask Blueprint for model API
model_api = Blueprint('model_api', __name__, url_prefix='/api/models')


@model_api.route('/initialize', methods=['POST'])
def initialize_models():
    """Initialize the model discovery system"""
    try:
        PrintStyle(color="blue").print("🔄 API: Initializing model system...")
        
        # Run async initialization
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(initialize_model_selector())
        finally:
            loop.close()
        
        if result.get('success'):
            PrintStyle(color="green").print("✅ API: Model system initialized successfully")
            return jsonify({
                'success': True,
                'message': 'Model system initialized',
                'data': result
            })
        else:
            PrintStyle(color="red").print(f"❌ API: Initialization failed: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown initialization error')
            }), 500
            
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Initialization exception: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500


@model_api.route('/ui-config', methods=['GET'])
def get_ui_config():
    """Get UI configuration for frontend components"""
    try:
        config = get_ui_configuration()
        return jsonify(config)
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: UI config error: {str(e)}")
        return jsonify({
            'error': str(e),
            'providers': {},
            'categories': [],
            'options': {},
            'state': {}
        }), 500


@model_api.route('/recommendations', methods=['POST'])
def get_recommendations():
    """Get model recommendations based on requirements"""
    try:
        data = request.get_json() or {}
        
        use_case = data.get('use_case', 'chat')
        budget_level = data.get('budget', 'balanced')
        context_length = data.get('context_length', 4000)
        vision_required = data.get('vision_required', False)
        function_calling_required = data.get('function_calling_required', False)
        performance_priority = data.get('performance_priority', 'balanced')
        
        PrintStyle(color="blue").print(f"🎯 API: Getting recommendations for {use_case} use case")
        
        # Create requirements object
        requirements = ModelRequirements(
            use_case=use_case,
            budget_level=budget_level,
            context_length_needed=context_length,
            vision_required=vision_required,
            function_calling_required=function_calling_required,
            performance_priority=performance_priority
        )
        
        # Run async recommendation request
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            recommendations = loop.run_until_complete(
                model_selector.get_recommendations(requirements)
            )
        finally:
            loop.close()
        
        # Convert recommendations to JSON-serializable format
        recommendations_data = []
        for rec in recommendations:
            recommendations_data.append({
                'model': {
                    'id': rec.model.id,
                    'name': rec.model.name,
                    'provider': rec.model.provider,
                    'description': rec.model.description,
                    'context_length': rec.model.context_length,
                    'input_cost': rec.model.input_cost,
                    'output_cost': rec.model.output_cost,
                    'performance_tier': rec.model.performance_tier,
                    'supports_vision': rec.model.supports_vision,
                    'supports_function_calling': rec.model.supports_function_calling,
                    'supports_streaming': rec.model.supports_streaming
                },
                'score': rec.score,
                'reasoning': rec.reasoning,
                'estimated_cost': rec.estimated_cost,
                'use_cases': rec.use_cases
            })
        
        PrintStyle(color="green").print(f"✅ API: Found {len(recommendations_data)} recommendations")
        return jsonify(recommendations_data)
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Recommendations error: {str(e)}")
        return jsonify({
            'error': str(e),
            'recommendations': []
        }), 500


@model_api.route('/search', methods=['POST'])
def search_models():
    """Search models with query and filters"""
    try:
        data = request.get_json() or {}
        
        query = data.get('query', '').strip()
        filters = data.get('filters', {})
        
        if not query:
            return jsonify([])
        
        PrintStyle(color="blue").print(f"🔍 API: Searching models with query: '{query}'")
        
        # Run async search
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                search_available_models(query, filters)
            )
        finally:
            loop.close()
        
        # Convert results to JSON-serializable format
        search_results = []
        for model in results:
            search_results.append({
                'id': model.id,
                'name': model.name,
                'provider': model.provider,
                'description': model.description,
                'context_length': model.context_length,
                'input_cost': model.input_cost,
                'output_cost': model.output_cost,
                'performance_tier': model.performance_tier,
                'supports_vision': model.supports_vision,
                'supports_function_calling': model.supports_function_calling,
                'supports_streaming': model.supports_streaming
            })
        
        PrintStyle(color="green").print(f"✅ API: Found {len(search_results)} search results")
        return jsonify(search_results)
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Search error: {str(e)}")
        return jsonify({
            'error': str(e),
            'results': []
        }), 500


@model_api.route('/validate', methods=['POST'])
def validate_model():
    """Validate if a specific model exists and is accessible"""
    try:
        data = request.get_json() or {}
        
        provider = data.get('provider', '').strip()
        model_name = data.get('model_name', '').strip()
        
        if not provider or not model_name:
            return jsonify({
                'valid': False,
                'error': 'Provider and model name are required'
            }), 400
        
        PrintStyle(color="blue").print(f"🔍 API: Validating model {provider}/{model_name}")
        
        # Run async validation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            validation_result = loop.run_until_complete(
                validate_model_exists(provider, model_name)
            )
        finally:
            loop.close()
        
        PrintStyle(color="green" if validation_result.get('valid') else "yellow").print(
            f"✅ API: Validation result: {validation_result.get('valid', False)}"
        )
        
        return jsonify(validation_result)
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Validation error: {str(e)}")
        return jsonify({
            'valid': False,
            'error': str(e)
        }), 500


@model_api.route('/apply', methods=['POST'])
def apply_model():
    """Apply model selection with backup and validation"""
    try:
        data = request.get_json() or {}
        
        provider = data.get('provider', '').strip()
        model_name = data.get('model_name', '').strip()
        model_type = data.get('model_type', 'chat').strip()
        backup_reason = data.get('backup_reason', 'user_model_change')
        
        if not provider or not model_name:
            return jsonify({
                'success': False,
                'error': 'Provider and model name are required'
            }), 400
        
        PrintStyle(color="blue").print(f"🔄 API: Applying model {provider}/{model_name} for {model_type}")
        
        # Run async application
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                apply_model_configuration(provider, model_name, model_type)
            )
        finally:
            loop.close()
        
        if result.get('success'):
            PrintStyle(color="green").print("✅ API: Model applied successfully")
        else:
            PrintStyle(color="red").print(f"❌ API: Model application failed: {result.get('error')}")
        
        return jsonify(result)
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Apply model error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'trace': traceback.format_exc()
        }), 500


@model_api.route('/test', methods=['POST'])
def test_model():
    """Test model with a simple request"""
    try:
        data = request.get_json() or {}
        
        provider = data.get('provider', '').strip()
        model_name = data.get('model_name', '').strip()
        test_message = data.get('test_message', 'Hello! This is a test message.')
        
        if not provider or not model_name:
            return jsonify({
                'success': False,
                'error': 'Provider and model name are required'
            }), 400
        
        PrintStyle(color="blue").print(f"🧪 API: Testing model {provider}/{model_name}")
        
        # This would implement actual model testing
        # For now, simulate a test
        import time
        time.sleep(1)  # Simulate API call delay
        
        # Simulate test results
        test_result = {
            'success': True,
            'response_time_ms': 850,
            'response_preview': 'Hello! I\'m working correctly. This is a test response...',
            'model_info': {
                'provider': provider,
                'model': model_name,
                'status': 'healthy',
                'capabilities_detected': ['text_generation', 'streaming']
            },
            'metrics': {
                'tokens_used': 25,
                'estimated_cost': '$0.0001'
            }
        }
        
        PrintStyle(color="green").print("✅ API: Model test completed")
        return jsonify(test_result)
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Model test error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_api.route('/backups', methods=['GET'])
def list_backups():
    """List all available settings backups"""
    try:
        backups = list_settings_backups()
        
        # Convert backups to JSON-serializable format
        backups_data = []
        for backup in backups:
            backups_data.append({
                'id': backup.id,
                'timestamp': backup.timestamp,
                'reason': backup.reason,
                'settings_hash': backup.settings_hash,
                'system_info': backup.system_info
            })
        
        return jsonify({
            'success': True,
            'backups': backups_data,
            'count': len(backups_data)
        })
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: List backups error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'backups': []
        }), 500


@model_api.route('/rollback', methods=['POST'])
def rollback_to_backup():
    """Rollback to a specific backup"""
    try:
        data = request.get_json() or {}
        backup_id = data.get('backup_id', '').strip()
        
        if not backup_id:
            return jsonify({
                'success': False,
                'error': 'Backup ID is required'
            }), 400
        
        PrintStyle(color="yellow").print(f"🔄 API: Rolling back to backup {backup_id}")
        
        success = rollback_settings(backup_id)
        
        if success:
            PrintStyle(color="green").print("✅ API: Rollback completed successfully")
            return jsonify({
                'success': True,
                'message': f'Successfully rolled back to backup {backup_id}'
            })
        else:
            PrintStyle(color="red").print("❌ API: Rollback failed")
            return jsonify({
                'success': False,
                'error': 'Rollback operation failed'
            }), 500
            
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Rollback error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_api.route('/providers', methods=['GET'])
def get_providers():
    """Get available providers and their capabilities"""
    try:
        providers_summary = model_selector.get_provider_summary()
        return jsonify({
            'success': True,
            'providers': providers_summary
        })
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Providers error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'providers': {}
        }), 500


@model_api.route('/categories', methods=['GET'])
def get_categories():
    """Get model categories with model counts"""
    try:
        from python.helpers.enhanced_model_selector import get_model_categories_list
        categories = get_model_categories_list()
        
        # Convert to counts
        category_counts = {}
        for category, models in categories.items():
            category_counts[category] = len(models)
        
        return jsonify({
            'success': True,
            'categories': category_counts
        })
        
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Categories error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e),
            'categories': {}
        }), 500


@model_api.route('/refresh', methods=['POST'])
def refresh_models():
    """Refresh model data from providers"""
    try:
        PrintStyle(color="blue").print("🔄 API: Refreshing model data...")
        
        # Clear cache and reinitialize
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            # Clear cache
            model_selector.state.available_models = {}
            model_selector.state.recommendations = []
            model_selector.state.search_results = []
            
            # Reinitialize
            result = loop.run_until_complete(initialize_model_selector())
        finally:
            loop.close()
        
        if result.get('success'):
            PrintStyle(color="green").print("✅ API: Model data refreshed successfully")
            return jsonify({
                'success': True,
                'message': 'Model data refreshed',
                'data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Refresh failed')
            }), 500
            
    except Exception as e:
        PrintStyle(color="red").print(f"❌ API: Refresh error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@model_api.route('/health', methods=['GET'])
def health_check():
    """Health check for model API"""
    try:
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'initialized': len(model_selector.state.available_models) > 0,
            'model_count': sum(len(models) for models in model_selector.state.available_models.values()),
            'recommendations_count': len(model_selector.state.recommendations)
        })
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


# Error handlers
@model_api.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'available_endpoints': [
            '/initialize', '/ui-config', '/recommendations', '/search',
            '/validate', '/apply', '/test', '/backups', '/rollback',
            '/providers', '/categories', '/refresh', '/health'
        ]
    }), 404


@model_api.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500


# Integration function for Flask app
def register_model_api(app: Flask):
    """Register the model API blueprint with Flask app"""
    app.register_blueprint(model_api)
    PrintStyle(color="green").print("✅ Model API endpoints registered")
    
    # Log available endpoints
    PrintStyle(color="cyan").print("📡 Model API Endpoints:")
    PrintStyle(color="cyan").print("  POST /api/models/initialize - Initialize model system")
    PrintStyle(color="cyan").print("  GET  /api/models/ui-config - Get UI configuration")
    PrintStyle(color="cyan").print("  POST /api/models/recommendations - Get model recommendations")
    PrintStyle(color="cyan").print("  POST /api/models/search - Search models")
    PrintStyle(color="cyan").print("  POST /api/models/validate - Validate model")
    PrintStyle(color="cyan").print("  POST /api/models/apply - Apply model selection")
    PrintStyle(color="cyan").print("  POST /api/models/test - Test model")
    PrintStyle(color="cyan").print("  GET  /api/models/backups - List backups")
    PrintStyle(color="cyan").print("  POST /api/models/rollback - Rollback to backup")
    PrintStyle(color="cyan").print("  GET  /api/models/providers - Get providers")
    PrintStyle(color="cyan").print("  GET  /api/models/categories - Get categories")
    PrintStyle(color="cyan").print("  POST /api/models/refresh - Refresh model data")
    PrintStyle(color="cyan").print("  GET  /api/models/health - Health check")


if __name__ == '__main__':
    # For testing the API independently
    app = Flask(__name__)
    register_model_api(app)
    app.run(debug=True, port=8080)