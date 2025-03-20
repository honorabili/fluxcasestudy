FROM pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime

# Set working directory
WORKDIR /app

# Copy code
COPY handler.py /app/handler.py

# Install dependencies to call huggingface
RUN pip install --upgrade pip
RUN pip install torch diffusers runpod transformers accelerate huggingface_hub

# Set environment variables
ENV MODEL_DIR=/app/model
RUN mkdir -p $MODEL_DIR

# Download the Stable Diffusion model (no authentication needed)
RUN huggingface-cli login(token="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")
RUN huggingface-cli download black-forest-labs/FLUX.1-dev --local-dir $MODEL_DIR --local-dir-use-symlinks False
# token added in runpod cli preconfig

# Expose the port (if required by RunPod)
EXPOSE 8000

# Set the handler as the entry point
CMD ["python3", "handler.py"]

#test
