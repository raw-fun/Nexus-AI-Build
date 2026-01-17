"""
NEXUS-AI Distributed Grid (NADG) - Master Orchestrator
============================================================
Purpose: Central brain that splits tasks and manages workers
Stack: Streamlit + Google Gemini API + Supabase
============================================================
"""

import os
import asyncio
import aiohttp
import streamlit as st
import logging
from datetime import datetime
import google.generativeai as genai
from supabase import create_client, Client

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
NADG_AUTH_TOKEN = os.environ.get('NADG_AUTH_TOKEN', '')

# Initialize clients
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')

if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


def get_active_workers():
    """Fetch all active worker nodes from Supabase"""
    try:
        response = supabase.table('worker_nodes').select('*').eq('status', 'active').execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching workers: {e}")
        return []


def mark_worker_offline(worker_id):
    """Mark a worker as offline in Supabase"""
    try:
        supabase.table('worker_nodes').update({
            'status': 'offline'
        }).eq('id', worker_id).execute()
        logger.info(f"Marked worker {worker_id} as offline")
    except Exception as e:
        logger.error(f"Error marking worker {worker_id} as offline: {e}")


async def send_task_to_worker(session, worker_url, task_data, worker_id=None):
    """
    Send a task to a worker node asynchronously with authentication.
    Includes X-NADG-AUTH header for secure communication.
    """
    headers = {}
    if NADG_AUTH_TOKEN:
        headers['X-NADG-AUTH'] = NADG_AUTH_TOKEN
    
    try:
        async with session.post(
            f"{worker_url}/execute",
            json=task_data,
            headers=headers,
            timeout=30
        ) as response:
            result = await response.json()
            return {
                'worker': worker_url,
                'worker_id': worker_id,
                'status': 'success',
                'result': result
            }
    except Exception as e:
        logger.error(f"Error sending task to worker {worker_url}: {e}")
        return {
            'worker': worker_url,
            'worker_id': worker_id,
            'status': 'error',
            'error': str(e)
        }


async def send_task_with_retry(session, task_data, task_index, initial_worker, all_workers_list, max_retries=3):
    """
    Send a task to a worker with retry logic and automatic re-assignment.
    If a worker fails, marks it offline and tries the next available worker.
    """
    attempted_workers = set()
    current_worker = initial_worker
    
    for attempt in range(max_retries):
        if current_worker['id'] in attempted_workers:
            # Already tried this worker, get a new one
            active_workers = get_active_workers()
            available_workers = [
                w for w in active_workers
                if w['id'] not in attempted_workers
            ]
            
            if not available_workers:
                logger.error(f"No more workers available for task {task_index}")
                return {
                    'worker': 'none',
                    'worker_id': None,
                    'status': 'error',
                    'error': 'No available workers remaining',
                    'task_index': task_index
                }
            
            current_worker = available_workers[0]
        
        attempted_workers.add(current_worker['id'])
        logger.info(f"Attempt {attempt + 1}/{max_retries}: Task {task_index} on worker {current_worker['id']}: {current_worker['vm_url']}")
        
        # Send task to worker
        result = await send_task_to_worker(
            session,
            current_worker['vm_url'],
            task_data,
            current_worker['id']
        )
        
        if result['status'] == 'success':
            logger.info(f"Task {task_index} succeeded on worker {current_worker['id']}")
            return result
        else:
            # Worker failed - mark as offline
            logger.warning(f"Worker {current_worker['id']} failed: {result.get('error')}")
            mark_worker_offline(current_worker['id'])
            
            # Continue to next iteration to try another worker
    
    return {
        'worker': 'failed',
        'worker_id': None,
        'status': 'error',
        'error': f'Task failed after {max_retries} retries',
        'task_index': task_index
    }


async def distribute_tasks(tasks, workers):
    """
    Distribute tasks to workers asynchronously with error recovery.
    Automatically retries failed tasks on different workers.
    """
    async with aiohttp.ClientSession() as session:
        task_promises = []
        for i, task in enumerate(tasks):
            worker = workers[i % len(workers)]
            task_data = {'task': task, 'task_id': i}
            task_promises.append(
                send_task_with_retry(session, task_data, i, worker, workers)
            )
        
        results = await asyncio.gather(*task_promises)
        return results


def split_task_with_gemini(user_command, num_workers):
    """
    Use Gemini API to intelligently split a task into subtasks.
    Handles dynamic worker counts where some nodes might be busy or offline.
    """
    prompt = f"""
You are a task distribution expert. Given the following user command and {num_workers} available workers,
split this into up to {num_workers} parallel subtasks that can be executed independently.

User Command: {user_command}

Important considerations:
- Create subtasks that are independent and can run in parallel
- If the command can be completed in fewer than {num_workers} subtasks, that's acceptable
- Each subtask should be concise, clear, and executable on its own
- Account for the fact that some workers might go offline during execution
- Ensure each subtask contributes to completing the overall user command

Please provide your subtasks as a numbered list. Each subtask should be:
1. Independent and executable on its own
2. Part of completing the overall user command
3. Concise and clear
4. Resilient to worker failures (no dependencies between subtasks)

Format your response as a simple numbered list.
"""
    
    try:
        response = model.generate_content(prompt)
        tasks_text = response.text
        
        # Parse the response into individual tasks
        tasks = []
        for line in tasks_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove numbering and clean up
                task = line.split('.', 1)[-1].strip() if '.' in line else line.strip('- ')
                if task:
                    tasks.append(task)
        
        return tasks[:num_workers]  # Ensure we don't exceed worker count
    except Exception as e:
        st.error(f"Error with Gemini API: {e}")
        return []


def update_worker_task_count(worker):
    """Increment the total_tasks counter for a worker"""
    try:
        supabase.table('worker_nodes').update({
            'total_tasks': worker['total_tasks'] + 1,
            'last_ping': datetime.now().isoformat()
        }).eq('id', worker['id']).execute()
    except Exception as e:
        st.error(f"Error updating worker: {e}")


# Streamlit UI
def main():
    st.set_page_config(page_title="NADG Master Orchestrator", page_icon="🤖", layout="wide")
    
    st.title("🤖 NEXUS-AI Distributed Grid")
    st.subheader("Master Orchestrator - Task Distribution System")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"Gemini API: {'✅ Configured' if GEMINI_API_KEY else '❌ Not Configured'}")
        st.info(f"Supabase: {'✅ Connected' if SUPABASE_URL and SUPABASE_SERVICE_KEY else '❌ Not Connected'}")
        st.info(f"Auth Token: {'✅ Enabled' if NADG_AUTH_TOKEN else '⚠️  Disabled (insecure)'}")
        
        if st.button("🔄 Refresh Workers"):
            st.rerun()
    
    # Worker Status Display
    st.header("👥 Active Workers")
    workers = get_active_workers()
    
    if workers:
        cols = st.columns(min(len(workers), 4))
        for i, worker in enumerate(workers):
            with cols[i % 4]:
                st.metric(
                    label=f"Worker {worker['id']}",
                    value=worker['status'].upper(),
                    delta=f"{worker['total_tasks']} tasks"
                )
                st.caption(f"URL: {worker['vm_url']}")
    else:
        st.warning("No active workers found. Please register workers in Supabase.")
    
    # Task Input and Distribution
    st.header("📋 Task Distribution")
    
    user_command = st.text_area(
        "Enter your command:",
        placeholder="Example: Analyze the sentiment of customer reviews, generate a summary, and create visualizations",
        height=100
    )
    
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.button("🚀 Execute Task", type="primary", disabled=not workers or not user_command):
            with st.spinner("Processing..."):
                # Split task using Gemini
                st.write("### 🧠 Splitting task with Gemini AI...")
                subtasks = split_task_with_gemini(user_command, len(workers))
                
                if subtasks:
                    st.write("### 📦 Generated Subtasks:")
                    for i, task in enumerate(subtasks, 1):
                        st.write(f"{i}. {task}")
                    
                    # Distribute tasks to workers
                    st.write("### 🌐 Distributing to workers...")
                    results = asyncio.run(distribute_tasks(subtasks, workers))
                    
                    # Display results
                    st.write("### ✅ Results:")
                    for result in results:
                        if result['status'] == 'success':
                            st.success(f"Worker {result['worker']}: Success")
                            st.json(result['result'])
                        else:
                            st.error(f"Worker {result['worker']}: {result['error']}")
                    
                    # Update worker stats
                    for worker in workers:
                        update_worker_task_count(worker)
                else:
                    st.error("Failed to split tasks. Please check your Gemini API configuration.")
    
    with col2:
        st.metric("Available Workers", len(workers))


if __name__ == "__main__":
    main()
