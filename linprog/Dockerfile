FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple/ -r requirements.txt

COPY . .

# 创建临时文件目录（用于Excel生成）
RUN mkdir -p /app/temp

# 暴露API端口
EXPOSE 8000

CMD ["python", "api.py"]
