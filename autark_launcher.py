#!/usr/bin/env python3
"""
AUTARK SYSTEM LAUNCHER
=====================

Enhanced launcher implementing the "Vom Kies zum Mosaik" philosophy
with integrated onboarding tours and documentation access.

Features:
- Start/stop demo system
- Interactive 30/5/60 minute tours
- Integrated documentation browser
- Enhanced system management

Author: AUTARK System
Version: 2.0.0 - Universal Repository Experience
"""

import sys
import subprocess
import time
from pathlib import Path


class AutarkLauncher:
    """Enhanced launcher for AUTARK system with universal repo experience"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.processes = {}
        self.config = {
            "demo_port": 8888,
            "overlay_port": 8889,
            "orchestrator_port": 8000,
            "video_ai_port": 8890
        }
    
    def show_banner(self):
        """Display AUTARK system banner"""
        banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                   AUTARK SYSTEM LAUNCHER                 ║
    ║          🚀 Vom Kies zum Mosaik - AI Development        ║
    ║                                                          ║
    ║  🎯 30 Sekunden verstehen • 5 Minuten produktiv         ║
    ║                                                          ║
    ║  Commands:                                               ║
    ║    demo     - Start demo system & main dashboard        ║
    ║    video    - Start Video AI Pipeline                   ║
    ║    knowledge- Start Knowledge Integration (AKIS)        ║
    ║    docs     - Open documentation browser                ║
    ║    tour     - Interactive onboarding tour               ║
    ║    stop     - Stop all processes                        ║
    ║    status   - Show detailed system status               ║
    ║    dashboard- Open main dashboard in browser            ║
    ║    help     - Show this help                            ║
    ╚══════════════════════════════════════════════════════════╝
        """
        print(banner)
    
    def check_port(self, port):
        """Check if a port is in use"""
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            return result == 0
        except Exception:
            return False
    
    def start_video_ai(self):
        """Start the Video AI Pipeline"""
        print("🎬 Starting Video AI Pipeline...")
        
        if self.check_port(self.config["video_ai_port"]):
            print(f"✅ Video AI Pipeline already running on port "
                  f"{self.config['video_ai_port']}")
            return True
        
        try:
            video_ai_script = self.base_dir / "autark_video_ai_pipeline.py"
            if not video_ai_script.exists():
                print("❌ autark_video_ai_pipeline.py not found")
                return False
            
            # Start Video AI process
            process = subprocess.Popen(
                [sys.executable, str(video_ai_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir)
            )
            
            self.processes["video_ai"] = process
            
            # Wait a moment and check if it started
            time.sleep(3)
            if process.poll() is None:
                print("✅ Video AI Pipeline started successfully")
                print(f"🎬 Video Dashboard: "
                      f"http://localhost:{self.config['video_ai_port']}")
                return True
            else:
                print("❌ Failed to start Video AI Pipeline")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Video AI Pipeline: {e}")
            return False
    
    def start_knowledge(self):
        """Start the AUTARK Knowledge Integration System"""
        try:
            print("🧠 Starting AUTARK Knowledge Integration System...")
            
            # Check if knowledge script exists
            knowledge_script = self.base_dir / "autark_knowledge_integration.py"
            if not knowledge_script.exists():
                print("❌ autark_knowledge_integration.py not found")
                return False
            
            # Start Knowledge Integration System
            process = subprocess.Popen(
                [sys.executable, str(knowledge_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir)
            )
            
            self.processes["knowledge"] = process
            
            # Wait a moment and check if it started
            time.sleep(3)
            if process.poll() is None:
                print("✅ Knowledge Integration System started successfully")
                print("🧠 KI Agent now has pre-trained expert knowledge!")
                print("📚 Knowledge Base: knowledge_base directory")
                return True
            else:
                print("❌ Failed to start Knowledge Integration System")
                return False
                
        except Exception as e:
            print(f"❌ Error starting Knowledge Integration System: {e}")
            return False
    
    def start_demo(self):
        """Start the AUTARK demo system"""
        print("🚀 Starting AUTARK Demo System...")
        
        if self.check_port(self.config["demo_port"]):
            print(f"✅ Demo system already running on port "
                  f"{self.config['demo_port']}")
            return True
        
        try:
            demo_script = self.base_dir / "autark_demo.py"
            if not demo_script.exists():
                print("❌ autark_demo.py not found")
                return False
            
            # Start demo process
            process = subprocess.Popen(
                [sys.executable, str(demo_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(self.base_dir)
            )
            
            self.processes["demo"] = process
            
            # Wait a moment and check if it started
            time.sleep(2)
            if process.poll() is None:
                print("✅ Demo system started successfully")
                print(f"📊 Dashboard: "
                      f"http://localhost:{self.config['demo_port']}")
                return True
            else:
                print("❌ Failed to start demo system")
                return False
                
        except Exception as e:
            print(f"❌ Error starting demo: {e}")
            return False
    
    def stop_all(self):
        """Stop all AUTARK processes"""
        print("🛑 Stopping all AUTARK processes...")
        
        # Stop tracked processes
        for name, process in self.processes.items():
            try:
                if process.poll() is None:
                    print(f"🔄 Stopping {name}...")
                    process.terminate()
                    process.wait(timeout=5)
                    print(f"✅ {name} stopped")
            except subprocess.TimeoutExpired:
                print(f"⚠️  Force killing {name}...")
                process.kill()
            except Exception as e:
                print(f"❌ Error stopping {name}: {e}")
        
        self.processes.clear()
        
        # Kill any remaining AUTARK processes
        try:
            subprocess.run(
                ["pkill", "-f", "autark"],
                capture_output=True
            )
            print("✅ All AUTARK processes stopped")
        except Exception:
            pass
    
    def show_status(self):
        """Show system status"""
        print("📊 AUTARK System Status")
        print("=" * 50)
        
        # Check ports
        services = [
            ("Demo System", self.config["demo_port"]),
            ("Video AI Pipeline", self.config["video_ai_port"]),
            ("Overlay Dashboard", self.config["overlay_port"]),
            ("Orchestrator API", self.config["orchestrator_port"])
        ]
        
        for service_name, port in services:
            status = "🟢 Running" if self.check_port(port) else "🔴 Stopped"
            print(f"{service_name:20} {status:15} Port: {port}")
        
        # Check Knowledge System
        knowledge_db = self.base_dir / "knowledge_base"
        if knowledge_db.exists():
            print(f"{'Knowledge Base':20} {'🟢 Ready':15} "
                  f"Database: Available")
        else:
            print(f"{'Knowledge Base':20} {'🔴 Not Init':15} "
                  f"Database: Missing")
        
        # Check processes
        print("\n🔄 Tracked Processes:")
        if not self.processes:
            print("   No tracked processes")
        else:
            for name, process in self.processes.items():
                if process.poll() is None:
                    print(f"   {name}: 🟢 Running (PID: {process.pid})")
                else:
                    print(f"   {name}: 🔴 Stopped")
        
        # Check system resources
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            print(f"\n💾 System Resources:")
            print(f"   CPU: {cpu_percent}%")
            print(f"   Memory: {memory.percent}% used")
        except ImportError:
            print("\n💾 System Resources: psutil not available")
    
    def open_docs(self):
        """Open documentation in browser"""
        docs_path = self.base_dir / "docs" / "README.md"
        if docs_path.exists():
            url = ("https://github.com/statesflowwishes-sketch/autark/"
                   "tree/main/docs")
            print(f"📚 Opening documentation: {url}")
            
            try:
                import webbrowser
                webbrowser.open(url)
                print("✅ Documentation opened in browser")
            except Exception:
                print("💡 Please open this URL manually in your browser:")
                print(f"   {url}")
        else:
            print("❌ Documentation not found")
            print("💡 Generate docs first with: python3 -m mkdocs serve")
    
    def start_tour(self):
        """Start interactive onboarding tour"""
        print("🎓 Starting AUTARK Onboarding Tour...")
        print("\n🎯 Welcome to the 30-5-60 Minute Journey!")
        print("   30 seconds: Understand the system")
        print("   5 minutes: Get productive")
        print("   60 minutes: Make your first contribution")
        
        tour_choice = input("\nChoose your tour (30/5/60): ").strip()
        
        if tour_choice == "30":
            self.tour_30_seconds()
        elif tour_choice == "5":
            self.tour_5_minutes()
        elif tour_choice == "60":
            self.tour_60_minutes()
        else:
            print("💡 Starting with 30-second overview...")
            self.tour_30_seconds()
    
    def tour_30_seconds(self):
        """30-second overview tour"""
        print("\n⚡ 30-Second AUTARK Overview")
        print("=" * 40)
        print("🧠 AKIS: Intelligent Knowledge System")
        print("🎬 Video-AI: Multimedia Analysis Pipeline")
        print("🤖 Orchestrator: Coordinated AI Agents")
        print("📊 Dashboard: Real-time System Monitoring")
        print("\n🎯 Result: Integrated AI Development Environment")
        print("💡 Next: Try 'python3 autark_launcher.py demo'")
    
    def tour_5_minutes(self):
        """5-minute hands-on tour"""
        print("\n🏃 5-Minute Hands-On Tour")
        print("=" * 40)
        
        if not self.start_demo():
            print("❌ Could not start demo system")
            return
            
        print("\n✅ Step 1/3: Demo system running")
        print("📊 Dashboard: http://localhost:8888")
        
        input("Press Enter when you've explored the dashboard...")
        
        if not self.start_video_ai():
            print("⚠️ Video-AI not available, skipping...")
        else:
            print("\n✅ Step 2/3: Video-AI active")
            print("🎬 Video Interface: http://localhost:8890")
            
        if not self.start_knowledge():
            print("⚠️ Knowledge system not available, skipping...")
        else:
            print("\n✅ Step 3/3: Knowledge system ready")
            print("🧠 AKIS: Integrated in main dashboard")
            
        print("\n🎉 5-Minute Tour Complete!")
        print("💡 Next: Explore individual components or try 60-minute tour")
        
    def tour_60_minutes(self):
        """60-minute deep dive tour"""
        print("\n🎓 60-Minute Deep Dive")
        print("=" * 40)
        print("📚 This tour covers:")
        print("  • Development setup")
        print("  • Code exploration")
        print("  • First contribution")
        print("\n📖 Follow the guide at:")
        print("   docs/onboarding/quickstart.md")
        print("\n💡 Or visit: "
              "https://github.com/statesflowwishes-sketch/autark/"
              "docs/onboarding")
    
    def open_dashboard(self):
        """Open dashboard in browser"""
        if self.check_port(self.config["demo_port"]):
            url = f"http://localhost:{self.config['demo_port']}"
            print(f"🌐 Opening dashboard: {url}")
            
            # Try different browser opening methods
            try:
                import webbrowser
                webbrowser.open(url)
                print("✅ Browser opened")
            except Exception:
                print("💡 Please open this URL manually in your browser:")
                print(f"   {url}")
        else:
            print("❌ Demo system is not running")
            print("💡 Start it first with: python3 autark_launcher.py demo")

    def run_command(self, command):
        """Execute a command"""
        if command == "demo":
            self.start_demo()
        elif command == "video":
            self.start_video_ai()
        elif command == "knowledge":
            self.start_knowledge()
        elif command == "docs":
            self.open_docs()
        elif command == "tour":
            self.start_tour()
        elif command == "stop":
            self.stop_all()
        elif command == "status":
            self.show_status()
        elif command == "dashboard":
            self.open_dashboard()
        elif command == "help":
            self.show_banner()
        else:
            print(f"❌ Unknown command: {command}")
            print("\n💡 Available commands:")
            print("   demo, video, knowledge, docs, tour")
            print("   stop, status, dashboard, help")
            self.show_banner()
    
    def interactive_mode(self):
        """Run in interactive mode"""
        self.show_banner()
        
        while True:
            try:
                command = input("\n🤖 AUTARK> ").strip().lower()
                
                if command in ["exit", "quit", "q"]:
                    print("👋 Goodbye!")
                    self.stop_all()
                    break
                elif command:
                    self.run_command(command)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                self.stop_all()
                break
            except EOFError:
                break


def main():
    """Main entry point"""
    launcher = AutarkLauncher()
    
    if len(sys.argv) > 1:
        # Command line mode
        command = sys.argv[1].lower()
        launcher.run_command(command)
    else:
        # Interactive mode
        launcher.interactive_mode()


if __name__ == "__main__":
    main()
