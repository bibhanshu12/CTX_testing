from typing import Optional

from fastapi import FastAPI, HTTPException, Query, Request, UploadFile, File, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.configuration.settings import settings
from app.core.exceptions import CTXError
from app.services.ctx_service import ctx_service
from app.domain.schemas import (
    EntityListItem,
    EntityListResponse,
    RecordsResponse,
    ConnectionStatus,
    ImportMetadataRequest,
    ImportMetadataResponse,
)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

cors_origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.exception_handler(CTXError)
async def ctx_error_handler(request, exc: CTXError):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code,
            "message": exc.message,
            "details": exc.details,
        },
    )


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": settings.app_version,
        "data_source": settings.ctx_data_source,
        "docs": "/docs",
    }


@app.get("/api/ctx/entities", response_model=EntityListResponse)
async def list_entities():
    entities = ctx_service.list_entities()
    return EntityListResponse(
        data_source=settings.ctx_data_source,
        entities=[
            EntityListItem(name=e, path=f"/api/ctx/entities/{e}/records")
            for e in entities
        ],
    )


@app.get("/api/ctx/entities/{entity_set}/metadata")
async def get_entity_metadata(entity_set: str):
    return ctx_service.get_metadata(entity_set)


@app.get("/api/ctx/entities/{entity_set}/records", response_model=RecordsResponse)
async def get_records(
    request: Request,
    entity_set: str,
    top: Optional[int] = Query(default=None, ge=1, le=1000),
    skip: Optional[int] = Query(default=None, ge=0),
    filter: Optional[str] = Query(default=None),
    orderby: Optional[str] = Query(default=None),
):
    qp = request.query_params
    if top is None and "$top" in qp:
        try:
            top = int(qp["$top"])
        except (ValueError, TypeError):
            top = None
    if skip is None and "$skip" in qp:
        try:
            skip = int(qp["$skip"])
        except (ValueError, TypeError):
            skip = None
    if filter is None and "$filter" in qp:
        filter = qp["$filter"]
    if orderby is None and "$orderby" in qp:
        orderby = qp["$orderby"]

    return ctx_service.get_records(
        entity_set=entity_set,
        top=top,
        skip=skip,
        filter=filter,
        orderby=orderby,
    )


@app.get("/api/ctx/status", response_model=ConnectionStatus)
async def connection_status():
    return ctx_service.get_connection_status()


@app.post("/api/ctx/import/metadata", response_model=ImportMetadataResponse)
async def import_metadata(payload: ImportMetadataRequest):
    result = ctx_service.validate_import_metadata(payload.content)
    return ImportMetadataResponse(**result)


@app.post("/api/ctx/import/metadata/file")
async def import_metadata_file(file: UploadFile = File(...)):
    MAX_SIZE = 5 * 1024 * 1024  # 5 MB
    content = await file.read()
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 5 MB size limit.",
        )
    allowed_extensions = (".xml", ".json", ".txt", ".csn", ".edmx")
    if not file.filename or not file.filename.lower().endswith(allowed_extensions):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
        )
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not valid UTF-8 text.",
        )
    result = ctx_service.validate_import_metadata(text)
    return {"filename": file.filename, "size_bytes": len(content), **result}
