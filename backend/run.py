import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    extra_files = []
    if debug:
        # Watch all Python files and templates for changes
        import glob
        extra_files = glob.glob('**/*.py', recursive=True) + glob.glob('**/*.html', recursive=True) + glob.glob('**/*.jinja2', recursive=True)
    app.run(host='0.0.0.0', port=5000, debug=debug, extra_files=extra_files)
