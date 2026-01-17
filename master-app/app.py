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
from datetime import datetime
import google.generativeai as genai
from supabase import create_client, Client

# Configuration from environment variables
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

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


async def send_task_to_worker(session, worker_url, task_data):
    """Send a task to a worker node asynchronously"""
    try:
        async with session.post(f"{worker_url}/execute", json=task_data, timeout=30) as response:
            result = await response.json()
            return {'worker': worker_url, 'status': 'success', 'result': result}
    except Exception as e:
        return {'worker': worker_url, 'status': 'error', 'error': str(e)}


async def distribute_tasks(tasks, workers):
    """Distribute tasks to workers asynchronously"""
    async with aiohttp.ClientSession() as session:
        task_promises = []
        for i, task in enumerate(tasks):
            worker = workers[i % len(workers)]
            task_data = {'task': task, 'task_id': i}
            task_promises.append(send_task_to_worker(session, worker['vm_url'], task_data))
        
        results = await asyncio.gather(*task_promises)
        return results


def split_task_with_gemini(user_command, num_workers):
    """Use Gemini API to intelligently split a task into subtasks"""
    prompt = f"""
You are a task distribution expert. Given the following user command and {num_workers} available workers,
split this into {num_workers} parallel subtasks that can be executed independently.

User Command: {user_command}

Please provide exactly {num_workers} subtasks as a numbered list. Each subtask should be:
1. Independent and executable on its own
2. Part of completing the overall user command
3. Concise and clear

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


def update_worker_task_count(worker_id):
    """Increment the total_tasks counter for a worker"""
    try:
        supabase.table('worker_nodes').update({
            'total_tasks': worker_id['total_tasks'] + 1,
            'last_ping': datetime.now().isoformat()
        }).eq('id', worker_id['id']).execute()
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
