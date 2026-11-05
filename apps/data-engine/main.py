import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import mapping, etl, simulation, demo

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Motor de Dados & Analytics para o SprintLens: Medallion Pipeline, Reconhecimento de Colunas e Simulação de Monte Carlo.",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include route modules
app.include_router(mapping.router)
app.include_router(etl.router)
app.include_router(simulation.router)
app.include_router(demo.router)

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
    )

