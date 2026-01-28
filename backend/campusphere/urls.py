"""
URL configuration for campusphere project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import FileResponse
from pathlib import Path
import mimetypes

# Frontend path
FRONTEND_DIR = Path(__file__).resolve().parent.parent.parent / 'frontend'

def serve_frontend_file(request, filepath=''):
    """Serve frontend files with correct MIME types"""
    # Default to index.html if no path or directory requested
    if not filepath or filepath.endswith('/'):
        filepath = 'index.html'
    
    file_path = FRONTEND_DIR / filepath
    
    # Security check - ensure file is within frontend directory
    try:
        file_path.resolve().relative_to(FRONTEND_DIR.resolve())
    except ValueError:
        return serve_frontend_file(request, 'index.html')
    
    # If file exists, serve it
    if file_path.exists() and file_path.is_file():
        mime_type, _ = mimetypes.guess_type(str(file_path))
        
        # Ensure JavaScript files are served with correct MIME type
        if filepath.endswith('.js'):
            mime_type = 'application/javascript'
        elif filepath.endswith('.html'):
            mime_type = 'text/html'
        elif filepath.endswith('.css'):
            mime_type = 'text/css'
        elif filepath.endswith('.json'):
            mime_type = 'application/json'
        
        response = FileResponse(open(file_path, 'rb'), content_type=mime_type or 'application/octet-stream')
        # Allow cross-origin for fonts and scripts
        if filepath.endswith(('.js', '.css', '.woff', '.woff2')):
            response['Cross-Origin-Embedder-Policy'] = 'require-corp'
        return response
    
    # For SPA routing, serve index.html for non-existent files (but not for api calls)
    if filepath != 'index.html' and not filepath.startswith('api/'):
        return serve_frontend_file(request, 'index.html')
    
    # Return 404 for API paths that don't exist
    from django.http import JsonResponse
    return JsonResponse({'error': 'Not found'}, status=404)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
]

# Frontend routes (must be last for catch-all)
urlpatterns += [
    path('', serve_frontend_file, name='frontend_root'),
    path('<path:filepath>', serve_frontend_file, name='frontend_files'),
]
