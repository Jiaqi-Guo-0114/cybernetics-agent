# Cybernetics Agent Docker 镜像
# 支持多平台：linux/amd64, linux/arm64

FROM python:3.12-slim AS builder

WORKDIR /app

# 安装构建依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir hatchling && \
    pip install --no-cache-dir -e .[fastapi,opentelemetry] || \
    pip install --no-cache-dir -e .

# 生成正式镜像
FROM python:3.12-slim

WORKDIR /app

# 创建非 root 用户
RUN groupadd -r cybernetics && useradd -r -g cybernetics cybernetics

# 复制 Python 环境
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制源代码
COPY src/ ./src/
COPY dashboard_static/ ./dashboard_static/
COPY README.md .

# 设置环境变量
ENV PYTHONPATH=/app/src
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 创建数据目录
RUN mkdir -p /app/data && chown -R cybernetics:cybernetics /app

# 切换到非 root 用户
USER cybernetics

# 健康检查
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

EXPOSE 8080

# 默认启动 dashboard
CMD ["python", "-m", "cybernetics_agent", "dashboard", "--host", "0.0.0.0", "--port", "8080"]
