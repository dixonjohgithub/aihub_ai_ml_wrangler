# Nginx reverse proxy Dockerfile
FROM nginx:alpine

# Copy custom configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy custom error pages (optional)
COPY error-pages/ /usr/share/nginx/html/ 2>/dev/null || true

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80/health || exit 1

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]