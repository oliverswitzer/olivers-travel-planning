#!/usr/bin/env bash
# setup.sh — one-time setup for olivers-travel-planning
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
WORKSPACE="$(dirname "$PROJECT_DIR")"
FLIGHTS_MCP_DIR="$WORKSPACE/flights-mcp"

echo "✈️  Oliver's Travel Planning — setup"
echo ""

# 1. Clone flights-mcp if not already present
if [ ! -d "$FLIGHTS_MCP_DIR" ]; then
  echo "📦 Cloning flights-mcp..."
  git clone https://github.com/ravinahp/flights-mcp "$FLIGHTS_MCP_DIR"
else
  echo "✅ flights-mcp already cloned at $FLIGHTS_MCP_DIR"
fi

# 2. Install dependencies
echo "📦 Installing flights-mcp dependencies (uv sync)..."
cd "$FLIGHTS_MCP_DIR"
uv sync
echo "✅ Dependencies installed"

# 3. Check for .env
if [ ! -f "$PROJECT_DIR/.env" ]; then
  echo ""
  echo "⚠️  No .env found. Creating from .env.sample..."
  cp "$PROJECT_DIR/.env.sample" "$PROJECT_DIR/.env"
  echo "👉 Edit $PROJECT_DIR/.env and set your DUFFEL_API_KEY_LIVE"
fi

# 4. Install LaunchAgent (macOS only)
PLIST_SRC="$SCRIPT_DIR/com.travel-planning.serve.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.travel-planning.serve.plist"

if [[ "$(uname)" == "Darwin" ]]; then
  # Stamp in the actual python path
  PYTHON_PATH="$(which python3)"
  sed "s|__PYTHON__|$PYTHON_PATH|g; s|__PROJECT_DIR__|$PROJECT_DIR|g" \
    "$PLIST_SRC" > "$PLIST_DST"

  launchctl unload "$PLIST_DST" 2>/dev/null || true
  launchctl load "$PLIST_DST"
  echo "✅ LaunchAgent installed — server will start on login"
  echo "   http://localhost:3031/"
  echo "   http://100.126.32.92:3031/ (Tailscale)"
else
  echo "ℹ️  Not macOS — skip LaunchAgent. Start manually: python $SCRIPT_DIR/serve.py"
fi

echo ""
echo "🎉 Setup complete! Open Claude Code in $PROJECT_DIR to start planning trips."
