#!/bin/bash
# init-databases.sh

set -e
set -u

function create_user_and_database() {
    local database=$1
    echo "  Creating user and database '$database'"

    # Подключаемся к базе данных 'postgres' для выполнения команд
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname="postgres" <<-EOSQL
        -- Создаем пользователя если не существует
        DO
        \$\$
        BEGIN
            IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = '$database') THEN
                CREATE USER $database WITH PASSWORD '$POSTGRES_PASSWORD';
            END IF;
        END
        \$\$;

        -- Создаем базу данных если не существует
        SELECT 'CREATE DATABASE $database'
        WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$database')\gexec

        -- Даем права пользователю
        GRANT ALL PRIVILEGES ON DATABASE $database TO $database;
EOSQL
}

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    echo "Multiple database creation requested: $POSTGRES_MULTIPLE_DATABASES"

    # Разделяем список баз данных
    IFS=',' read -ra databases <<< "$POSTGRES_MULTIPLE_DATABASES"

    for db in "${databases[@]}"; do
        # Убираем пробелы
        db=$(echo $db | xargs)
        create_user_and_database $db
    done

    echo "Multiple databases created"
fi