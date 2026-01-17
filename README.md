# 🤖 NEXUS-AI Distributed Grid (NADG)

[![NADG Heartbeat](https://github.com/raw-fun/Nexus-AI-Build/actions/workflows/heartbeat.yml/badge.svg)](https://github.com/raw-fun/Nexus-AI-Build/actions/workflows/heartbeat.yml)

## 📋 Overview

NEXUS-AI Distributed Grid (NADG) is a professional distributed system architecture that combines:
- **GitHub** (Control Center & Automation)
- **Google AI Studio** (Gemini 1.5 Pro for intelligent task splitting)
- **Hugging Face Spaces** (Worker node deployment)
- **Supabase** (Database registry for worker management)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    GitHub (Hub)                         │
│  • Source Code Repository                              │
│  • GitHub Actions (24/7 Heartbeat)                     │
│  • Secrets Management                                  │
└────────────────┬────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
┌───▼──────────┐      ┌──────▼─────────┐
│ Master App   │      │   Supabase     │
│ (Streamlit)  │◄────►│   (Registry)   │
│              │      │                │
│ • Gemini API │      │ • Worker Nodes │
│ • Task Split │      │ • Task History │
└───┬──────────┘      └────────────────┘
    │
    │ Distributes Tasks
    │
    ▼
┌─────────────────────────────────────────┐
│         Worker Nodes (N instances)      │
│                                         │
│  Worker 1    Worker 2    Worker N      │
│  (FastAPI)   (FastAPI)   (FastAPI)     │
│  HF Space    HF Space    HF Space      │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### Step 1: Clone this Repository

```bash
git clone https://github.com/raw-fun/Nexus-AI-Build.git
cd Nexus-AI-Build
```

### Step 2: Configure GitHub Secrets

Go to **Settings > Secrets and Variables > Actions** and add:

| Secret Name | Description | Where to Get It |
|------------|-------------|-----------------|
| `GEMINI_API_KEY` | Google Gemini API key | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `SUPABASE_URL` | Your Supabase project URL | Supabase Project Settings |
| `SUPABASE_SERVICE_KEY` | Supabase service role key | Supabase Project API Settings |
| `HF_TOKEN` | Hugging Face write token | [Hugging Face Settings](https://huggingface.co/settings/tokens) |

### Step 3: Set Up Supabase Database

1. Create a new project on [Supabase](https://supabase.com)
2. Go to the SQL Editor
3. Run the schema from `database/schema.sql`:

```sql
CREATE TABLE worker_nodes (
    id SERIAL PRIMARY KEY,
    vm_url TEXT UNIQUE NOT NULL,
    status TEXT DEFAULT 'active',
    total_tasks INTEGER DEFAULT 0,
    last_ping TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### Step 4: Deploy Worker Nodes to Hugging Face

1. Create a new Space on [Hugging Face](https://huggingface.co/spaces)
2. Choose **Docker** as the SDK
3. Upload the contents of the `worker-node/` directory:
   - `Dockerfile`
   - `main.py`
   - `requirements.txt`
4. Once deployed, copy the Space URL (e.g., `https://username-spacename.hf.space`)
5. Register the worker in Supabase:

```sql
INSERT INTO worker_nodes (vm_url) 
VALUES ('https://your-worker-space.hf.space');
```

Repeat for multiple workers as needed.

### Step 5: Run the Master Orchestrator Locally

```bash
cd master-app
pip install -r requirements.txt

# Set environment variables
export GEMINI_API_KEY="your-key"
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_KEY="your-key"

# Run the app
streamlit run app.py
```

The master app will open in your browser at `http://localhost:8501`

### Step 6: Enable 24/7 Heartbeat (Automatic)

The GitHub Actions workflow in `.github/workflows/heartbeat.yml` will automatically:
- Run every 15 minutes
- Ping all registered workers
- Update their status in Supabase
- Keep Hugging Face Spaces from going to sleep

No additional configuration needed - it will start automatically once you push to the repository.

## 📁 Project Structure

```
nexus-ai-grid/
├── .github/
│   └── workflows/
│       └── heartbeat.yml          # 24/7 worker ping automation
├── database/
│   └── schema.sql                 # Supabase database schema
├── master-app/
│   ├── app.py                     # Streamlit orchestrator app
│   └── requirements.txt           # Python dependencies
├── worker-node/
│   ├── main.py                    # FastAPI worker service
│   ├── Dockerfile                 # Container for HF Spaces
│   └── requirements.txt           # Python dependencies
└── README.md                      # This file
```

## 🎯 How It Works

### Task Distribution Flow

1. **User Input**: Enter a complex command in the Master App
2. **AI Analysis**: Gemini 1.5 Pro analyzes and splits the task into N subtasks
3. **Worker Selection**: System fetches active workers from Supabase
4. **Distribution**: Master sends subtasks to workers via async POST requests
5. **Execution**: Each worker executes its subtask independently
6. **Aggregation**: Results are collected and displayed in the Master App

### Example Usage

**Input**: 
```
Analyze customer sentiment from reviews, generate a summary report, 
and create data visualizations
```

**Gemini Splits Into**:
1. Extract and analyze sentiment from customer reviews
2. Generate comprehensive summary statistics
3. Create visualization charts and graphs

**Workers Execute**:
- Worker 1 → Sentiment Analysis
- Worker 2 → Summary Generation  
- Worker 3 → Visualization Creation

## 🔧 Configuration

### Master App Environment Variables

```bash
GEMINI_API_KEY=your_gemini_api_key
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key
```

### Worker Node Environment Variables

```bash
WORKER_ID=worker-1  # Optional: Identifier for this worker
PORT=7860           # Default port for Hugging Face Spaces
```

## 📊 Worker Management

### Register a New Worker

```sql
INSERT INTO worker_nodes (vm_url, status) 
VALUES ('https://worker-url.hf.space', 'active');
```

### Check Worker Status

```sql
SELECT * FROM worker_nodes 
WHERE status = 'active' 
ORDER BY last_ping DESC;
```

### Remove a Worker

```sql
DELETE FROM worker_nodes WHERE id = 1;
```

## 🛠️ Development

### Running Worker Locally

```bash
cd worker-node
pip install -r requirements.txt
python main.py
```

Worker will be available at `http://localhost:7860`

### Testing Worker Endpoints

```bash
# Health check
curl http://localhost:7860/health

# Execute a task
curl -X POST http://localhost:7860/execute \
  -H "Content-Type: application/json" \
  -d '{"task": "print(\"Hello from NADG\")", "task_id": 1}'
```

## 🔐 Security Considerations

- **Never commit secrets** to the repository
- Use GitHub Secrets for all sensitive credentials
- Worker nodes execute tasks in isolated subprocess environments
- Consider implementing additional sandboxing for production use
- Regularly rotate API keys and tokens

## 📈 Monitoring

### GitHub Actions Logs

View heartbeat logs: **Actions > NADG Heartbeat > Latest run**

### Worker Health

Check worker status in Supabase or via the Master App dashboard

### Task History

Query the `task_history` table in Supabase for execution logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues or questions:
- Open an issue on GitHub
- Check existing documentation
- Review worker logs in Hugging Face Spaces

## 🎓 Use Cases

- **Parallel Data Processing**: Split large datasets across workers
- **Multi-model AI Tasks**: Different workers run different models
- **Distributed Computing**: Execute compute-intensive tasks in parallel
- **Automated Testing**: Run test suites across multiple environments
- **Content Generation**: Parallel generation of content pieces

## 🔮 Future Enhancements

- [ ] Auto-scaling based on workload
- [ ] Advanced task scheduling and prioritization
- [ ] Worker performance monitoring and analytics
- [ ] Support for GPU workers
- [ ] Task result caching
- [ ] Worker load balancing improvements

---

**Built with ❤️ for distributed AI workloads**