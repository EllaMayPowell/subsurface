from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pyo import Server
import traceback

# Start audio server
s = Server().boot().start()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Keep track of running pyo objects
STATE = {"objects": []}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("editor.html", {"request": request})

@app.post("/run")
async def run_code(request: Request):
    code = (await request.body()).decode("utf-8")
    try:
        # Stop old sounds
        for obj in STATE["objects"]:
            try:
                obj.stop()
            except:
                pass
        STATE["objects"].clear()

        local_scope = {"s": s, "STATE": STATE}
        exec(code, {}, local_scope)

        if "out_obj" in local_scope:
            STATE["objects"].append(local_scope["out_obj"])

        return JSONResponse({"status": "ok"})
    except Exception as e:
        tb = traceback.format_exc()
        return JSONResponse({"status": "error", "error": str(e), "traceback": tb})

@app.post("/stop")
async def stop_code():
    for obj in STATE["objects"]:
        try:
            obj.stop()
        except:
            pass
    STATE["objects"].clear()
    return JSONResponse({"status": "stopped"})
