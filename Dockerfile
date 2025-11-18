# Multi-stage Dockerfile for Vite frontend + Node backend

# 1) Build stage: install deps and build the Vite frontend
FROM node:18-alpine AS builder
WORKDIR /app

# copy root package files for frontend
COPY package*.json ./
# If there's a lockfile, copy it too
COPY package-lock.json* .npmrc* ./  

RUN npm ci --silent || npm install --silent

# Copy the whole repo and build frontend
COPY . .
RUN npm run build --silent

# 2) Production image: backend serves the built frontend
FROM node:18-alpine AS runner
WORKDIR /app/backend

# Install backend deps
COPY backend/package*.json ./
RUN npm ci --omit=dev || npm install --omit=dev

# Copy backend source and the built frontend from builder
COPY backend/ ./
COPY --from=builder /app/dist ./dist

ENV NODE_ENV=production
ENV PORT=8080
EXPOSE 8080

# Start the backend (which now serves the built frontend)
CMD ["node", "index.js"]
