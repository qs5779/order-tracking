"""Top level module for fastapi application."""

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from loguru import logger
from starlette.responses import FileResponse

from app.config.config import cfg, templates
from app.config.database import engine
from app.models import create_all_tables
from app.routes.forms.router import router as form_routes
from app.routes.order.router import router as order_routes
from app.routes.shipper.router import router as shipper_routes
from app.routes.vendor.router import router as vendor_routes

# FastAPI app instance
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

logger.debug(str(cfg))

create_all_tables(engine)

app.include_router(vendor_routes)
app.include_router(shipper_routes)
app.include_router(order_routes)
app.include_router(form_routes)


@app.get("/")
def main_function(request: Request) -> HTMLResponse:
    """Redirect to documentation (`/docs/`)."""
    context = {
        "request": request,
        "pending_url": order_routes.url_path_for("pending"),
        "orders_url": order_routes.url_path_for("orders"),
        "add_order_url": form_routes.url_path_for("order_get", order_id=0),
    }
    return templates.TemplateResponse("index.html.j2", context)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon() -> FileResponse:
    """Serve favicon.ico file."""
    return FileResponse("static/favicon.ico")


if __name__ == "__main__":
    import uvicorn  # noqa: WPS433

    PORT = 8000
    uvicorn.run(app, host="127.0.0.1", port=PORT)
