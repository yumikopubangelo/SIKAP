FROM node:20-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

# Expose Vite dev server port
EXPOSE 5173

# Development: Vite dev server dengan hot reload
# --host 0.0.0.0 supaya accessible dari luar container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
