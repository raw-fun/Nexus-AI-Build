# GitHub Agent Prompts for NADG

This file contains useful prompts for GitHub Copilot or Workspace agents to help build and extend the NADG system.

## Initial Setup Prompts

### 1. Build the Worker Node
```
Build a Python FastAPI worker node that accepts a JSON task, processes it using subprocess, 
and returns the output. The worker should have health check endpoints and be deployable to 
Hugging Face Spaces using Docker.
```

### 2. Create the Master Orchestrator
```
Write a Streamlit master app that integrates Google Gemini API to split a complex prompt 
into N tasks based on available workers in Supabase. It should distribute tasks 
asynchronously and display results in a dashboard.
```

### 3. Generate Heartbeat Workflow
```
Generate a GitHub Action YAML that reads URLs from a Supabase table and pings them every 
15 minutes to keep them alive. Update the last_ping timestamp and worker status in the database.
```

## Extension Prompts

### Add Authentication
```
Add JWT-based authentication to the worker node endpoints to ensure only authorized 
master apps can send tasks. Store API keys in environment variables.
```

### Implement Task Queue
```
Implement a Redis-based task queue system where the master app queues tasks and workers 
pull from the queue. Include retry logic for failed tasks.
```

### Add Monitoring Dashboard
```
Create a monitoring dashboard using Streamlit that shows real-time worker health, 
task completion rates, average execution time, and error rates from Supabase.
```

### GPU Worker Support
```
Modify the worker node to support GPU-based tasks using PyTorch or TensorFlow. 
Add a capability field to the database schema to track GPU vs CPU workers.
```

### Advanced Task Splitting
```
Enhance the Gemini prompt to analyze task dependencies and create a DAG (directed acyclic graph) 
for task execution order. Execute independent tasks in parallel and dependent tasks sequentially.
```

### Auto-scaling
```
Create a GitHub Action that monitors task queue depth in Supabase and automatically 
deploys additional Hugging Face Space workers when the queue exceeds a threshold.
```

### Results Aggregation
```
Add a results aggregation function to the master app that combines outputs from multiple 
workers using Gemini API to create a coherent final result.
```

### Error Recovery
```
Implement automatic retry logic in the master app. If a worker fails, redistribute 
its task to another available worker. Store retry attempts in the task_history table.
```

### Worker Specialization
```
Add a 'capabilities' JSON field to worker_nodes table. Let workers register their 
specializations (e.g., 'nlp', 'image-processing', 'data-analysis') and have the 
master app assign tasks to appropriate specialists.
```

### Docker Compose Setup
```
Create a docker-compose.yml that runs the master app, multiple worker instances, 
and a PostgreSQL database for local development and testing.
```

## Testing Prompts

### Unit Tests for Worker
```
Write pytest unit tests for the worker node that test all endpoints, error handling, 
timeout scenarios, and task execution with mocked subprocess calls.
```

### Integration Tests
```
Create integration tests that spin up a worker, register it in a test Supabase instance, 
run the master app, and verify end-to-end task distribution and execution.
```

### Load Testing
```
Build a load testing script using locust or pytest-benchmark that simulates 100 concurrent 
tasks being distributed to 10 workers and measures throughput and latency.
```

## Security Prompts

### Add Rate Limiting
```
Implement rate limiting on worker endpoints using slowapi to prevent abuse. 
Limit requests to 60 per minute per IP address.
```

### Sandbox Task Execution
```
Enhance worker security by using Docker containers or subprocess isolation with 
resource limits (CPU, memory, network) for task execution.
```

### Encrypt Communication
```
Add TLS/SSL certificate support to worker nodes and implement HTTPS-only communication 
between master and workers.
```

## Documentation Prompts

### API Documentation
```
Generate OpenAPI/Swagger documentation for the worker node API endpoints. 
Include example requests and responses for each endpoint.
```

### Architecture Diagram
```
Create a detailed architecture diagram in Mermaid format showing the flow of data 
between GitHub Actions, Master App, Supabase, Gemini API, and Worker Nodes.
```

### Deployment Guide
```
Write a comprehensive deployment guide for deploying the master app to Streamlit Cloud, 
workers to Hugging Face Spaces, and setting up Supabase with proper security rules.
```
