"""Point d'entree FastAPI - assemble les routers de chaque module domaine."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.annexes.router import router as annexes_router
from app.auth.router import router as auth_router
from app.core.config import get_settings
from app.geolocation.router import router as geolocation_router
from app.ingestion.router import router as ingestion_router
from app.material_invoices.router import router as material_invoices_router
from app.model_generation.router import router as model_generation_router
from app.questionnaire.router import router as questionnaire_router
from app.thermal_engine.router import router as thermal_engine_router
from app.vision_analysis.router import router as vision_analysis_router
from app.wall_profiles.router import router as wall_profiles_router

settings = get_settings()

app = FastAPI(
    title="ArchI3D API",
    description="Backend de reconstruction 3D hybride et d'analyse thermique/energetique.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Fichiers uploades/generes en stockage local (photos, plans, GLB...). Non utilise si
# STORAGE_BACKEND=r2 (les fichiers sont alors servis directement depuis Cloudflare R2).
app.mount("/files", StaticFiles(directory=settings.storage_path, check_dir=False), name="files")

# Assets illustratifs du catalogue de types de construction (ossature bois, ITE, monomur...).
_reference_assets_dir = Path(__file__).parent / "thermal_engine" / "reference_data" / "assets"
app.mount("/reference-assets", StaticFiles(directory=_reference_assets_dir), name="reference-assets")

app.include_router(auth_router)
app.include_router(ingestion_router)
app.include_router(geolocation_router)
app.include_router(annexes_router)
app.include_router(vision_analysis_router)
app.include_router(model_generation_router)
app.include_router(material_invoices_router)
app.include_router(thermal_engine_router)
app.include_router(questionnaire_router)
app.include_router(wall_profiles_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
