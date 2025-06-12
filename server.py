import http.server
import socketserver
import webbrowser

PORT = 8000
URL = f"http://localhost:{PORT}/"

Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving at {URL}")
    webbrowser.open(URL)  # ブラウザを自動で開く
    httpd.serve_forever()
