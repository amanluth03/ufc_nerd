#!/bin/bash

# UFC Nerd Development Runner
echo "🥊 Starting UFC Nerd Development Environment..."

# Function to kill background processes on exit
cleanup() {
    echo "Stopping all processes..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend server..."
cd backend
export FLASK_ENV=development
export API_PORT=5001
python3 app.py &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 2

# Start frontend
echo "Starting frontend development server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Both servers are running!"
echo "   - Backend: http://localhost:5001"
echo "   - Frontend: http://localhost:3000"
echo "   - API Health: http://localhost:5001/api/health"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID 