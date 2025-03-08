FROM python:3.10.4

WORKDIR /app

COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip && \
    PIP_INDEX_URLS=" \
      https://pypi.tuna.tsinghua.edu.cn/simple \
      https://mirrors.aliyun.com/pypi/simple \
      https://pypi.org/simple" && \
    for url in $PIP_INDEX_URLS; do \
      pip install --no-cache-dir -r requirements.txt --index-url $url && break || echo "Trying next mirror..."; \
    done

COPY . /app

CMD ["python", "app.py"]

