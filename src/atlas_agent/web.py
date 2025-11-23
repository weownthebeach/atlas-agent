"""Web interface for ATLAS Agent."""

import asyncio
import os
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from atlas_agent.core import AtlasAgent
from atlas_agent.config import AtlasConfig

app = FastAPI(title="ATLAS Web Tester", description="AI-powered web testing with Claude")

# Store test results
test_results = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ATLAS Web Tester</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
        }
        .form-container {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        input[type="text"], input[type="url"], textarea {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 14px;
            margin-bottom: 15px;
        }
        textarea {
            min-height: 100px;
            resize: vertical;
        }
        button {
            background: #007bff;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 4px;
            font-size: 16px;
            cursor: pointer;
            width: 100%;
        }
        button:hover {
            background: #0056b3;
        }
        button:disabled {
            background: #ccc;
            cursor: not-allowed;
        }
        .results {
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .result-item {
            border-bottom: 1px solid #eee;
            padding: 15px 0;
        }
        .result-item:last-child {
            border-bottom: none;
        }
        .result-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
        }
        .result-task {
            font-weight: 600;
        }
        .result-status {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
        }
        .status-running {
            background: #fff3cd;
            color: #856404;
        }
        .result-response {
            background: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            font-size: 13px;
            white-space: pre-wrap;
            max-height: 300px;
            overflow-y: auto;
        }
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #007bff;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .config-note {
            background: #e7f3ff;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            color: #0056b3;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <h1>🔍 ATLAS Web Tester</h1>
    <p class="subtitle">AI-powered web testing using Claude's computer-use capability</p>

    <div class="form-container">
        <form id="testForm">
            <div class="config-note">
                API Key Status: <strong id="apiStatus">Checking...</strong>
            </div>

            <label for="url">Target URL</label>
            <input type="url" id="url" name="url" placeholder="https://example.com" required>

            <label for="task">Test Description</label>
            <textarea id="task" name="task" placeholder="Describe what you want to test in natural language...&#10;&#10;Examples:&#10;- Click the login button and verify a form appears&#10;- Fill in the search box with 'test' and submit&#10;- Verify all navigation links are visible" required></textarea>

            <button type="submit" id="submitBtn">Run Test</button>
        </form>
    </div>

    <div class="results">
        <h2>Test Results</h2>
        <div id="resultsContainer">
            <p style="color: #666; text-align: center;">No tests run yet</p>
        </div>
    </div>

    <script>
        // Check API status
        fetch('/api/status')
            .then(r => r.json())
            .then(data => {
                document.getElementById('apiStatus').textContent =
                    data.api_configured ? '✅ Configured' : '❌ Not set (export ANTHROPIC_API_KEY)';
            });

        document.getElementById('testForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const btn = document.getElementById('submitBtn');
            const container = document.getElementById('resultsContainer');

            btn.disabled = true;
            btn.textContent = 'Running Test...';

            // Add loading indicator
            const loadingId = Date.now();
            container.innerHTML = `
                <div class="result-item" id="result-${loadingId}">
                    <div class="loading">
                        <div class="spinner"></div>
                        Running test... This may take a minute.
                    </div>
                </div>
            ` + container.innerHTML;

            try {
                const response = await fetch('/api/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        url: document.getElementById('url').value,
                        task: document.getElementById('task').value
                    })
                });

                const result = await response.json();

                document.getElementById(`result-${loadingId}`).innerHTML = `
                    <div class="result-header">
                        <span class="result-task">${result.task}</span>
                        <span class="result-status ${result.success ? 'status-success' : 'status-error'}">
                            ${result.success ? 'PASS' : 'FAIL'}
                        </span>
                    </div>
                    <div><strong>URL:</strong> ${result.url}</div>
                    <div><strong>Iterations:</strong> ${result.iterations}</div>
                    <div class="result-response">${result.response || result.error || 'No response'}</div>
                `;
            } catch (error) {
                document.getElementById(`result-${loadingId}`).innerHTML = `
                    <div class="result-header">
                        <span class="result-task">Error</span>
                        <span class="result-status status-error">ERROR</span>
                    </div>
                    <div class="result-response">${error.message}</div>
                `;
            }

            btn.disabled = false;
            btn.textContent = 'Run Test';
        });
    </script>
</body>
</html>
"""


class TestRequest(BaseModel):
    url: str
    task: str


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve the main web interface."""
    return HTML_TEMPLATE


@app.get("/api/status")
async def status():
    """Check API configuration status."""
    config = AtlasConfig()
    return {
        "api_configured": config.validate_api_key(),
        "model": config.model,
        "driver": config.driver_type,
    }


@app.post("/api/test")
async def run_test(request: TestRequest):
    """Run a test and return results."""
    config = AtlasConfig(headless=True)

    if not config.validate_api_key():
        return JSONResponse(
            status_code=400,
            content={
                "success": False,
                "error": "ANTHROPIC_API_KEY not configured",
                "task": request.task,
                "url": request.url,
                "iterations": 0,
                "response": ""
            }
        )

    try:
        async with AtlasAgent(config) as agent:
            result = await agent.run_test(request.task, request.url)
            return {
                "success": result.success,
                "task": result.task,
                "url": result.url,
                "response": result.response,
                "iterations": result.iterations,
                "error": result.error
            }
    except Exception as e:
        return {
            "success": False,
            "task": request.task,
            "url": request.url,
            "response": "",
            "iterations": 0,
            "error": str(e)
        }


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the web server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
