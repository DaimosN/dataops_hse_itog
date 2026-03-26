FROM python:3.9-slim

# Устанавливаем Node.js для proxy
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем JupyterHub и зависимости
RUN pip install --no-cache-dir \
    jupyterhub \
    jupyterlab \
    notebook \
    configurable-http-proxy

# Создаем структуру директорий
RUN mkdir -p /srv/jupyterhub/data /etc/jupyterhub

# Копируем конфигурацию
COPY jupyterhub_config.py /etc/jupyterhub/jupyterhub_config.py

# Создаем пользователей
RUN useradd -m -s /bin/bash admin && \
    echo "admin:admin" | chpasswd && \
    useradd -m -s /bin/bash jupyter-user && \
    echo "jupyter-user:jupyter" | chpasswd

# Создаем директории для пользователей
RUN mkdir -p /home/admin /home/jupyter-user && \
    chown -R admin:admin /home/admin && \
    chown -R jupyter-user:jupyter-user /home/jupyter-user

# Устанавливаем права
RUN chmod -R 755 /srv/jupyterhub/data

# Создаем символическую ссылку для совместимости
RUN ln -s /usr/local/bin/jupyter /usr/bin/jupyter

# Открываем порт
EXPOSE 8000

# Запускаем JupyterHub
CMD ["jupyterhub", "-f", "/etc/jupyterhub/jupyterhub_config.py"]