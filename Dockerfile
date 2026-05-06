FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

# Set non-interactive to avoid timezone prompts
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3.10-dev \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set python3.10 as default
RUN ln -sf /usr/bin/python3.10 /usr/bin/python
RUN ln -sf /usr/bin/python3.10 /usr/bin/python3

# Install PyTorch
RUN pip3 install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install HF and LoRA dependencies
RUN pip3 install --no-cache-dir \
    transformers \
    peft \
    trl \
    datasets \
    accelerate \
    bitsandbytes \
    scipy \
    sentencepiece

# Set working directory
WORKDIR /workspace

# Copy scripts and schema
COPY scripts/ /workspace/scripts/
COPY schema/ /workspace/schema/

CMD ["/bin/bash"]
