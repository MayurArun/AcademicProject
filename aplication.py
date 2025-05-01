import threading
import os
import sys
import time
import webbrowser

def run_django():
    print("[INFO] Starting Django...")

    # Step into the extra_features directory (where manage.py and classroom_project live)
    os.chdir('extra_features')

    # Add extra_features to the Python path
    sys.path.insert(0, os.getcwd())

    # Point to settings module inside classroom_project
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'classroom_project.settings')

    from django.core.management import execute_from_command_line
    execute_from_command_line(['manage.py', 'runserver', '8000', '--noreload'])


def run_flask():
    print("[INFO] Starting Flask...")
    from app import app
    app.run(port=5000, debug=True, use_reloader=False)


if __name__ == '__main__':
    threading.Thread(target=run_django).start()
    time.sleep(3)
    threading.Thread(target=run_flask).start()
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:5000")
