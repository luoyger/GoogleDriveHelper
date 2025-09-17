from fastapi import APIRouter
from router.google_drive_router import router as google_drive_router
from router.multi_user_router import router as multi_user_router

router = APIRouter()

# Include the Google Drive router (单一账户模式)
router.include_router(google_drive_router)

# Include the Multi-User router (多用户模式)
router.include_router(multi_user_router)

