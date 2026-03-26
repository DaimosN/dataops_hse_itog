# jupyterhub_config.py
c = get_config()

# Базовые настройки
c.JupyterHub.ip = '0.0.0.0'
c.JupyterHub.port = 8000

# Простая аутентификация
c.JupyterHub.authenticator_class = 'jupyterhub.auth.DummyAuthenticator'
c.DummyAuthenticator.password = 'admin'

# Разрешенные пользователи
c.Authenticator.allowed_users = {'admin', 'jupyter-user'}
c.Authenticator.admin_users = {'admin'}

# Настройка спавнера
c.JupyterHub.spawner_class = 'jupyterhub.spawner.SimpleLocalProcessSpawner'

# Увеличиваем таймауты (значительно!)
c.Spawner.start_timeout = 300  # 5 минут
c.Spawner.http_timeout = 120   # 2 минуты

# Настройка окружения для пользователя
c.Spawner.environment = {
    'JUPYTER_ENABLE_LAB': 'yes',
    'JUPYTER_ALLOW_ROOT': '1'  # Разрешаем запуск от root (для разработки)
}

# Аргументы для jupyter notebook/lab
c.Spawner.args = ['--allow-root']  # Разрешаем root

# База данных
c.JupyterHub.db_url = 'sqlite:///srv/jupyterhub/data/jupyterhub.sqlite'
c.JupyterHub.cookie_secret_file = '/srv/jupyterhub/data/jupyterhub_cookie_secret'

# Настройки прокси
c.ConfigurableHTTPProxy.api_url = 'http://127.0.0.1:8001'
c.ConfigurableHTTPProxy.should_start = True
c.ConfigurableHTTPProxy.debug = True
c.ConfigurableHTTPProxy.auth_token = 'test-token'

# Логирование
c.JupyterHub.log_level = 'DEBUG'
c.Spawner.debug = True