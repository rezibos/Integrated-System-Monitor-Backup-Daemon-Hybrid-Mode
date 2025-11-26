#!/bin/bash

###############################################################################
# Fix Daemon - One-Shot Boot Mode Setup
# Mengatasi masalah: backup terus-menerus, daemon tidak berhenti
###############################################################################

echo "=============================================="
echo "   FIX: One-Shot Boot Mode Setup"
echo "   Mengatasi: Backup berulang & daemon running"
echo "=============================================="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Script harus dijalankan sebagai root!"
    echo "   Gunakan: sudo bash fix_daemon_oneshot.sh"
    exit 1
fi

# Define paths
BASE_DIR="/home/firaz/SO_LATIHAN/log-monitor"
SERVICE_NAME="integrated-monitor"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

echo "📋 Konfigurasi:"
echo "   Base Dir: $BASE_DIR"
echo "   Service: $SERVICE_NAME"
echo ""

# Step 1: Stop existing service
echo "🛑 Step 1: Stopping existing service..."
systemctl stop $SERVICE_NAME 2>/dev/null
systemctl disable $SERVICE_NAME 2>/dev/null

# Kill any running Python processes
pkill -f integrated_daemon 2>/dev/null

sleep 2
echo "   ✓ Service stopped"
echo ""

# Step 2: Backup old files
echo "💾 Step 2: Backup old files..."
if [ -f "$BASE_DIR/integrated_daemon.py" ]; then
    cp "$BASE_DIR/integrated_daemon.py" "$BASE_DIR/integrated_daemon_OLD.py.backup"
    echo "   ✓ Python file backed up"
fi

if [ -f "$SERVICE_FILE" ]; then
    cp "$SERVICE_FILE" "${SERVICE_FILE}.backup"
    echo "   ✓ Service file backed up"
fi
echo ""

# Step 3: Prompt to clean old backups
echo "🗑️  Step 3: Clean old backup files?"
echo "   Current backup count:"
BACKUP_COUNT=$(ls -1 "$BASE_DIR/output/backups/"*.zip 2>/dev/null | wc -l)
echo "   → $BACKUP_COUNT ZIP files found"
echo ""

if [ $BACKUP_COUNT -gt 5 ]; then
    read -p "   Ada banyak backup. Hapus semua? (y/N): " -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        mkdir -p "$BASE_DIR/backup_archive"
        mv "$BASE_DIR/output/backups/"*.zip "$BASE_DIR/backup_archive/" 2>/dev/null
        echo "   ✓ Backups moved to backup_archive/"
    else
        echo "   ⊘ Skipped cleaning backups"
    fi
else
    echo "   ⊘ Backup count OK, tidak perlu dibersihkan"
fi
echo ""

# Step 4: Check if new Python file exists
echo "📝 Step 4: Checking new Python file..."
if [ ! -f "$BASE_DIR/integrated_daemona.py" ]; then
    echo "   ⚠️  File integrated_daemona.py tidak ditemukan!"
    echo "   Silakan:"
    echo "   1. Buat file: nano $BASE_DIR/integrated_daemona.py"
    echo "   2. Copy code dari artifact 'integrated_daemon_oneshot.py'"
    echo "   3. Save dan jalankan script ini lagi"
    echo ""
    exit 1
else
    chmod +x "$BASE_DIR/integrated_daemona.py"
    echo "   ✓ Python file found and executable"
fi
echo ""

# Step 5: Create/update service file
echo "⚙️  Step 5: Creating systemd service file..."
cat > "$SERVICE_FILE" << EOFSERVICE
[Unit]
Description=Integrated System Monitor and Backup (Boot Once)
Documentation=https://github.com/yourrepo/log-monitor
After=network.target multi-user.target
Wants=network.target

[Service]
Type=oneshot
RemainAfterExit=no
User=root
Group=root
WorkingDirectory=$BASE_DIR
ExecStart=/usr/bin/python3 $BASE_DIR/integrated_daemona.py

# Timeout untuk eksekusi
TimeoutStartSec=300

# Logging
StandardOutput=journal
StandardError=journal
SyslogIdentifier=$SERVICE_NAME

# Security
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOFSERVICE

echo "   ✓ Service file created: $SERVICE_FILE"
echo ""

# Step 6: Reload and enable
echo "🔄 Step 6: Reloading systemd..."
systemctl daemon-reload
echo "   ✓ Daemon reloaded"
echo ""

echo "✅ Step 7: Enabling service for boot..."
systemctl enable $SERVICE_NAME
echo "   ✓ Service enabled"
echo ""

# Step 8: Test run
echo "🧪 Step 8: Test running service..."
echo "   Starting service (this may take 10-30 seconds)..."
echo ""

systemctl start $SERVICE_NAME

# Wait for completion
sleep 5

# Check status
echo "📊 Service Status:"
systemctl status $SERVICE_NAME --no-pager -l
echo ""

# Step 9: Verify outputs
echo "✅ Step 9: Verifying outputs..."
echo ""

if [ -f "$BASE_DIR/output/system_monitor_boot.log" ]; then
    LOG_LINES=$(wc -l < "$BASE_DIR/output/system_monitor_boot.log")
    echo "   ✓ Log file created: $LOG_LINES lines"
else
    echo "   ⚠️  Log file not found"
fi

BACKUP_COUNT_NEW=$(ls -1 "$BASE_DIR/output/backups/"*.zip 2>/dev/null | wc -l)
echo "   ✓ Backup files: $BACKUP_COUNT_NEW"

if [ -f "$BASE_DIR/web/data.json" ]; then
    TOTAL_LOGS=$(grep -oP '"total":\s*\K\d+' "$BASE_DIR/web/data.json" | head -1)
    echo "   ✓ data.json updated: $TOTAL_LOGS total logs"
else
    echo "   ⚠️  data.json not found"
fi

echo ""
echo "=============================================="
echo "   ✅ Setup Selesai!"
echo "=============================================="
echo ""
echo "📋 NEXT STEPS:"
echo ""
echo "1. Reboot untuk test auto-start:"
echo "   sudo reboot"
echo ""
echo "2. Setelah boot, check status:"
echo "   sudo systemctl status $SERVICE_NAME"
echo ""
echo "3. View logs:"
echo "   sudo journalctl -u $SERVICE_NAME -n 50"
echo "   cat $BASE_DIR/output/system_monitor_boot.log"
echo ""
echo "4. Start web dashboard:"
echo "   cd $BASE_DIR/web"
echo "   python3 -m http.server 8080"
echo "   Browser: http://localhost:8080"
echo ""
echo "=============================================="
echo ""
echo "🔍 MONITORING COMMANDS:"
echo "   Status: sudo systemctl status $SERVICE_NAME"
echo "   Logs:   sudo journalctl -u $SERVICE_NAME -f"
echo "   Files:  ls -lh $BASE_DIR/output/backups/"
echo ""
echo "=============================================="