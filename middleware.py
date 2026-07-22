from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request:Request,call_next):
        response = await call_next(request)
        protected_paths = (
            "/feed",
            "/users/profile",
            "/users/settings",
            "/posts/my_posts",
            "/posts/saved",
            "/posts/create",
        )
        if request.url.path.startswith(protected_paths):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    