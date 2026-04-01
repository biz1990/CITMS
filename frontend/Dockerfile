# Stage 1: Build Node.js Vite App
FROM node:18-alpine AS builder

WORKDIR /app

# Dependency resolution
COPY package.json package-lock.json* ./
RUN npm install --frozen-lockfile

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx Alpine
FROM nginx:alpine

# Copy custom nginx configuration (proxy setup)
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy Vite build output to nginx document root
COPY --from=builder /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
