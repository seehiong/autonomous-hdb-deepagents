FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        gcc wget curl build-essential && \
    rm -rf /var/lib/apt/lists/*

# ---------------------------
# Install GENAI Toolbox binary
# ---------------------------
ENV TOOLBOX_VERSION=0.22.0
RUN curl -L -o /usr/local/bin/toolbox \
      https://storage.googleapis.com/genai-toolbox/v${TOOLBOX_VERSION}/linux/amd64/toolbox \
    && chmod +x /usr/local/bin/toolbox

# Copy project
COPY . .

# Install uv + dependency sync
RUN pip install uv
RUN uv sync --frozen

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000 7860 5000

CMD ["bash", "-c", "echo 'Use docker-compose to run'"]