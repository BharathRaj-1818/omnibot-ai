FROM node:18-alpine AS build

WORKDIR /app

# Copy package files first (better layer caching)
COPY package*.json ./
RUN npm ci --silent

# Copy source and build
COPY . .
RUN npm run build

# Production stage — serve with nginx
FROM nginx:alpine

# Copy built React app
COPY --from=build /app/build /usr/share/nginx/html

# Nginx config to handle React Router (SPA routing)
RUN echo 'server { \
    listen 80; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
    location /api { \
        proxy_pass http://backend:8000; \
        proxy_set_header Host $host; \
        proxy_set_header X-Real-IP $remote_addr; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
