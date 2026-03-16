#!/bin/bash
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m'

usage() {
    echo "Usage: bash setup.sh <game-name> <code> [options]"
    echo ""
    echo "  <game-name>    Game name (e.g. \"My Game\")"
    echo "  <code>         2-4 letter project code (e.g. MG)"
    echo ""
    echo "Options:"
    echo "  --reset-git    Reset git history with fresh initial commit"
    echo "  --github       Create GitHub repo (private by default)"
    echo "  --public       Make GitHub repo public (use with --github)"
    echo "  -h, --help     Show this help"
    echo ""
    echo "Examples:"
    echo "  bash setup.sh \"My Game\" MG"
    echo "  bash setup.sh \"My Game\" MG --reset-git --github"
    exit 0
}

# ── Parse args ──────────────────────────────────────────────
GAME_NAME=""
GAME_CODE=""
RESET_GIT=false
CREATE_GITHUB=false
PUBLIC_REPO=false

for arg in "$@"; do
    case "$arg" in
        -h|--help)    usage ;;
        --reset-git)  RESET_GIT=true ;;
        --github)     CREATE_GITHUB=true ;;
        --public)     PUBLIC_REPO=true ;;
        *)
            if [ -z "$GAME_NAME" ]; then
                GAME_NAME="$arg"
            elif [ -z "$GAME_CODE" ]; then
                GAME_CODE="$arg"
            fi
            ;;
    esac
done

if [ -z "$GAME_NAME" ] || [ -z "$GAME_CODE" ]; then
    echo -e "${RED}Error: Game name and code are required.${NC}"
    echo ""
    usage
fi

GAME_CODE=$(echo "$GAME_CODE" | tr '[:lower:]' '[:upper:]')

echo -e "${BLUE}━━━ Game MCP Setup ━━━${NC}"
echo -e "${DIM}Game: ${GAME_NAME} (${GAME_CODE})${NC}"
echo ""

# ── 1. Check prerequisites ─────────────────────────────────
echo -n "Checking uv... "
if ! command -v uv &> /dev/null; then
    echo -e "${RED}NOT FOUND${NC}"
    echo "Error: uv is required. Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi
echo -e "${GREEN}$(uv --version 2>&1)${NC}"

echo -n "Checking python3... "
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}NOT FOUND${NC}"
    echo "Error: Python3 required. Install it first."
    exit 1
fi
echo -e "${GREEN}$(python3 --version 2>&1)${NC}"

# ── 2. Python dependencies via uv ──────────────────────────
echo -n "Installing Python deps... "
if uv sync --quiet 2>/dev/null; then
    echo -e "${GREEN}OK${NC}"
else
    echo -e "${RED}FAILED${NC}"
    echo "Try: uv sync"
    exit 1
fi

# ── 3. MCP config ──────────────────────────────────────────
echo -n "Setting up .mcp.json... "
if [ -f ".mcp.json" ]; then
    echo -e "${DIM}EXISTS (keeping current)${NC}"
else
    cp .mcp.json.example .mcp.json
    echo -e "${GREEN}CREATED${NC}"
    echo -e "  ${BLUE}→ Edit .mcp.json to set your API keys (PIXELLAB_API_TOKEN, etc.)${NC}"
fi

# ── 4. Git reset (optional) ────────────────────────────────
if [ "$RESET_GIT" = true ]; then
    echo -n "Resetting git history... "
    rm -rf .git
    git init -q
    git add -A
    git commit -q -m "Initial commit: $GAME_NAME"
    echo -e "${GREEN}OK${NC}"
fi

# ── 5. GitHub repo (optional) ──────────────────────────────
if [ "$CREATE_GITHUB" = true ]; then
    echo -n "Creating GitHub repo... "
    if command -v gh &> /dev/null; then
        REPO_NAME=$(echo "$GAME_NAME" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
        if [ "$PUBLIC_REPO" = true ]; then
            gh repo create "$REPO_NAME" --public --source . --push 2>/dev/null
        else
            gh repo create "$REPO_NAME" --private --source . --push 2>/dev/null
        fi
        echo -e "${GREEN}OK${NC}"
    else
        echo -e "${RED}FAILED${NC} ${DIM}(gh CLI not found)${NC}"
    fi
fi

# ── Done ────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}━━━ Setup complete! ━━━${NC}"
echo ""
echo "Next steps:"
echo "  1. code ."
echo "  2. Open Claude Code"
echo "  3. Type /lead"
