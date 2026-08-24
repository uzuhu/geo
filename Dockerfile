# =====================================================================
# GEO 收录查询系统 - 统一应用镜像
# 基础镜像：微软官方 Playwright Python 镜像（已预装浏览器系统依赖 + Chromium）
# 选用原因：无需在纯净 python:slim 上手动补 X11/Mesa 等图形库，
#           避免 Linux 动态链接库缺失导致 Playwright 启动失败。
# =====================================================================
FROM mcr.microsoft.com/playwright/python:1.48.0

# 统一运行环境
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# 先拷贝依赖清单并安装（利用 Docker 层缓存，源码变动不触发重装）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 保底：确保 headless Chromium 完全就绪。
# 官方镜像已预装对应版本，通常仅校验复用、不重复下载；
# 若 pip 解析的 playwright 版本与镜像预装不一致，此步会补齐对应浏览器。
RUN playwright install chromium

# 拷贝应用源码（运行时可用 volume 挂载覆盖以实现热更新）
COPY . .

# 端口（compose 中 web 服务映射宿主机 8000）
EXPOSE 8000

# 默认启动命令，compose 中 web/worker 各自用 command 覆盖
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
