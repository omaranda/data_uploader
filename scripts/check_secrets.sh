#!/bin/bash
# Security check script - Run before committing to verify no secrets are exposed

echo "🔒 Security Check: Scanning for exposed secrets..."
echo "=================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ISSUES_FOUND=0

# Check 1: Verify .env is gitignored
echo -e "\n1. Checking if .env is gitignored..."
if git check-ignore -q .env; then
    echo -e "${GREEN}✓${NC} .env is properly gitignored"
else
    echo -e "${RED}✗${NC} WARNING: .env is NOT gitignored!"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
fi

# Check 2: Verify .env is not tracked
echo -e "\n2. Checking if .env is tracked in git..."
if git ls-files --error-unmatch .env 2>/dev/null; then
    echo -e "${RED}✗${NC} DANGER: .env is tracked in git!"
    echo -e "${YELLOW}  Run: git rm --cached .env${NC}"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓${NC} .env is not tracked"
fi

# Check 3: Scan for potential API keys in tracked files
echo -e "\n3. Scanning for potential hardcoded API keys..."
if git grep -n "pVEoLsguuoY6D3P" -- ':!.env' ':!SECURITY.md' ':!scripts/check_secrets.sh' 2>/dev/null; then
    echo -e "${RED}✗${NC} Found potential API key in tracked files!"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓${NC} No API keys found in tracked files"
fi

# Check 4: Scan for hardcoded URLs
echo -e "\n4. Scanning for hardcoded API endpoints..."
if git grep -n "wm2drzie9x.eu-west-1.awsapprunner.com" -- '*.py' ':!SECURITY.md' ':!.env.example' ':!scripts/check_secrets.sh' 2>/dev/null; then
    echo -e "${RED}✗${NC} Found hardcoded API endpoint in Python files!"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓${NC} No hardcoded endpoints found in Python files"
fi

# Check 5: Verify config files are gitignored
echo -e "\n5. Checking config files..."
TRACKED_CONFIGS=$(git ls-files config_files/*.json 2>/dev/null | grep -v example_config.json)
if [ -n "$TRACKED_CONFIGS" ]; then
    echo -e "${YELLOW}⚠${NC}  Warning: Some config files are tracked:"
    echo "$TRACKED_CONFIGS"
    echo -e "${YELLOW}  These may contain sensitive data${NC}"
else
    echo -e "${GREEN}✓${NC} Only example_config.json is tracked"
fi

# Check 6: Verify .env.example has no real secrets
echo -e "\n6. Checking .env.example for real secrets..."
if grep -q "pVEoLsguuoY6D3P" .env.example 2>/dev/null; then
    echo -e "${RED}✗${NC} .env.example contains real API key!"
    ISSUES_FOUND=$((ISSUES_FOUND + 1))
else
    echo -e "${GREEN}✓${NC} .env.example has placeholder values only"
fi

# Final summary
echo -e "\n=================================================="
if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "${GREEN}✓ All security checks passed!${NC}"
    echo "Safe to commit."
    exit 0
else
    echo -e "${RED}✗ Found $ISSUES_FOUND security issue(s)${NC}"
    echo -e "${YELLOW}Please fix the issues above before committing.${NC}"
    exit 1
fi
