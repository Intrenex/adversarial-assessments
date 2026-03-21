#!/bin/bash
ollama serve &
echo "Waiting for Ollama server..."
until curl -s localhost:11434/api/tags > /dev/null; do
  sleep 2
done
echo "Loading Llama Guard weights..."
ollama pull llama-guard3
wait
