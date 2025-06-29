#!/bin/bash

# RSMT CI/CD Pipeline Status Monitor
# This script provides real-time monitoring of the CI/CD pipeline status

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
METRICS_DIR="${PROJECT_ROOT}/metrics"
LOGS_DIR="${PROJECT_ROOT}/logs"
TEMP_DIR="/tmp/rsmt_monitor"

# Create necessary directories
mkdir -p "${METRICS_DIR}" "${LOGS_DIR}" "${TEMP_DIR}"

# Function to display header
show_header() {
    clear
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║                     RSMT CI/CD Pipeline Monitor                             ║${NC}"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "${BLUE}Last Update: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo ""
}

# Function to check GitHub Actions status
check_github_actions() {
    echo -e "${YELLOW}📋 GitHub Actions Status${NC}"
    echo "─────────────────────────"
    
    # Check if we have GitHub CLI installed
    if command -v gh &> /dev/null; then
        # Get workflow runs
        if gh api repos/:owner/:repo/actions/runs --paginate --jq '.workflow_runs[0:5] | .[] | {status: .status, conclusion: .conclusion, name: .name, created_at: .created_at}' 2>/dev/null; then
            echo ""
        else
            echo -e "${YELLOW}⚠️  GitHub CLI not authenticated or repository not accessible${NC}"
            echo ""
        fi
    else
        echo -e "${YELLOW}⚠️  GitHub CLI (gh) not installed${NC}"
        echo "   Install with: https://cli.github.com/"
        echo ""
    fi
}

# Function to check local pipeline health
check_local_health() {
    echo -e "${YELLOW}🏥 Local Pipeline Health${NC}"
    echo "─────────────────────────"
    
    # Check if health check script exists and run it
    if [[ -f "${PROJECT_ROOT}/tools/ci_cd/health_check.py" ]]; then
        cd "${PROJECT_ROOT}"
        python tools/ci_cd/health_check.py --json > "${TEMP_DIR}/health_status.json" 2>/dev/null || true
        
        if [[ -f "${TEMP_DIR}/health_status.json" ]]; then
            local overall_status=$(jq -r '.overall_status' "${TEMP_DIR}/health_status.json" 2>/dev/null || echo "unknown")
            local critical_count=$(jq -r '.critical_issues | length' "${TEMP_DIR}/health_status.json" 2>/dev/null || echo "0")
            local warning_count=$(jq -r '.warnings | length' "${TEMP_DIR}/health_status.json" 2>/dev/null || echo "0")
            
            case "$overall_status" in
                "excellent") echo -e "  Overall Status: ${GREEN}🟢 EXCELLENT${NC}" ;;
                "good") echo -e "  Overall Status: ${GREEN}🟡 GOOD${NC}" ;;
                "fair") echo -e "  Overall Status: ${YELLOW}🟠 FAIR${NC}" ;;
                "poor") echo -e "  Overall Status: ${RED}🔴 POOR${NC}" ;;
                "critical") echo -e "  Overall Status: ${RED}🚨 CRITICAL${NC}" ;;
                *) echo -e "  Overall Status: ${YELLOW}❓ UNKNOWN${NC}" ;;
            esac
            
            echo -e "  Critical Issues: ${RED}${critical_count}${NC}"
            echo -e "  Warnings: ${YELLOW}${warning_count}${NC}"
        else
            echo -e "  ${RED}❌ Health check failed${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  Health check script not found${NC}"
    fi
    echo ""
}

# Function to check test status
check_test_status() {
    echo -e "${YELLOW}🧪 Test Status${NC}"
    echo "─────────────────"
    
    cd "${PROJECT_ROOT}"
    
    # Quick test discovery
    if command -v pytest &> /dev/null; then
        local test_count=$(pytest --co -q 2>/dev/null | grep -E "tests? collected" | head -1 | awk '{print $1}' || echo "0")
        echo -e "  Total Tests: ${BLUE}${test_count}${NC}"
        
        # Quick test run (dry run style)
        echo -e "  Running quick test check..."
        if timeout 30s pytest --maxfail=1 -x -q > "${TEMP_DIR}/test_output.log" 2>&1; then
            echo -e "  Status: ${GREEN}✅ PASSING${NC}"
        else
            echo -e "  Status: ${RED}❌ FAILING${NC}"
            echo -e "  ${YELLOW}Check ${TEMP_DIR}/test_output.log for details${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  pytest not available${NC}"
    fi
    echo ""
}

# Function to check code quality
check_code_quality() {
    echo -e "${YELLOW}🔍 Code Quality${NC}"
    echo "─────────────────"
    
    cd "${PROJECT_ROOT}"
    
    # Check various quality tools
    local tools=("black" "isort" "flake8" "mypy" "bandit")
    local available_tools=0
    local passing_tools=0
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            ((available_tools++))
            echo -n "  $tool: "
            
            case "$tool" in
                "black")
                    if black --check . > /dev/null 2>&1; then
                        echo -e "${GREEN}✅${NC}"
                        ((passing_tools++))
                    else
                        echo -e "${YELLOW}⚠️${NC}"
                    fi
                    ;;
                "isort")
                    if isort --check-only . > /dev/null 2>&1; then
                        echo -e "${GREEN}✅${NC}"
                        ((passing_tools++))
                    else
                        echo -e "${YELLOW}⚠️${NC}"
                    fi
                    ;;
                "flake8")
                    if flake8 --count > /dev/null 2>&1; then
                        echo -e "${GREEN}✅${NC}"
                        ((passing_tools++))
                    else
                        echo -e "${YELLOW}⚠️${NC}"
                    fi
                    ;;
                "mypy")
                    if mypy rsmt > /dev/null 2>&1; then
                        echo -e "${GREEN}✅${NC}"
                        ((passing_tools++))
                    else
                        echo -e "${YELLOW}⚠️${NC}"
                    fi
                    ;;
                "bandit")
                    if bandit -r . -f json > /dev/null 2>&1; then
                        echo -e "${GREEN}✅${NC}"
                        ((passing_tools++))
                    else
                        echo -e "${YELLOW}⚠️${NC}"
                    fi
                    ;;
            esac
        fi
    done
    
    if [[ $available_tools -gt 0 ]]; then
        local percentage=$((passing_tools * 100 / available_tools))
        echo -e "  Quality Score: ${BLUE}${percentage}%${NC} (${passing_tools}/${available_tools})"
    else
        echo -e "  ${YELLOW}⚠️  No quality tools available${NC}"
    fi
    echo ""
}

# Function to check resource usage
check_resources() {
    echo -e "${YELLOW}💻 Resource Usage${NC}"
    echo "──────────────────"
    
    # CPU usage
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | sed 's/%us,//' || echo "N/A")
    echo -e "  CPU Usage: ${BLUE}${cpu_usage}${NC}"
    
    # Memory usage
    local mem_info=$(free -m | awk 'NR==2{printf "%.1f%% (%dMB/%dMB)", $3*100/$2, $3, $2}')
    echo -e "  Memory Usage: ${BLUE}${mem_info}${NC}"
    
    # Disk usage (project directory)
    local disk_usage=$(du -sh "${PROJECT_ROOT}" 2>/dev/null | awk '{print $1}' || echo "N/A")
    echo -e "  Project Size: ${BLUE}${disk_usage}${NC}"
    
    # Docker usage (if available)
    if command -v docker &> /dev/null; then
        local docker_images=$(docker images --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}" 2>/dev/null | grep -v "REPOSITORY" | wc -l || echo "0")
        echo -e "  Docker Images: ${BLUE}${docker_images}${NC}"
    fi
    echo ""
}

# Function to check recent activity
check_recent_activity() {
    echo -e "${YELLOW}📈 Recent Activity${NC}"
    echo "──────────────────"
    
    cd "${PROJECT_ROOT}"
    
    # Recent commits
    if git rev-parse --git-dir > /dev/null 2>&1; then
        echo -e "  ${CYAN}Recent Commits:${NC}"
        git log --oneline -5 --pretty=format:"    %C(yellow)%h%C(reset) %s %C(dim)(%cr)%C(reset)" 2>/dev/null || echo "    No git history"
        echo ""
        
        # Check for uncommitted changes
        if ! git diff-index --quiet HEAD -- 2>/dev/null; then
            echo -e "  ${YELLOW}⚠️  Uncommitted changes detected${NC}"
        else
            echo -e "  ${GREEN}✅ Working directory clean${NC}"
        fi
    else
        echo -e "  ${YELLOW}⚠️  Not a git repository${NC}"
    fi
    echo ""
}

# Function to check metrics trends
check_metrics_trends() {
    echo -e "${YELLOW}📊 Metrics Trends${NC}"
    echo "─────────────────"
    
    if [[ -d "${METRICS_DIR}" ]]; then
        local metric_files=$(find "${METRICS_DIR}" -name "metrics_*.json" | wc -l)
        echo -e "  Historical Metrics: ${BLUE}${metric_files} files${NC}"
        
        if [[ $metric_files -gt 0 ]]; then
            local latest_metric=$(find "${METRICS_DIR}" -name "metrics_*.json" | sort | tail -1)
            if [[ -f "$latest_metric" ]]; then
                local timestamp=$(jq -r '.timestamp' "$latest_metric" 2>/dev/null | cut -d'T' -f1 || echo "unknown")
                echo -e "  Latest Metrics: ${BLUE}${timestamp}${NC}"
                
                # Extract key metrics
                local coverage=$(jq -r '.quality.coverage.overall_coverage // "N/A"' "$latest_metric" 2>/dev/null)
                local build_time=$(jq -r '.performance.build.docker_build_time // "N/A"' "$latest_metric" 2>/dev/null)
                
                if [[ "$coverage" != "N/A" ]]; then
                    echo -e "  Test Coverage: ${BLUE}${coverage}%${NC}"
                fi
                if [[ "$build_time" != "N/A" ]]; then
                    echo -e "  Build Time: ${BLUE}${build_time}s${NC}"
                fi
            fi
        fi
    else
        echo -e "  ${YELLOW}⚠️  No metrics directory found${NC}"
    fi
    echo ""
}

# Function to show quick actions
show_quick_actions() {
    echo -e "${YELLOW}⚡ Quick Actions${NC}"
    echo "────────────────"
    echo -e "  ${CYAN}r${NC} - Refresh dashboard"
    echo -e "  ${CYAN}t${NC} - Run tests"
    echo -e "  ${CYAN}q${NC} - Run quality checks"
    echo -e "  ${CYAN}h${NC} - Run health check"
    echo -e "  ${CYAN}m${NC} - Collect metrics"
    echo -e "  ${CYAN}c${NC} - Clear logs"
    echo -e "  ${CYAN}e${NC} - Exit monitor"
    echo ""
}

# Function to run tests
run_tests() {
    echo -e "${YELLOW}Running tests...${NC}"
    cd "${PROJECT_ROOT}"
    
    if command -v python &> /dev/null && [[ -f "tools/testing/run_tests.py" ]]; then
        python tools/testing/run_tests.py --quick
    elif command -v pytest &> /dev/null; then
        pytest -v
    else
        echo -e "${RED}❌ No test runner available${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}Press any key to continue...${NC}"
    read -n 1
}

# Function to run quality checks
run_quality_checks() {
    echo -e "${YELLOW}Running quality checks...${NC}"
    cd "${PROJECT_ROOT}"
    
    if command -v pre-commit &> /dev/null; then
        pre-commit run --all-files
    else
        echo -e "${YELLOW}Running individual tools...${NC}"
        
        [[ -x "$(command -v black)" ]] && black --check .
        [[ -x "$(command -v isort)" ]] && isort --check-only .
        [[ -x "$(command -v flake8)" ]] && flake8
        [[ -x "$(command -v mypy)" ]] && mypy rsmt
    fi
    
    echo ""
    echo -e "${CYAN}Press any key to continue...${NC}"
    read -n 1
}

# Function to run health check
run_health_check() {
    echo -e "${YELLOW}Running health check...${NC}"
    cd "${PROJECT_ROOT}"
    
    if [[ -f "tools/ci_cd/health_check.py" ]]; then
        python tools/ci_cd/health_check.py
    else
        echo -e "${RED}❌ Health check script not found${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}Press any key to continue...${NC}"
    read -n 1
}

# Function to collect metrics
collect_metrics() {
    echo -e "${YELLOW}Collecting metrics...${NC}"
    cd "${PROJECT_ROOT}"
    
    if [[ -f "tools/ci_cd/metrics_collector.py" ]]; then
        python tools/ci_cd/metrics_collector.py --save
    else
        echo -e "${RED}❌ Metrics collector script not found${NC}"
    fi
    
    echo ""
    echo -e "${CYAN}Press any key to continue...${NC}"
    read -n 1
}

# Function to clear logs
clear_logs() {
    echo -e "${YELLOW}Clearing logs...${NC}"
    
    [[ -d "${LOGS_DIR}" ]] && rm -f "${LOGS_DIR}"/*.log
    [[ -d "${TEMP_DIR}" ]] && rm -f "${TEMP_DIR}"/*
    
    echo -e "${GREEN}✅ Logs cleared${NC}"
    sleep 1
}

# Main monitoring loop
main_loop() {
    while true; do
        show_header
        check_github_actions
        check_local_health
        check_test_status
        check_code_quality
        check_resources
        check_recent_activity
        check_metrics_trends
        show_quick_actions
        
        echo -n "Choose action (or wait 30s for auto-refresh): "
        
        # Read input with timeout
        if read -t 30 -n 1 action; then
            echo ""
            case "$action" in
                "r"|"R") continue ;;
                "t"|"T") run_tests ;;
                "q"|"Q") run_quality_checks ;;
                "h"|"H") run_health_check ;;
                "m"|"M") collect_metrics ;;
                "c"|"C") clear_logs ;;
                "e"|"E"|"q") 
                    echo -e "\n${GREEN}Exiting monitor...${NC}"
                    exit 0 
                    ;;
                *) 
                    echo -e "\n${YELLOW}Unknown action: $action${NC}"
                    sleep 1
                    ;;
            esac
        else
            echo ""  # Auto-refresh after timeout
        fi
    done
}

# Function to show usage
show_usage() {
    echo "RSMT CI/CD Pipeline Monitor"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help     Show this help message"
    echo "  --once         Run once and exit (no interactive mode)"
    echo "  --json         Output in JSON format"
    echo ""
    echo "Interactive Commands:"
    echo "  r - Refresh dashboard"
    echo "  t - Run tests"
    echo "  q - Run quality checks"  
    echo "  h - Run health check"
    echo "  m - Collect metrics"
    echo "  c - Clear logs"
    echo "  e - Exit"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_usage
        exit 0
        ;;
    --once)
        show_header
        check_github_actions
        check_local_health
        check_test_status
        check_code_quality
        check_resources
        check_recent_activity
        check_metrics_trends
        exit 0
        ;;
    --json)
        # Output structured data for external consumption
        cd "${PROJECT_ROOT}"
        
        # Create JSON output
        json_output=$(cat << EOF
{
  "timestamp": "$(date -Iseconds)",
  "project_root": "${PROJECT_ROOT}",
  "status": {
    "github_actions": "unknown",
    "local_health": "unknown",
    "tests": "unknown",
    "code_quality": "unknown"
  },
  "metrics": {
    "disk_usage": "$(du -sh "${PROJECT_ROOT}" 2>/dev/null | awk '{print $1}' || echo "N/A")",
    "git_commits": $(git rev-list --count HEAD 2>/dev/null || echo 0),
    "test_files": $(find . -name "test_*.py" 2>/dev/null | wc -l || echo 0)
  }
}
EOF
        )
        echo "$json_output"
        exit 0
        ;;
    "")
        # Interactive mode (default)
        echo -e "${GREEN}Starting RSMT CI/CD Pipeline Monitor...${NC}"
        sleep 1
        main_loop
        ;;
    *)
        echo -e "${RED}Unknown option: $1${NC}"
        show_usage
        exit 1
        ;;
esac
