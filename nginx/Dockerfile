FROM nginx:alpine

# Remove default nginx configuration
RUN rm /etc/nginx/nginx.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create log directories
RUN mkdir -p /var/log/nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]