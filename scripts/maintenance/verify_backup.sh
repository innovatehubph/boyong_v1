#!/bin/bash

# Pareng Boyong Backup Verification Script
# Verifies backup integrity and completeness
# Usage: ./verify_backup.sh --backup=backup_directory [--detailed]

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Verification configuration
BACKUP_PATH=""
DETAILED_CHECK=false
CRITICAL_FILES=(
    "backup_info.json"
    "RESTORE_INSTRUCTIONS.md"
    "config/.env"
    "code/python"
    "code/prompts"
    "webui"
)

# Parse arguments
for arg in "$@"; do
    case $arg in
        --backup=*)
            BACKUP_PATH="${arg#*=}"
            shift
            ;;
        --detailed)
            DETAILED_CHECK=true
            shift
            ;;
        --help)
            echo "Usage: $0 --backup=backup_directory [--detailed]"
            echo "  --backup=PATH     Path to backup directory or archive"
            echo "  --detailed        Perform detailed file integrity checks"
            exit 0
            ;;
    esac
done

# List available backups if none specified
if [ -z "$BACKUP_PATH" ]; then
    echo -e "${BLUE}Available backups:${NC}"
    if [ -d "backups" ]; then
        find backups -name "backup_*" -type d | sort -r | while read backup; do
            if [ -f "$backup/backup_info.json" ]; then
                date_info=""
                if command -v jq &> /dev/null; then
                    date_info=$(jq -r '.date' "$backup/backup_info.json" 2>/dev/null | head -c 20)
                fi
                echo -e "  ${GREEN}$backup${NC} ${YELLOW}($date_info)${NC}"
            else
                echo -e "  ${RED}$backup${NC} (invalid)"
            fi
        done
        
        # Check for archives
        find backups -name "backup_*.tar.gz" -type f | sort -r | while read archive; do
            echo -e "  ${CYAN}$archive${NC} (archive)"
        done
    else
        echo -e "${YELLOW}  No backups directory found${NC}"
    fi
    
    echo -e "\nUsage: $0 --backup=backup_directory"
    exit 0
fi

# Handle compressed archives
TEMP_DIR=""
if [[ "$BACKUP_PATH" == *.tar.gz ]]; then
    echo -e "${YELLOW}Extracting archive for verification...${NC}"
    TEMP_DIR="/tmp/verify_$(date +%s)"
    mkdir -p "$TEMP_DIR"
    tar -xzf "$BACKUP_PATH" -C "$TEMP_DIR"
    BACKUP_PATH="$TEMP_DIR/$(ls "$TEMP_DIR")"
fi

# Verify backup exists
if [ ! -d "$BACKUP_PATH" ]; then
    echo -e "${RED}Error: Backup directory not found: $BACKUP_PATH${NC}"
    exit 1
fi

echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}       Pareng Boyong Backup Verification${NC}"
echo -e "${CYAN}       Verifying: $(basename "$BACKUP_PATH")${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

# Initialize counters
TOTAL_CHECKS=0
PASSED_CHECKS=0
WARNINGS=0
ERRORS=0

# Function to report check result
report_check() {
    local check_name=$1
    local status=$2
    local message=$3
    
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    
    case $status in
        "PASS")
            echo -e "  ${GREEN}✓${NC} $check_name"
            PASSED_CHECKS=$((PASSED_CHECKS + 1))
            ;;
        "WARN")
            echo -e "  ${YELLOW}⚠${NC} $check_name ${YELLOW}($message)${NC}"
            WARNINGS=$((WARNINGS + 1))
            ;;
        "FAIL")
            echo -e "  ${RED}✗${NC} $check_name ${RED}($message)${NC}"
            ERRORS=$((ERRORS + 1))
            ;;
    esac
}

# 1. Basic structure verification
echo -e "${BLUE}[1/6] Basic Structure Verification${NC}"

for file in "${CRITICAL_FILES[@]}"; do
    if [ -e "$BACKUP_PATH/$file" ]; then
        report_check "$file" "PASS"
    else
        report_check "$file" "FAIL" "Missing critical file"
    fi
done

# 2. Backup metadata verification
echo -e "\n${BLUE}[2/6] Backup Metadata Verification${NC}"

if [ -f "$BACKUP_PATH/backup_info.json" ]; then
    # Check if JSON is valid
    if command -v jq &> /dev/null; then
        if jq . "$BACKUP_PATH/backup_info.json" >/dev/null 2>&1; then
            report_check "JSON validity" "PASS"
            
            # Extract metadata
            backup_date=$(jq -r '.date' "$BACKUP_PATH/backup_info.json" 2>/dev/null)
            backup_size=$(jq -r '.backup_size' "$BACKUP_PATH/backup_info.json" 2>/dev/null)
            git_commit=$(jq -r '.git_commit' "$BACKUP_PATH/backup_info.json" 2>/dev/null)
            
            echo -e "${YELLOW}    Date: $backup_date${NC}"
            echo -e "${YELLOW}    Size: $backup_size${NC}"
            echo -e "${YELLOW}    Git:  $git_commit${NC}"
        else
            report_check "JSON validity" "FAIL" "Invalid JSON format"
        fi
    else
        report_check "JSON validity" "WARN" "jq not available for validation"
    fi
    
    # Check restore instructions exist
    if [ -f "$BACKUP_PATH/RESTORE_INSTRUCTIONS.md" ]; then
        report_check "Restore instructions" "PASS"
    else
        report_check "Restore instructions" "WARN" "Missing restore guide"
    fi
else
    report_check "Backup metadata" "FAIL" "No backup_info.json found"
fi

# 3. Configuration verification
echo -e "\n${BLUE}[3/6] Configuration Files Verification${NC}"

if [ -d "$BACKUP_PATH/config" ]; then
    # Check environment file
    if [ -f "$BACKUP_PATH/config/.env" ]; then
        env_lines=$(wc -l < "$BACKUP_PATH/config/.env")
        if [ "$env_lines" -gt 10 ]; then
            report_check "Environment config" "PASS"
        else
            report_check "Environment config" "WARN" "File seems incomplete ($env_lines lines)"
        fi
    else
        report_check "Environment config" "FAIL" "Missing .env file"
    fi
    
    # Check Python requirements
    if [ -f "$BACKUP_PATH/config/requirements.txt" ]; then
        req_count=$(wc -l < "$BACKUP_PATH/config/requirements.txt")
        report_check "Python requirements" "PASS" "$req_count packages"
    else
        report_check "Python requirements" "WARN" "No requirements.txt"
    fi
    
    # Check settings
    if [ -d "$BACKUP_PATH/config/tmp" ]; then
        report_check "Application settings" "PASS"
    else
        report_check "Application settings" "WARN" "No settings directory"
    fi
else
    report_check "Config directory" "FAIL" "Config directory missing"
fi

# 4. Code verification
echo -e "\n${BLUE}[4/6] Code Files Verification${NC}"

if [ -d "$BACKUP_PATH/code" ]; then
    # Python code
    if [ -d "$BACKUP_PATH/code/python" ]; then
        python_files=$(find "$BACKUP_PATH/code/python" -name "*.py" | wc -l)
        if [ "$python_files" -gt 0 ]; then
            report_check "Python code" "PASS" "$python_files files"
        else
            report_check "Python code" "WARN" "No Python files found"
        fi
    else
        report_check "Python code" "FAIL" "Python directory missing"
    fi
    
    # Prompts
    if [ -d "$BACKUP_PATH/code/prompts" ]; then
        prompt_files=$(find "$BACKUP_PATH/code/prompts" -name "*.md" | wc -l)
        if [ "$prompt_files" -gt 0 ]; then
            report_check "Prompt files" "PASS" "$prompt_files files"
        else
            report_check "Prompt files" "WARN" "No prompt files found"
        fi
    else
        report_check "Prompt files" "FAIL" "Prompts directory missing"
    fi
    
    # Tools
    if [ -d "$BACKUP_PATH/code/python/tools" ]; then
        tool_count=$(find "$BACKUP_PATH/code/python/tools" -name "*.py" | wc -l)
        report_check "Tool files" "PASS" "$tool_count tools"
    else
        report_check "Tool files" "WARN" "Tools directory missing"
    fi
else
    report_check "Code directory" "FAIL" "Code directory missing"
fi

# 5. Web UI verification
echo -e "\n${BLUE}[5/6] Web Interface Verification${NC}"

if [ -d "$BACKUP_PATH/webui" ]; then
    # Check for key web files
    html_files=$(find "$BACKUP_PATH/webui" -name "*.html" | wc -l)
    js_files=$(find "$BACKUP_PATH/webui" -name "*.js" | wc -l)
    css_files=$(find "$BACKUP_PATH/webui" -name "*.css" | wc -l)
    
    if [ "$html_files" -gt 0 ]; then
        report_check "HTML files" "PASS" "$html_files files"
    else
        report_check "HTML files" "WARN" "No HTML files found"
    fi
    
    if [ "$js_files" -gt 0 ]; then
        report_check "JavaScript files" "PASS" "$js_files files"
    else
        report_check "JavaScript files" "WARN" "No JS files found"
    fi
    
    if [ "$css_files" -gt 0 ]; then
        report_check "CSS files" "PASS" "$css_files files"
    else
        report_check "CSS files" "WARN" "No CSS files found"
    fi
else
    report_check "WebUI directory" "FAIL" "WebUI directory missing"
fi

# 6. Detailed integrity checks
echo -e "\n${BLUE}[6/6] File Integrity Verification${NC}"

# Calculate backup size
if [ -d "$BACKUP_PATH" ]; then
    actual_size=$(du -sh "$BACKUP_PATH" | cut -f1)
    report_check "Backup accessibility" "PASS" "Size: $actual_size"
else
    report_check "Backup accessibility" "FAIL" "Cannot access backup"
fi

# Check for empty files
if [ "$DETAILED_CHECK" = true ]; then
    echo -e "\n${YELLOW}Detailed Integrity Check:${NC}"
    
    empty_files=$(find "$BACKUP_PATH" -type f -empty | wc -l)
    if [ "$empty_files" -eq 0 ]; then
        report_check "Empty files check" "PASS" "No empty files"
    else
        report_check "Empty files check" "WARN" "$empty_files empty files found"
        if [ "$empty_files" -lt 10 ]; then
            find "$BACKUP_PATH" -type f -empty | sed 's/^/    /'
        fi
    fi
    
    # Check for very large files that might be corrupted
    large_files=$(find "$BACKUP_PATH" -type f -size +100M | wc -l)
    if [ "$large_files" -gt 0 ]; then
        report_check "Large files check" "WARN" "$large_files files >100MB (check if expected)"
    else
        report_check "Large files check" "PASS" "No unexpectedly large files"
    fi
fi

# Git information verification
if [ -f "$BACKUP_PATH/git_commit_hash.txt" ]; then
    commit_hash=$(cat "$BACKUP_PATH/git_commit_hash.txt")
    if [ ${#commit_hash} -eq 40 ] || [ "$commit_hash" = "No git commit" ]; then
        report_check "Git state" "PASS" "$commit_hash"
    else
        report_check "Git state" "WARN" "Unusual git hash format"
    fi
else
    report_check "Git state" "WARN" "No git information"
fi

# Clean up temp directory if used
if [ -n "$TEMP_DIR" ] && [ -d "$TEMP_DIR" ]; then
    rm -rf "$TEMP_DIR"
fi

# Summary
echo -e "\n${CYAN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${CYAN}         Backup Verification Summary${NC}"
echo -e "${CYAN}═══════════════════════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Results:${NC}"
echo -e "  Total Checks:   ${CYAN}$TOTAL_CHECKS${NC}"
echo -e "  Passed:         ${GREEN}$PASSED_CHECKS${NC}"
echo -e "  Warnings:       ${YELLOW}$WARNINGS${NC}"
echo -e "  Errors:         ${RED}$ERRORS${NC}"

# Overall status
if [ "$ERRORS" -eq 0 ]; then
    if [ "$WARNINGS" -eq 0 ]; then
        echo -e "\n${GREEN}✓ BACKUP IS COMPLETE AND VALID${NC}"
        echo -e "${GREEN}  This backup should restore successfully.${NC}"
    else
        echo -e "\n${YELLOW}⚠ BACKUP IS USABLE WITH WARNINGS${NC}"
        echo -e "${YELLOW}  Backup can be restored but may be missing some components.${NC}"
    fi
else
    echo -e "\n${RED}✗ BACKUP HAS CRITICAL ISSUES${NC}"
    echo -e "${RED}  This backup may not restore properly.${NC}"
    echo -e "${RED}  Consider creating a new backup from current system.${NC}"
fi

# Restoration recommendation
echo -e "\n${BLUE}Restoration Command:${NC}"
echo -e "  ${CYAN}./restore_production.sh --backup=$BACKUP_PATH${NC}"

exit $ERRORS