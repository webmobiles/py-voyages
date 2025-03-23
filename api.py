from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from dotenv import load_dotenv
import psycopg2
import os

# Load environment variables
load_dotenv()

# FastAPI app
app = FastAPI(
    title="Tour Booking API",
    description="An API to fetch available tours from a PostgreSQL database and render them via HTML templates.",
    version="1.0.0",
    contact={
        "name": "Dave I.",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

# Jinja2 templates directory
templates = Jinja2Templates(directory="templates")

# Database configuration
DB_CONFIG = {
    'dbname': os.getenv('POSTGRES_DB'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.getenv('POSTGRES_HOST'),
    'port': os.getenv('POSTGRES_PORT', 5432),
}


# Pydantic model for API documentation (in case we use JSON)
class Tour(BaseModel):
    id: int
    name: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Alpine Hiking Tour"
            }
        }


def get_tours():
    """Fetch tours from the PostgreSQL database that are active and not deleted."""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT id, name 
        FROM tour 
        WHERE onlineregtype = 2 
        AND inactive IS NOT TRUE 
        AND deleted IS NOT TRUE
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "name": r[1]} for r in rows]


@app.get(
    "/",
    response_class=HTMLResponse,
    tags=["Web Pages"],
    summary="HTML Tour Page",
    description="Returns an HTML page that lists all available tours from the database."
)
def tour_list(request: Request):
    """
    Render the `tours.html` template with tour data.

    - Fetches all active, visible tours from the database.
    - Passes the list to the HTML template for display.
    """
    tours = get_tours()
    return templates.TemplateResponse("tours.html", {"request": request, "tours": tours})


@app.get(
    "/api/tours",
    response_model=list[Tour],
    tags=["API"],
    summary="Get All Tours (JSON)",
    description="Returns a JSON array of all active tours that are available for online registration."
)
def get_tours_api():
    """
    Get a list of active tours in JSON format.

    Returns:
    - A list of objects with `id` and `name` fields.
    - Only includes tours where `onlineregtype = 2`, `inactive IS NOT TRUE`, and `deleted IS NOT TRUE`.
    """
    return get_tours()
