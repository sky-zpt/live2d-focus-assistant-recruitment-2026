"""Live2D 专注助手的 Flask 应用入口。"""

from pathlib import Path

from flask import Flask, jsonify, render_template

from src.config import DEFAULT_CONFIG
from src.db import init_app as init_db_app
from src.routes import api


def create_app(test_config=None):
    """创建并配置 Flask 应用。

    ``test_config`` 仅用于测试环境覆盖默认配置，例如使用内存数据库。
    数据库连接和业务逻辑会在后续模块中注册。
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DEFAULT_CONFIG)
    app.config["DATABASE"] = str(Path(app.instance_path) / "focus.db")

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_db_app(app)
    app.register_blueprint(api)

    @app.get("/health")
    def health_check():
        """返回应用健康状态，供启动与部署检查使用。"""
        return jsonify({"status": "ok"})

    @app.get("/")
    def index():
        """渲染专注助手首页。"""
        return render_template("index.html")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
