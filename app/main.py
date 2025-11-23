from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from app.routers import auth, classroom, assignments

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include Routers
app.include_router(auth.router)
app.include_router(classroom.router)
app.include_router(assignments.router)

@app.get("/")
async def root():
    return RedirectResponse(url="/static/pages/login.html")

# For development convenience, serve pages directly from root if needed, 
# but sticking to /static/pages/ for now as per structure.
# We can add a redirect for login/register if we want clean URLs.
@app.get("/login")
async def login_page():
    return RedirectResponse(url="/static/pages/login.html")

@app.get("/register")
async def register_page():
    return RedirectResponse(url="/static/pages/register.html")
