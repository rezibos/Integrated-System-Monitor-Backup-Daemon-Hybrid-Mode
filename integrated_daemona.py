import os
import json
import subprocess
import zipfile
import time
import signal
from datetime import datetime

class EnhancedDaemon:
    def __init__(self):
        self.running = True
        
        # --- PATH CONFIG ---
        self.base_dir = '/home/firaz/SO_LATIHAN/log-monitor'
        self.backup_source = '/home/firaz/Downloads/Data Dumy Back Up'
        
        # Output
        self.output_dir = os.path.join(self.base_dir, 'output')
        self.backup_dir = os.path.join(self.output_dir, 'backups')
        self.logs_dir = os.path.join(self.output_dir, 'logs')
        self.json_output = os.path.join(self.base_dir, 'web', 'data.json')
        self.update_log = os.path.join(self.logs_dir, f'updates_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        # Init Dirs
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(self.logs_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.json_output), exist_ok=True)

        # Signal Handler
        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, signum, frame):
        self.log("🛑 Stopping daemon...")
        self.running = False

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] {message}")

    # --- REAL TIME TASKS ---
    def get_cpu_usage(self):
        try:
            with open('/proc/stat', 'r') as f:
                line1 = f.readline()
            time.sleep(1)
            with open('/proc/stat', 'r') as f:
                line2 = f.readline()

            p1 = [int(x) for x in line1.split()[1:]]
            p2 = [int(x) for x in line2.split()[1:]]

            busy1 = sum(p1[0:3]) + sum(p1[5:8])
            total1 = sum(p1)
            busy2 = sum(p2[0:3]) + sum(p2[5:8])
            total2 = sum(p2)

            delta_total = total2 - total1
            if delta_total == 0: return 0
            
            delta_busy = busy2 - busy1
            return round((delta_busy / delta_total) * 100, 1)
        except:
            return 0

    def get_memory_usage(self):
        try:
            mem = {}
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    parts = line.split(':')
                    if len(parts) == 2:
                        mem[parts[0]] = int(parts[1].split()[0])

            total = mem.get('MemTotal', 1)
            avail = mem.get('MemAvailable', 0)
            used = total - avail
            
            return {
                'percent': round((used / total) * 100, 1),
                'used_gb': round(used / (1024*1024), 2),
                'total_gb': round(total / (1024*1024), 2)
            }
        except:
            return {'percent': 0, 'used_gb': 0, 'total_gb': 0}

    def get_disk_usage(self):
        try:
            result = subprocess.run(['df', '-h', '/'], capture_output=True, text=True)
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                return {
                    'total': parts[1],
                    'used': parts[2],
                    'available': parts[3],
                    'percent': parts[4].replace('%', '')
                }
        except:
            pass
        return {'total': '0G', 'used': '0G', 'available': '0G', 'percent': '0'}

    def get_uptime(self):
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_seconds = float(f.readline().split()[0])
                hours = int(uptime_seconds // 3600)
                minutes = int((uptime_seconds % 3600) // 60)
                return f"{hours}h {minutes}m"
        except:
            return "N/A"

    # --- ONE SHOT TASKS ---
    def check_updates_once(self):
        self.log("🔍 Checking updates (One-Time)...")
        packages = []
        distro = "Unknown"
        
        try:
            # Detect distro
            is_arch = os.path.exists('/etc/arch-release')
            is_debian = os.path.exists('/etc/debian_version')
            
            if is_arch:
                distro = "Arch Linux"
                cmd = ['checkupdates'] if os.path.exists('/usr/bin/checkupdates') else ['pacman', '-Qu']
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.stdout:
                    for line in res.stdout.strip().split('\n'):
                        p = line.split()
                        if len(p) >= 4:
                            packages.append({
                                'name': p[0],
                                'current': p[1],
                                'new': p[3]
                            })
            elif is_debian:
                distro = "Debian/Ubuntu"
                res = subprocess.run(['apt', 'list', '--upgradable'], capture_output=True, text=True)
                if res.stdout:
                    for line in res.stdout.split('\n'):
                        if '/' in line and 'Listing' not in line:
                            parts = line.split('/')
                            if len(parts) > 0:
                                name = parts[0]
                                version = line.split()[1] if len(line.split()) > 1 else 'available'
                                packages.append({
                                    'name': name,
                                    'current': 'installed',
                                    'new': version
                                })
            
            # Write to log file
            self.write_update_log(packages, distro)
            
        except Exception as e:
            self.log(f"Update check failed: {e}")
        
        return {
            'count': len(packages),
            'list': packages,
            'distro': distro,
            'log_file': os.path.basename(self.update_log)
        }

    def write_update_log(self, packages, distro):
        """Write update information to log file"""
        try:
            with open(self.update_log, 'w') as f:
                f.write("="*70 + "\n")
                f.write(f"  SYSTEM UPDATE CHECK REPORT\n")
                f.write(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"  Distribution: {distro}\n")
                f.write("="*70 + "\n\n")
                
                if len(packages) == 0:
                    f.write("✅ System is fully updated!\n")
                    f.write("No packages require updates at this time.\n")
                else:
                    f.write(f"⚠️  {len(packages)} package(s) available for update:\n\n")
                    f.write(f"{'Package Name':<30} {'Current':<20} {'New Version':<20}\n")
                    f.write("-"*70 + "\n")
                    
                    for pkg in packages:
                        f.write(f"{pkg['name']:<30} {pkg['current']:<20} {pkg['new']:<20}\n")
                    
                    f.write("\n" + "="*70 + "\n")
                    f.write("HOW TO UPDATE:\n")
                    if 'Arch' in distro:
                        f.write("  sudo pacman -Syu\n")
                    else:
                        f.write("  sudo apt update && sudo apt upgrade\n")
                    f.write("="*70 + "\n")
            
            self.log(f"✅ Update log written: {self.update_log}")
        except Exception as e:
            self.log(f"Failed to write update log: {e}")

    def perform_backup_once(self):
        self.log("📦 Performing Boot Backup (One-Time)...")
        if not os.path.exists(self.backup_source):
            return {'status': 'error', 'msg': 'Source not found'}

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.zip"
        filepath = os.path.join(self.backup_dir, filename)

        try:
            file_count = 0
            with zipfile.ZipFile(filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.backup_source):
                    for file in files:
                        p = os.path.join(root, file)
                        zipf.write(p, os.path.relpath(p, self.backup_source))
                        file_count += 1
            
            size_mb = round(os.path.getsize(filepath) / (1024*1024), 2)
            self.log(f"✅ Backup finished: {filename}")
            return {
                'status': 'success',
                'filename': filename,
                'size': f"{size_mb} MB",
                'files': file_count,
                'timestamp': timestamp
            }
        except Exception as e:
            return {'status': 'error', 'msg': str(e)}

    def get_backup_history(self):
        history = []
        if os.path.exists(self.backup_dir):
            files = sorted([f for f in os.listdir(self.backup_dir) if f.endswith('.zip')], reverse=True)
            for f in files[:10]:  # Last 10 backups
                p = os.path.join(self.backup_dir, f)
                stat = os.stat(p)
                history.append({
                    'name': f,
                    'size': f"{round(stat.st_size/(1024*1024), 2)} MB",
                    'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        return history

    def get_recent_update_logs(self):
        """Get list of recent update log files"""
        logs = []
        if os.path.exists(self.logs_dir):
            files = sorted([f for f in os.listdir(self.logs_dir) if f.startswith('updates_')], reverse=True)
            for f in files[:5]:  # Last 5 logs
                p = os.path.join(self.logs_dir, f)
                stat = os.stat(p)
                logs.append({
                    'name': f,
                    'size': f"{round(stat.st_size/1024, 2)} KB",
                    'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                })
        return logs

    def run(self):
        self.log("🚀 Enhanced Daemon Started")
        
        # 1. BOOT TASKS (ONE TIME)
        self.log("📋 Running boot tasks...")
        static_updates = self.check_updates_once()
        static_backup = self.perform_backup_once()
        static_history = self.get_backup_history()
        update_logs = self.get_recent_update_logs()
        
        boot_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.log("✅ Boot tasks completed. Starting real-time monitor...")

        # 2. REAL-TIME MONITORING LOOP
        while self.running:
            # Real-time metrics
            cpu = self.get_cpu_usage()  # This sleeps 1 second
            ram = self.get_memory_usage()
            disk = self.get_disk_usage()
            uptime = self.get_uptime()
            
            # Combine all data
            data = {
                'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'boot_time': boot_time,
                'uptime': uptime,
                'system': {
                    'hostname': os.uname().nodename,
                    'kernel': os.uname().release,
                    'arch': os.uname().machine
                },
                'resources': {
                    'cpu': cpu,
                    'ram': ram,
                    'disk': disk
                },
                'updates': static_updates,
                'backup': {
                    'current': static_backup,
                    'history': static_history
                },
                'logs': {
                    'update_logs': update_logs
                }
            }

            # Write to JSON
            try:
                with open(self.json_output, 'w') as f:
                    json.dump(data, f, indent=2)
            except Exception as e:
                print(f"Error writing JSON: {e}")

if __name__ == "__main__":
    daemon = EnhancedDaemon()
    daemon.run()