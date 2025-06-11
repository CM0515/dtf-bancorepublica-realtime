from flask import render_template, jsonify, request
from app import app
from models import TasaDTF
from dtf_collector import collect_dtf_data, get_collection_status
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        # Get latest 30 DTF rates for the chart
        latest_rates = TasaDTF.get_latest(30)
        
        # Get collection status
        status = get_collection_status()
        
        # Calculate some basic statistics
        if latest_rates:
            rates_values = [rate.tasa for rate in latest_rates]
            current_rate = latest_rates[0].tasa if latest_rates else 0
            avg_rate = sum(rates_values) / len(rates_values)
            max_rate = max(rates_values)
            min_rate = min(rates_values)
            
            # Calculate trend (last 7 days vs previous 7 days)
            if len(latest_rates) >= 14:
                recent_avg = sum(rates_values[:7]) / 7
                previous_avg = sum(rates_values[7:14]) / 7
                trend = "up" if recent_avg > previous_avg else "down" if recent_avg < previous_avg else "stable"
            else:
                trend = "stable"
        else:
            current_rate = avg_rate = max_rate = min_rate = 0
            trend = "stable"
        
        stats = {
            'current_rate': round(current_rate, 4),
            'avg_rate': round(avg_rate, 4),
            'max_rate': round(max_rate, 4),
            'min_rate': round(min_rate, 4),
            'trend': trend,
            'total_records': status['total_records'],
            'latest_date': status['latest_date']
        }
        
        return render_template('index.html', 
                             latest_rates=latest_rates,
                             stats=stats,
                             status=status)
    
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        return render_template('index.html', 
                             latest_rates=[],
                             stats={},
                             status={},
                             error="Error loading DTF data")

@app.route('/api/dtf/latest/<int:limit>')
def api_latest_dtf(limit=30):
    """API endpoint to get latest DTF rates"""
    try:
        if limit > 365:  # Limit to 1 year of data
            limit = 365
            
        rates = TasaDTF.get_latest(limit)
        return jsonify({
            'success': True,
            'data': [rate.to_dict() for rate in rates],
            'count': len(rates)
        })
    except Exception as e:
        logger.error(f"Error in API latest DTF: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dtf/all')
def api_all_dtf():
    """API endpoint to get all DTF rates"""
    try:
        rates = TasaDTF.get_all_ordered()
        return jsonify({
            'success': True,
            'data': [rate.to_dict() for rate in rates],
            'count': len(rates)
        })
    except Exception as e:
        logger.error(f"Error in API all DTF: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dtf/collect', methods=['POST'])
def api_collect_dtf():
    """API endpoint to manually trigger DTF data collection"""
    try:
        success = collect_dtf_data()
        if success:
            return jsonify({
                'success': True,
                'message': 'DTF data collection completed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'DTF data collection failed'
            }), 500
    except Exception as e:
        logger.error(f"Error in manual DTF collection: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/dtf/status')
def api_dtf_status():
    """API endpoint to get DTF collection status"""
    try:
        status = get_collection_status()
        return jsonify({
            'success': True,
            'status': status
        })
    except Exception as e:
        logger.error(f"Error getting DTF status: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/table')
def dtf_table():
    """Page with complete DTF data table"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        # Limit per_page to reasonable values
        if per_page > 200:
            per_page = 200
        
        # Get paginated results
        rates_query = TasaDTF.query.order_by(TasaDTF.fecha.desc())
        rates_paginated = rates_query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return render_template('table.html', 
                             rates=rates_paginated.items,
                             pagination=rates_paginated)
    
    except Exception as e:
        logger.error(f"Error in table route: {e}")
        return render_template('table.html', 
                             rates=[],
                             pagination=None,
                             error="Error loading DTF data table")

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return render_template('500.html'), 500
