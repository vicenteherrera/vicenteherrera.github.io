#!/usr/bin/env python3
import os
import sys
import time
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

class ReloadHandler(SimpleHTTPRequestHandler):
    """HTTP handler that serves files normally."""
    def end_headers(self):
        # Add aggressive cache control headers to prevent all caching
        self.send_header('Cache-Control', 'no-store, no-cache, no-must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        # Always serve fresh content, never use 304 Not Modified
        if self.path == '/':
            self.path = '/index.html'
        
        try:
            file = self.translate_path(self.path)
            if os.path.isdir(file):
                if not self.path.endswith('/'):
                    self.send_response(301)
                    self.send_header('Location', self.path + '/')
                    self.end_headers()
                    return
                for index in 'index.html', 'index.htm':
                    index = os.path.join(file, index)
                    if os.path.exists(index):
                        file = index
                        break
            if os.path.exists(file):
                self.send_response(200)
                self.send_header('Content-type', self.guess_type(file))
                fs = os.stat(file)
                self.send_header('Content-Length', str(fs.st_size))
                self.end_headers()
                with open(file, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404)
        except Exception as e:
            self.send_error(500)

def watch_files():
    """Watch for file changes and print a message to trigger reload."""
    watched_extensions = {'.html', '.css', '.js', '.png'}
    file_times = {}
    
    # Initial scan
    for ext in watched_extensions:
        for file_path in Path('.').glob(f'*{ext}'):
            if file_path.is_file():
                file_times[str(file_path)] = os.path.getmtime(file_path)
    
    while True:
        time.sleep(0.5)
        for ext in watched_extensions:
            for file_path in Path('.').glob(f'*{ext}'):
                if file_path.is_file():
                    file_str = str(file_path)
                    current_time = os.path.getmtime(file_path)
                    if file_str in file_times:
                        if current_time != file_times[file_str]:
                            print(f'\n✓ File changed: {file_str} - refresh your browser\n', flush=True)
                            file_times[file_str] = current_time
                    else:
                        file_times[file_str] = current_time

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    
    # Start file watcher in background thread
    watcher = threading.Thread(target=watch_files, daemon=True)
    watcher.start()
    
    # Start HTTP server
    server = HTTPServer(('', port), ReloadHandler)
    print(f'Starting server at http://localhost:{port}')
    print('Watching for file changes...')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServer stopped.')
        server.shutdown()
