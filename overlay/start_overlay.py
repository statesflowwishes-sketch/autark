#!/usr/bin/env python3
"""
Original Overlay Web Server
Zeigt das AUTARK SYSTEM Dashboard an
"""

import sys
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler
import webbrowser
import threading
import time


class OverlayHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(Path(__file__).parent), **kwargs)
    
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()
    
    def log_message(self, format, *args):
        # Unterdrücke Standard-Logs für saubere Ausgabe
        pass


def start_overlay_server():
    """Startet den Original Overlay Web Server"""
    port = 8888
    
    print("🖥️  ORIGINAL OVERLAY")
    print("=" * 50)
    print(f"🌐 Starting web server on port {port}...")
    
    try:
        server = HTTPServer(('localhost', port), OverlayHandler)
        
        # Dashboard URL
        dashboard_url = f"http://localhost:{port}/dashboard.html"
        
        print(f"✅ Server running at: {dashboard_url}")
        print("🎯 AUTARK SYSTEM Dashboard ready!")
        print("=" * 50)
        print("📋 Features:")
        print("   • Real-time system status")
        print("   • Agent monitoring")
        print("   • Database connectivity")
        print("   • Performance metrics")
        print("   • Matrix-style interface")
        print("=" * 50)
        print("Press Ctrl+C to stop server")
        
        # Browser automatisch öffnen
        def open_browser():
            time.sleep(1)
            try:
                webbrowser.open(dashboard_url)
                print(f"🚀 Browser opened: {dashboard_url}")
            except Exception as e:
                print(f"⚠️  Please open manually: {dashboard_url} - {e}")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # Server starten
        server.serve_forever()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Original Overlay server...")
        server.shutdown()
        print("👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    start_overlay_server()
