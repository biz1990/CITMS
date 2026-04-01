# Dockerfile for Frontend
FROM node:20-alpine

WORKDIR /app

# Copy package and install
COPY package.json package-lock.json* ./
RUN npm install

# Do not copy source code here in dev, rely on docker volume mounting
# COPY . .

CMD ["npm", "run", "dev", "--", "--host"]
