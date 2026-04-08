from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.error_handlers import register_error_handlers
from app.presentation.routers import auth, branches, users, tax_rates

app = FastAPI(title="SystemPOS API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_error_handlers(app)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(branches.router, prefix="/branches", tags=["branches"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(tax_rates.router, prefix="/tax-rates", tags=["tax-rates"])


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# Para arrancar el servidor:
#
# source.venv / bin / activate
# uvicorn
# app.main: app - -reload
# # Docs en: http://localhost:8000/docs