# NADG Setup Guide

This guide walks you through setting up the complete NEXUS-AI Distributed Grid system.

## Prerequisites

- GitHub account with a repository
- Google AI Studio account (for Gemini API)
- Supabase account (free tier is fine)
- Hugging Face account (for deploying workers)
- Python 3.10+ installed locally

## Detailed Setup Steps

### 1. GitHub Repository Configuration

1. If you haven't already, create a new repository or use this one
2. Navigate to **Settings** > **Secrets and variables** > **Actions**
3. Click **New repository secret** for each of the following:

#### GEMINI_API_KEY
- Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
- Click "Create API Key"
- Copy the key and add it as a secret

#### SUPABASE_URL and SUPABASE_SERVICE_KEY
- Go to [Supabase](https://supabase.com) and create a new project
- Once created, go to **Project Settings** > **API**
- Copy the **URL** (save as SUPABASE_URL)
- Copy the **service_role** key (save as SUPABASE_SERVICE_KEY)
  - ⚠️ Use service_role, not anon key, for the master app

#### HF_TOKEN
- Go to [Hugging Face Settings](https://huggingface.co/settings/tokens)
- Create a new token with **write** access
- Copy and save as HF_TOKEN secret

#### NADG_AUTH_TOKEN
- Generate a secure random token (e.g., using `openssl rand -hex 32`)
- This token secures communication between master and workers
- Add it as a secret with name NADG_AUTH_TOKEN
- ⚠️ **Important**: Use the same token in both master and worker environments

### 2. Database Setup

1. In your Supabase project, click **SQL Editor**
2. Create a new query and paste the contents of `database/schema.sql`
3. Run the query to create the tables
4. Verify the tables were created in the **Table Editor**

### 3. Deploy Your First Worker

#### Option A: Using Hugging Face Spaces (Recommended)

1. Go to [Hugging Face Spaces](https://huggingface.co/spaces)
2. Click **Create new Space**
3. Choose:
   - Name: `nadg-worker-1` (or any name)
   - License: Your choice (MIT recommended)
   - SDK: **Docker**
   - Hardware: CPU (free tier)
4. Once created, go to **Settings** > **Variables and secrets**
5. Add a new secret:
   - Name: `NADG_AUTH_TOKEN`
   - Value: Same token you added to GitHub secrets
6. Click **Files** > **Add file** > **Upload files**
7. Upload these files from the `worker-node/` directory:
   - `Dockerfile`
   - `main.py`
   - `requirements.txt`
8. Commit the files
9. Wait for the Space to build (check the logs)
10. Once running, copy your Space URL (e.g., `https://username-nadg-worker-1.hf.space`)

#### Option B: Deploy Locally for Testing

```bash
cd worker-node
pip install -r requirements.txt

# Set the authentication token
export NADG_AUTH_TOKEN="your-secret-token"

python main.py
```

This will run a worker at `http://localhost:7860`

### 4. Register Worker in Supabase

1. Go to your Supabase project
2. Open **Table Editor** > **worker_nodes**
3. Click **Insert** > **Insert row**
4. Fill in:
   - `vm_url`: Your worker URL (from step 3)
   - `status`: `active`
   - Leave other fields as default
5. Click **Save**

Alternatively, use SQL:

```sql
INSERT INTO worker_nodes (vm_url, status) 
VALUES ('https://your-worker-url.hf.space', 'active');
```

### 5. Run the Master Orchestrator

#### Local Development

```bash
cd master-app
pip install -r requirements.txt

# Set environment variables (Linux/Mac)
export GEMINI_API_KEY="your-key"
export SUPABASE_URL="your-url"
export SUPABASE_SERVICE_KEY="your-key"
export NADG_AUTH_TOKEN="your-secret-token"

# Or on Windows
set GEMINI_API_KEY=your-key
set SUPABASE_URL=your-url
set SUPABASE_SERVICE_KEY=your-key
set NADG_AUTH_TOKEN=your-secret-token

# Run the app
streamlit run app.py
```

#### Using .env file (Recommended)

```bash
cd master-app
cp .env.example .env
# Edit .env with your actual values
pip install -r requirements.txt
streamlit run app.py
```

The app will open at `http://localhost:8501`

### 6. Test the System

1. Open the Master App in your browser
2. You should see your worker(s) listed in the "Active Workers" section
3. Enter a test command, for example:
   ```
   Create a Python script that prints "Hello from NADG"
   ```
4. Click "Execute Task"
5. Watch as Gemini splits the task and distributes it to workers
6. View the results

### 7. Verify GitHub Actions

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You should see "NADG Heartbeat" workflow
4. The workflow will run automatically every 15 minutes
5. You can also click **Run workflow** to trigger it manually

### 8. Scale to Multiple Workers

Repeat step 3 to create more workers, and step 4 to register them. The system will automatically distribute tasks across all active workers.

## Troubleshooting

### Worker shows as "offline" in dashboard

- Check if the worker URL is accessible
- Verify the worker is running (check Hugging Face Space logs)
- Ensure the URL in Supabase is correct (include https://)

### Master App can't connect to Supabase

- Verify SUPABASE_URL and SUPABASE_SERVICE_KEY are set correctly
- Check that you're using the service_role key, not the anon key
- Ensure the Supabase project is active

### Gemini API errors

- Verify your GEMINI_API_KEY is correct
- Check your API quota at Google AI Studio
- Ensure you have enabled the Gemini API in your Google Cloud project

### GitHub Actions heartbeat failing

- Check the Actions logs for specific errors
- Verify secrets are set correctly in repository settings
- Ensure Supabase credentials have the correct permissions

## Next Steps

- Add more workers to increase capacity
- Customize the worker execution logic in `worker-node/main.py`
- Enhance the master app UI in `master-app/app.py`
- Set up monitoring and logging
- Deploy the master app to a cloud platform for 24/7 access

## Support

If you encounter issues:
1. Check the logs (GitHub Actions, Hugging Face Space, local terminal)
2. Review the troubleshooting section above
3. Open an issue on GitHub with details about your problem
