# 使用 Python 3.9 作为基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . /app/

# 安装依赖
RUN pip install --no-cache-dir -r dev-requirements.txt

# 设置环境变量
ENV PYTHONUNBUFFERED=1

# 创建数据目录（当使用卷挂载时可能不需要）
# RUN mkdir -p /app/data /app/dist

# 设置入口点
ENTRYPOINT ["python", "scripts/update.py"]
