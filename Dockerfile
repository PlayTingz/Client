FROM python:3.13.3-alpine
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    linux-headers
RUN pip install uv
WORKDIR /app
COPY pyproject.toml .
RUN uv sync
COPY src src
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=30s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:5000/health || exit 1
ENTRYPOINT [ "uv", "run", "./src/app.py" ]