"""SQLite 连接与建表初始化。"""

import sqlite3
from pathlib import Path

from flask import current_app, g


def get_db():
    """返回当前请求或应用上下文复用的 SQLite 连接。"""
    if "db" not in g:
        connection = sqlite3.connect(current_app.config["DATABASE"])
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        g.db = connection
    return g.db


def close_db(_error=None):
    """在上下文结束时关闭数据库连接。"""
    connection = g.pop("db", None)
    if connection is not None:
        connection.close()


def init_db():
    """创建尚不存在的数据表和索引，不删除已有数据。"""
    schema_path = Path(__file__).with_name("schema.sql")
    with schema_path.open(encoding="utf-8") as schema_file:
        connection = get_db()
        connection.executescript(schema_file.read())
        columns = {row[1] for row in connection.execute("PRAGMA table_info(focus_sessions)")}
        if "archived" not in columns:
            connection.execute(
                "ALTER TABLE focus_sessions ADD COLUMN archived INTEGER NOT NULL DEFAULT 0"
            )
        connection.commit()


def init_app(app):
    """将数据库生命周期和建表逻辑注册到 Flask 应用。"""
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()
