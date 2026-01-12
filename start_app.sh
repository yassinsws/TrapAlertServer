#!/bin/bash

# TrapAlert Application Startup Script

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== Starting TrapAlert System ===${NC}"

# Function to check if a port is in use
check_port() {
    lsof -i:$1 > /dev/null
    if [ $? -eq 0 ]; then
        echo -e "${RED}Warning: Port $1 is already in use.${NC}"
        return 0
    else
        return 1
    fi
}

# Cleanup function
cleanup() {
    echo -e "\n${BLUE}Shutting down services...${NC}"
    pkill -P $$ 
    exit
}

# Trap SIGINT (Ctrl+C)
trap cleanup SIGINT

# 1. Start Backend
echo -e "\n${GREEN}[1/2] Starting Backend Server (Port 8000)...${NC}"
check_port 8000
if [ $? -eq 0 ]; then
    echo "Killing existing process on port 8000..."
    lsof -ti:8000 | xargs kill -9
fi

source .venv/bin/activate
uvicorn main:app --reload --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend running (PID: $BACKEND_PID). Logs: backend.log"

# 2. Start Frontend
echo -e "\n${GREEN}[2/2] Starting Admin Dashboard (Port 3000)...${NC}"
check_port 3000
if [ $? -eq 0 ]; then
    echo "Killing existing process on port 3000..."
    lsof -ti:3000 | xargs kill -9
fi

cd admin-dashboard
npm run dev -- -p 3000 &
FRONTEND_PID=$!
echo "Frontend running (PID: $FRONTEND_PID)"

echo -e "\n${BLUE}=== System is Live! ===${NC}"
echo -e "Backend:  http://localhost:8000"
echo -e "Frontend: http://localhost:3000"
echo -e "Press Ctrl+C to stop all services."

# Wait for both processes
wait
