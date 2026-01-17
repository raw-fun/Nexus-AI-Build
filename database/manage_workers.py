#!/usr/bin/env python3
"""
Worker Management Utility for NADG
Helps manage workers in Supabase database
"""

import os
import sys
from supabase import create_client
from datetime import datetime

def get_supabase_client():
    """Initialize Supabase client from environment variables"""
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set")
        print("   Export them as environment variables or add to .env file")
        sys.exit(1)
    
    return create_client(url, key)


def list_workers():
    """List all workers in the database"""
    supabase = get_supabase_client()
    response = supabase.table('worker_nodes').select('*').execute()
    
    workers = response.data
    if not workers:
        print("📭 No workers found in database")
        return
    
    print(f"\n📋 Found {len(workers)} worker(s):\n")
    print(f"{'ID':<5} {'Status':<10} {'Tasks':<8} {'Last Ping':<25} {'URL'}")
    print("-" * 100)
    
    for w in workers:
        print(f"{w['id']:<5} {w['status']:<10} {w['total_tasks']:<8} {w['last_ping']:<25} {w['vm_url']}")


def add_worker(url):
    """Add a new worker to the database"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('worker_nodes').insert({
            'vm_url': url,
            'status': 'active'
        }).execute()
        
        print(f"✅ Worker added successfully!")
        print(f"   ID: {response.data[0]['id']}")
        print(f"   URL: {url}")
    except Exception as e:
        print(f"❌ Error adding worker: {e}")


def remove_worker(worker_id):
    """Remove a worker from the database"""
    supabase = get_supabase_client()
    
    try:
        supabase.table('worker_nodes').delete().eq('id', int(worker_id)).execute()
        print(f"✅ Worker {worker_id} removed successfully!")
    except Exception as e:
        print(f"❌ Error removing worker: {e}")


def update_worker_status(worker_id, status):
    """Update worker status"""
    supabase = get_supabase_client()
    
    valid_statuses = ['active', 'busy', 'offline']
    if status not in valid_statuses:
        print(f"❌ Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return
    
    try:
        supabase.table('worker_nodes').update({
            'status': status,
            'last_ping': datetime.now().isoformat()
        }).eq('id', int(worker_id)).execute()
        
        print(f"✅ Worker {worker_id} status updated to '{status}'")
    except Exception as e:
        print(f"❌ Error updating worker: {e}")


def print_usage():
    """Print usage information"""
    print("""
🤖 NADG Worker Management Utility

Usage:
    python manage_workers.py list                    - List all workers
    python manage_workers.py add <url>               - Add a new worker
    python manage_workers.py remove <id>             - Remove a worker
    python manage_workers.py status <id> <status>    - Update worker status

Examples:
    python manage_workers.py list
    python manage_workers.py add https://worker-1.hf.space
    python manage_workers.py remove 1
    python manage_workers.py status 1 active

Required environment variables:
    SUPABASE_URL           - Your Supabase project URL
    SUPABASE_SERVICE_KEY   - Your Supabase service role key
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "list":
        list_workers()
    elif command == "add":
        if len(sys.argv) < 3:
            print("❌ Error: URL required")
            print("   Usage: python manage_workers.py add <url>")
            sys.exit(1)
        add_worker(sys.argv[2])
    elif command == "remove":
        if len(sys.argv) < 3:
            print("❌ Error: Worker ID required")
            print("   Usage: python manage_workers.py remove <id>")
            sys.exit(1)
        remove_worker(sys.argv[2])
    elif command == "status":
        if len(sys.argv) < 4:
            print("❌ Error: Worker ID and status required")
            print("   Usage: python manage_workers.py status <id> <status>")
            sys.exit(1)
        update_worker_status(sys.argv[2], sys.argv[3])
    else:
        print(f"❌ Unknown command: {command}")
        print_usage()
        sys.exit(1)
