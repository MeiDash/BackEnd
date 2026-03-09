import modal
import subprocess
import time

app = modal.App("ollama-server")

image = (
    modal.Image.debian_slim()
    .apt_install("curl", "zstd")
    .run_commands(
        "curl -fsSL https://ollama.com/install.sh | sh",
        "ollama serve & sleep 5 && ollama pull llama3.2-vision && ollama pull gemma3:1b",
    )
    .pip_install("fastapi[standard]", "requests", "httpx")
)

@app.function(
    gpu="T4",
    image=image,
    scaledown_window=300,
    timeout=300,
)
@modal.asgi_app()
def ollama_proxy():
    from fastapi import FastAPI, Request
    from fastapi.responses import StreamingResponse
    import httpx

    subprocess.Popen(["ollama", "serve"])
    time.sleep(3)

    app = FastAPI()

    @app.api_route("/{path:path}", methods=["GET", "POST", "DELETE"])
    async def proxy(path: str, request: Request):
        async with httpx.AsyncClient(timeout=240) as client:
            url = f"http://localhost:11434/{path}"
            body = await request.body()
            resp = await client.request(
                method=request.method,
                url=url,
                content=body,
                headers={"Content-Type": "application/json"},
            )
            return StreamingResponse(
                content=iter([resp.content]),
                status_code=resp.status_code,
                media_type=resp.headers.get("content-type", "application/json"),
            )

    return app