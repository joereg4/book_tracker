from flask import Blueprint, jsonify, render_template
from flask_login import login_required
from extensions import limiter
from datetime import datetime, UTC, timedelta
import redis
import json
from utils.decorators import admin_required

# Create a dummy client that does nothing but doesn't break the app
class DummyRedis:
    def __getattr__(self, name):
        return lambda *args, **kwargs: None if 'get' in name else {}

bp = Blueprint('monitoring', __name__, url_prefix='/monitoring')

# Try to connect to Redis, fall back to a dummy client if not available
try:
    redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    redis_client.ping()  # Test the connection
except (redis.ConnectionError, redis.RedisError):
    redis_client = DummyRedis()

def record_rate_limit_hit(endpoint, user_ip):
    """Record a rate limit hit in Redis"""
    try:
        now = datetime.now(UTC)
        day_key = f"rate_limits:{endpoint}:{now.strftime('%Y-%m-%d')}"
        hour_key = f"rate_limits:{endpoint}:{now.strftime('%Y-%m-%d:%H')}"
        
        # Only try to record if we have a real Redis connection
        if not isinstance(redis_client, DummyRedis):
            # Increment counters
            redis_client.hincrby(day_key, user_ip, 1)
            redis_client.hincrby(hour_key, user_ip, 1)
            
            # Set expiry (keep daily data for 30 days, hourly for 48 hours)
            redis_client.expire(day_key, 60 * 60 * 24 * 30)
            redis_client.expire(hour_key, 60 * 60 * 48)
    except redis.RedisError:
        # Log error but don't fail the request
        print(f"Error recording rate limit hit: {endpoint} - {user_ip}")

@bp.route('/rate-limits')
@login_required
@admin_required
def rate_limits_dashboard():
    """Dashboard showing rate limit metrics"""
    # Get current limits from decorators
    current_limits = {
        'login': '5 per minute',  # From auth.py login route
        'book_search': '30 per minute'  # From books.py search route
    }
    
    try:
        if isinstance(redis_client, DummyRedis):
            today_hits = {}
            hourly_stats = {}
        else:
            # Get today's stats
            today = datetime.now(UTC).strftime('%Y-%m-%d')
            today_key = f"rate_limits:login:{today}"
            today_hits = redis_client.hgetall(today_key) or {}
            
            # Get hourly stats for the past 24 hours
            hourly_stats = {}
            now = datetime.now(UTC)
            for i in range(24):
                hour = now - timedelta(hours=i)
                hour_key = f"rate_limits:login:{hour.strftime('%Y-%m-%d:%H')}"
                hour_hits = redis_client.hgetall(hour_key) or {}
                if hour_hits:
                    hourly_stats[hour.strftime('%Y-%m-%d %H:00')] = hour_hits
    except redis.RedisError:
        # Return empty stats on Redis error
        today_hits = {}
        hourly_stats = {}
    
    return render_template('monitoring/rate_limits.html',
                         current_limits=current_limits,
                         today_hits=today_hits,
                         hourly_stats=hourly_stats)

@bp.route('/api/rate-limits')
@login_required
@admin_required
def rate_limits_api():
    """API endpoint for rate limit metrics"""
    today = datetime.now(UTC).strftime('%Y-%m-%d')
    endpoints = ['login', 'book_search']
    
    try:
        if isinstance(redis_client, DummyRedis):
            metrics = {endpoint: {
                'today_total': 0,
                'current_hour': 0,
                'unique_ips_today': 0,
                'today_hits': {},
                'hourly_stats': {}
            } for endpoint in endpoints}
        else:
            metrics = {}
            for endpoint in endpoints:
                day_key = f"rate_limits:{endpoint}:{today}"
                hour_key = f"rate_limits:{endpoint}:{datetime.now(UTC).strftime('%Y-%m-%d:%H')}"
                
                day_hits = redis_client.hgetall(day_key) or {}
                hour_hits = redis_client.hgetall(hour_key) or {}
                
                metrics[endpoint] = {
                    'today_total': sum(int(v) for v in day_hits.values()),
                    'current_hour': sum(int(v) for v in hour_hits.values()),
                    'unique_ips_today': len(day_hits),
                    'today_hits': day_hits,
                    'hourly_stats': hour_hits
                }
    except redis.RedisError:
        # Return empty metrics on Redis error
        metrics = {endpoint: {
            'today_total': 0,
            'current_hour': 0,
            'unique_ips_today': 0,
            'today_hits': {},
            'hourly_stats': {}
        } for endpoint in endpoints}
    
    return jsonify(metrics) 