FROM node:22-alpine
ENV NODE_ENV=production
WORKDIR /app
COPY index.html main.js tracking.js style.css server.mjs ./
USER node
EXPOSE 8080
CMD ["node", "server.mjs"]
