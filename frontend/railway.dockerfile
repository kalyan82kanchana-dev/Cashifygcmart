FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package.json yarn.lock* ./

# Install dependencies
RUN yarn install --frozen-lockfile

# Copy source code
COPY . .

# Build the application
RUN yarn build

# Install serve to run the production build
RUN yarn global add serve

# Expose port
EXPOSE 3000

# Start the application
CMD ["sh", "-c", "serve -s build -l ${PORT:-3000}"]