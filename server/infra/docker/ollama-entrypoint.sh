#!/bin/bash

/bin/ollama serve &

echo "Waiting for Ollama server..."
until ollama list >/dev/null 2>&1; do
    sleep 1
done

echo "Ollama is up. Creating models..."

if ! ollama list | grep -q "lexigrade-generator"; then
    echo "Creating lexigrade-generator..."
    ollama create lexigrade-generator -f /models/lexigrade-generator/Modelfile
fi

if ! ollama list | grep -q "lexigrade-reviewer"; then
    echo "Creating lexigrade-reviewer..."
    ollama create lexigrade-reviewer -f /models/lexigrade-reviewer/Modelfile
fi


echo "All models ready."

wait -n