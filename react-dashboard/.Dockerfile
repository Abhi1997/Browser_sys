FROM node:20-alpine

# Set working directory
WORKDIR /usr/src/app

# Copy dependency files first (for caching)
COPY react-dashboard/package.json .
COPY react-dashboard/package-lock.json .

# Install dependencies
RUN npm install

# Copy full React project
COPY react-dashboard/ .

# Expose port for development server
EXPOSE 3000

# Start the development server
CMD ["npm", "run", "dev"]
