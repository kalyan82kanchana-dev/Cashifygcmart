# Use Node.js 20 and Python 3.11
FROM node:20-alpine

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json ./
COPY frontend/package.json ./frontend/
COPY backend/requirements.txt ./backend/

# Install Node.js dependencies
WORKDIR /app/frontend
RUN npm install --legacy-peer-deps

# Install Python dependencies
WORKDIR /app/backend
RUN pip install --break-system-packages -r requirements.txt

# Copy source code
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm run build

# Set working directory to backend for runtime
WORKDIR /app/backend

# Expose port
EXPOSE 8001

# Start the application
CMD ["python3", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8001"]
