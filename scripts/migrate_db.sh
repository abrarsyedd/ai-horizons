#!/usr/bin/env bash
set -e

echo "=== [DB MIGRATION] Starting schema import ==="

DB_HOST="localhost"
DB_USER="admin"
DB_PASS="admin"
DB_NAME="ai_horizons_db"
SCHEMA_FILE="/home/ubuntu/ai_horizons/schema.sql"

# --- Step 1: Install MySQL if not already installed ---
if ! command -v mysql >/dev/null 2>&1; then
  echo "MySQL not found. Installing..."
  sudo apt-get update -y
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y mysql-server
  sudo systemctl enable mysql
  sudo systemctl start mysql
else
  echo "MySQL already installed."
fi

# --- Step 2: Ensure MySQL service is running ---
echo "Checking MySQL status..."
sudo systemctl start mysql
sleep 3

# --- Step 3: Create DB user and database if needed ---
echo "Ensuring database and user exist..."
sudo mysql -u root <<EOF
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\`;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost';
FLUSH PRIVILEGES;
EOF

# --- Step 4: Import schema if available ---
if [ -f "$SCHEMA_FILE" ]; then
  echo "Importing schema from $SCHEMA_FILE..."
  mysql -h "$DB_HOST" -u"$DB_USER" -p"$DB_PASS" "$DB_NAME" < "$SCHEMA_FILE"
  echo "Schema imported successfully."
else
  echo "⚠️  Schema file not found at $SCHEMA_FILE"
fi

echo "=== [DB MIGRATION] Completed successfully ==="
