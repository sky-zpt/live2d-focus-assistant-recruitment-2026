"""命令行历史工具：python -m src.cli <command>。"""
import argparse
from pathlib import Path
from app import create_app
from src.db import get_db
from src import repositories
from src.analytics import report
from src.cleanup_service import cleanup_stale_sessions
from src.import_export import export_json

def main():
    parser = argparse.ArgumentParser(description="Live2D 专注助手历史工具")
    parser.add_argument("command", choices=["history", "summary", "export", "cleanup"])
    parser.add_argument("path", nargs="?")
    args = parser.parse_args()
    app = create_app()
    with app.app_context():
        db = get_db()
        if args.command == "history":
            for row in repositories.all_sessions(db): print(f"#{row['id']} [{row['status']}] {row['task_text']}")
        elif args.command == "summary":
            import json; print(json.dumps(report(db), ensure_ascii=False, indent=2))
        elif args.command == "export":
            target = Path(args.path or "focus-sessions.json"); target.write_text(export_json(db), encoding="utf-8"); print(target)
        else:
            print(f"abandoned: {len(cleanup_stale_sessions(db))}")
if __name__ == "__main__": main()
