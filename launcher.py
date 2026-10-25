import json
import subprocess
from pathlib import Path


JSON_FILE = "launcher_apps.json"


def load_apps():
    with open(JSON_FILE, encoding="utf-8") as file:
        return json.load(file)


def launch_app(app):
    app_path = Path(app["app_path"])
    venv_path = app.get("venv_path")

    if venv_path:
        python_path = (
            Path(venv_path)
            / "Scripts"
            / "python.exe"
        )
    else:
        python_path = "python"


    subprocess.Popen(
        [
            "cmd",
            "/k",
            str(python_path),
            str(app_path),
        ],
        cwd=app_path.parent,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

def main():
    apps = load_apps()
    app_names = list(apps)

    print()
    print("=== Python Application Launcher ===")
    print()

    for index, app_name in enumerate(app_names, start=1):
        print(f"{index}. {app_name}")

    print()
    print("0. Exit")
    print()

    try:
        selection = int(input("Select application: "))
    except ValueError:
        print("Invalid input.")
        return

    if selection == 0:
        return

    if not 1 <= selection <= len(app_names):
        print("Invalid selection.")
        return

    app_name = app_names[selection - 1]
    app = apps[app_name]

    print()
    print(f"Starting: {app_name}")

    launch_app(app)


if __name__ == "__main__":
    main()