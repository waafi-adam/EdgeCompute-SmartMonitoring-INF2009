# Use Node.js 22 on Debian Bullseye (compatible with aarch64)
FROM node:22-bullseye

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json first to leverage Docker caching
COPY package.json package-lock.json ./

# Ensure sqlite3 is installed properly
RUN npm install --omit=dev sqlite3

# Copy all backend files into the container
COPY . .

# Ensure the database directory exists
RUN mkdir -p /app/database

# Expose the application port
EXPOSE 5000

# Run the server
CMD ["node", "server.js"]
