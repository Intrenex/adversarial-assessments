FROM ollama/ollama:latest

# Create a place for our setup script
WORKDIR /app

# Copy the entrypoint script from your host to the container
COPY entrypoint.sh .

# Ensure it has permission to run
RUN chmod +x entrypoint.sh

# Entrypoint handles starting the engine and pulling the model
ENTRYPOINT ["./entrypoint.sh"]
