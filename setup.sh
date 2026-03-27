#!/bin/bash

# ============================================================
# Claude Code Website Builder Setup
# One command to install everything you need to build
# stunning animated websites with Claude Code.
#
# What this installs:
#   1. Framer Motion  — animation library
#   2. UI/UX Pro Max  — Claude Code skill for world-class UI
#   3. Magic MCP      — 21st.dev component library for Claude
# ============================================================

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}   Claude Code Website Builder Setup${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""

# ── Step 1: Framer Motion ──────────────────────────────────
echo -e "${YELLOW}[1/3] Installing Framer Motion...${NC}"

if [ -f "package.json" ]; then
  # Detect package manager
  if [ -f "pnpm-lock.yaml" ]; then
    pnpm add framer-motion
  elif [ -f "yarn.lock" ]; then
    yarn add framer-motion
  elif [ -f "bun.lockb" ]; then
    bun add framer-motion
  else
    npm install framer-motion
  fi
  echo -e "${GREEN}✓ Framer Motion installed${NC}"
else
  echo -e "${YELLOW}  No package.json found — skipping Framer Motion.${NC}"
  echo -e "${YELLOW}  Run this from your project root, or install manually:${NC}"
  echo -e "${YELLOW}  npm install framer-motion${NC}"
fi

echo ""

# ── Step 2: UI/UX Pro Max Skill ───────────────────────────
echo -e "${YELLOW}[2/3] Installing UI/UX Pro Max skill...${NC}"

SKILLS_DIR="$HOME/.claude/skills"
SKILL_NAME="ui-ux-pro-max"
SKILL_DIR="$SKILLS_DIR/$SKILL_NAME"
REPO_URL="https://github.com/nextlevelbuilder/ui-ux-pro-max-skill"

mkdir -p "$SKILLS_DIR"

if [ -d "$SKILL_DIR" ]; then
  echo -e "  Skill already exists — pulling latest..."
  git -C "$SKILL_DIR" pull --quiet
else
  # Clone only the .claude/skills folder (sparse checkout)
  git clone --quiet --filter=blob:none --sparse "$REPO_URL" "$SKILL_DIR" 2>/dev/null || \
  git clone --quiet "$REPO_URL" /tmp/ui-ux-pro-max-tmp && \
  cp -r /tmp/ui-ux-pro-max-tmp/.claude/skills/. "$SKILLS_DIR/" && \
  rm -rf /tmp/ui-ux-pro-max-tmp
fi

echo -e "${GREEN}✓ UI/UX Pro Max skill installed at ~/.claude/skills/${NC}"
echo ""

# ── Step 3: 21st.dev Magic MCP ────────────────────────────
echo -e "${YELLOW}[3/3] Installing 21st.dev Magic MCP...${NC}"

# Check for API key argument
MAGIC_API_KEY="${MAGIC_API_KEY:-$1}"

if [ -z "$MAGIC_API_KEY" ]; then
  echo ""
  echo -e "${RED}  Magic MCP needs your 21st.dev API key.${NC}"
  echo -e "  Get it free at: https://21st.dev → Settings → API Keys"
  echo ""
  echo -e "  Then run:"
  echo -e "  ${BLUE}MAGIC_API_KEY=your_key_here bash setup.sh${NC}"
  echo -e "  or:"
  echo -e "  ${BLUE}bash setup.sh your_key_here${NC}"
  echo ""
  echo -e "${YELLOW}  Skipping Magic MCP for now. Everything else is installed.${NC}"
else
  claude mcp add magic --scope user --env API_KEY="$MAGIC_API_KEY"
  echo -e "${GREEN}✓ Magic MCP installed${NC}"
fi

echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}  Setup complete. Start building:${NC}"
echo ""
echo -e "  Tell Claude Code:"
echo -e "  ${BLUE}\"Build me a landing page with smooth animations\"${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
