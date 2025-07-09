# Dockerfile

# Use a minimal Python image
FROM python:3.13-slim

# 1. Set working directory
WORKDIR /app

# 2. Install dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy the entire project, including entrypoint.sh
COPY . .

# 4. Ensure entrypoint.sh is executable
RUN chmod +x ./entrypoint.sh

# 5. Expose FastAPI port
EXPOSE 8000

# 6. Use /bin/sh to run the entrypoint script
ENTRYPOINT ["sh", "./entrypoint.sh"]
