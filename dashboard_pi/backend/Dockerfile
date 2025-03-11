# Use Node.js 22 on Debian Bullseye (Raspberry Pi compatible)
FROM node:22-bullseye

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json before installing dependencies
COPY package.json package-lock.json ./

# Explicitly install sqlite3
RUN npm install sqlite3 --build-from-source

# Install all other dependencies
RUN npm install --omit=dev

# Copy application files
COPY . .

# Ensure database directory exists
RUN mkdir -p /app/database

# Expose backend port
EXPOSE 5000

# Start the server
CMD ["node", "server.js"]
