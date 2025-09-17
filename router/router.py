from fastapi import APIRouter
from router.google_drive_router import router as google_drive_router

router = APIRouter()

# Include the Google Drive router
router.include_router(google_drive_router)

