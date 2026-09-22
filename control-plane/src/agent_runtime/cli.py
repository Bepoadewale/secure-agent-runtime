import json
import os
import urllib.request

import typer

app = typer.Typer(help="Secure Agent Runtime API client")
URL = os.getenv("AGENT_RUNTIME_URL", "http://127.0.0.1:8000")
TOKEN = os.getenv("AGENT_RUNTIME_TOKEN")


def get(path):
    if not TOKEN:
        raise typer.BadParameter("set AGENT_RUNTIME_TOKEN to a signed local JWT")
    request = urllib.request.Request(f"{URL}{path}", headers={"Authorization": f"Bearer {TOKEN}"})
    return json.loads(urllib.request.urlopen(request, timeout=10).read())


@app.command()
def status(task_id: str):
    typer.echo(json.dumps(get(f"/api/v1/tasks/{task_id}"), indent=2))


@app.command()
def logs(task_id: str):
    typer.echo(json.dumps(get(f"/api/v1/tasks/{task_id}/events"), indent=2))


@app.command()
def artifacts(task_id: str):
    typer.echo(json.dumps(get(f"/api/v1/tasks/{task_id}/artifacts"), indent=2))
