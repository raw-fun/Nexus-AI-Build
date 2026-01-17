# NADG Usage Examples

This document provides practical examples of using the NEXUS-AI Distributed Grid system.

## Example 1: Simple Text Processing

### User Input
```
Analyze the sentiment of customer reviews, categorize them by topic, and generate a summary report
```

### How NADG Handles It

1. **Gemini Splits Task:**
   - Subtask 1: Extract and analyze sentiment from customer reviews
   - Subtask 2: Categorize reviews by topic (product, service, support)
   - Subtask 3: Generate summary statistics and report

2. **Distribution:**
   - Worker 1 receives Subtask 1
   - Worker 2 receives Subtask 2
   - Worker 3 receives Subtask 3

3. **Execution:**
   Each worker processes its subtask independently

4. **Result:**
   Master app collects and displays all results

## Example 2: Data Processing Pipeline

### User Input
```
Process a dataset by cleaning missing values, performing statistical analysis, and creating visualizations
```

### Task Split by Gemini
1. Clean dataset and handle missing values
2. Perform statistical analysis (mean, median, correlations)
3. Generate data visualizations and charts

### Worker Assignment
- Worker 1: Data cleaning
- Worker 2: Statistical analysis
- Worker 3: Visualization generation

## Example 3: Multi-Model AI Tasks

### User Input
```
Generate product descriptions, create marketing copy, and design email templates for a new product launch
```

### Task Split
1. Generate detailed product descriptions highlighting features
2. Create compelling marketing copy for advertisements
3. Design email template structure and content

### Parallel Execution
All three workers generate content simultaneously, reducing total time by ~3x

## Example 4: Research and Analysis

### User Input
```
Research competitors, analyze market trends, and summarize findings with recommendations
```

### Task Split
1. Compile competitor information and features
2. Analyze current market trends and statistics
3. Synthesize findings and create recommendations

## Example 5: Code Generation

### User Input
```
Create a Python API client, write unit tests, and generate documentation
```

### Task Split
1. Develop Python API client with all endpoints
2. Write comprehensive unit tests with pytest
3. Generate API documentation and usage examples

## Real-World Workflow Example

### Scenario: Content Creation for Blog

```python
# User submits via Master App UI:
task = """
Create a technical blog post about distributed systems:
1. Write an introduction about microservices
2. Explain the benefits of distributed computing
3. Provide code examples in Python
4. Create a conclusion with best practices
"""

# Gemini splits into 4 subtasks (assuming 4 workers):
subtasks = [
    "Write an engaging introduction about microservices architecture",
    "Explain the key benefits of distributed computing with examples",
    "Provide practical Python code examples for distributed systems",
    "Create a conclusion summarizing best practices for distributed systems"
]

# Distribution (async):
Worker 1 -> Subtask 1 (Introduction)
Worker 2 -> Subtask 2 (Benefits)
Worker 3 -> Subtask 3 (Code Examples)
Worker 4 -> Subtask 4 (Conclusion)

# Results collected in 1/4 of the time it would take sequentially
```

## Testing the System Locally

### Step 1: Start a Worker
```bash
cd worker-node
source venv/bin/activate
python main.py
# Worker running on http://localhost:7860
```

### Step 2: Test Worker Manually
```bash
# In another terminal
curl http://localhost:7860/health

# Send a test task
curl -X POST http://localhost:7860/execute \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate the sum of 1+2+3",
    "task_id": 1
  }'
```

### Step 3: Run Master App
```bash
cd master-app
source venv/bin/activate

# Set environment variables
export GEMINI_API_KEY="your-key"
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_KEY="your-key"

# Start the app
streamlit run app.py
```

### Step 4: Register Worker in Supabase
```sql
INSERT INTO worker_nodes (vm_url, status) 
VALUES ('http://localhost:7860', 'active');
```

### Step 5: Submit Task via UI
1. Open http://localhost:8501
2. Enter a task in the text area
3. Click "Execute Task"
4. Watch the results appear

## Advanced Usage Patterns

### Pattern 1: Batch Processing
```
Submit multiple independent tasks
Each task gets distributed to available workers
Process hundreds of items in parallel
```

### Pattern 2: Pipeline Processing
```
Task A -> Worker 1 (completed)
Output of A feeds into Task B -> Worker 2
Sequential with parallel sub-components
```

### Pattern 3: Map-Reduce
```
Map Phase: Distribute data chunks to workers
Each worker processes its chunk
Reduce Phase: Aggregate results from all workers
```

## Performance Considerations

### Optimal Task Characteristics
✅ **Good for NADG:**
- Independent, parallel tasks
- CPU-bound operations
- I/O operations that can run concurrently
- Multiple similar tasks (batch processing)

❌ **Not ideal for NADG:**
- Tasks with heavy dependencies
- Requires shared state
- Very short tasks (overhead > execution time)
- Tasks requiring GPU (unless workers are GPU-enabled)

### Scaling Guidelines

| Workers | Suitable For | Example Use Case |
|---------|-------------|------------------|
| 2-3 | Simple splitting | "Analyze and summarize" |
| 4-8 | Medium complexity | "Process dataset in 5 steps" |
| 10+ | Batch processing | "Process 100 images" |

## Troubleshooting Examples

### Example: Task Times Out
```
Problem: Worker doesn't respond in time
Solution: 
1. Increase timeout in task request
2. Check worker logs in Hugging Face Space
3. Verify worker is not sleeping (heartbeat)
```

### Example: Task Fails
```
Problem: Worker returns error
Solution:
1. Check worker logs for error details
2. Verify task is valid and executable
3. Test task locally first
4. Check worker has required dependencies
```

### Example: Uneven Distribution
```
Problem: One worker gets all tasks
Solution:
1. Verify all workers are registered as 'active'
2. Check worker_nodes table in Supabase
3. Ensure heartbeat is running to keep workers alive
```

## Best Practices

### 1. Task Design
- Keep subtasks independent
- Avoid inter-task communication
- Design for idempotency (safe to retry)

### 2. Error Handling
- Always set reasonable timeouts
- Plan for worker failures
- Have fallback strategies

### 3. Monitoring
- Check worker status regularly
- Monitor task success rates
- Track execution times

### 4. Cost Optimization
- Use free tier for development
- Upgrade to paid tier for production
- Monitor API quotas (Gemini)

## Production Example

### Real Deployment Workflow

1. **Setup (One-time):**
   - Configure all GitHub Secrets
   - Deploy 5 workers to Hugging Face Spaces
   - Register workers in Supabase
   - Deploy master app to Streamlit Cloud

2. **Daily Usage:**
   - Users access master app via URL
   - Submit tasks via web interface
   - System automatically distributes and executes
   - Results displayed in real-time

3. **Monitoring:**
   - GitHub Actions heartbeat runs every 15 min
   - Workers stay alive 24/7
   - Check Supabase dashboard for stats

4. **Scaling:**
   - Add more workers during peak times
   - Register new workers in Supabase
   - System auto-discovers and uses them

## API Usage Example (Future)

```python
# Example of programmatic access (can be extended)
import requests

master_url = "https://your-master-app.streamlit.app"

task = {
    "command": "Process 100 images with filters",
    "priority": "high"
}

response = requests.post(f"{master_url}/api/submit", json=task)
results = response.json()
```

## Next Steps

After trying these examples:
1. Deploy your own workers to Hugging Face
2. Customize worker capabilities
3. Enhance task splitting logic
4. Build custom UIs for specific use cases
5. Integrate with your existing workflows
