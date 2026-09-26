# RojasWebs Django Mockup

A ready-to-run Django version of the one-page RojasWebs portfolio mockup.

## Open in VS Code

1. Extract the ZIP.
2. Open the `rojaswebs_django_mockup` folder in VS Code.
3. Open the VS Code terminal.
4. Create a virtual environment:

   **Windows PowerShell**
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **Git Bash on Windows**
   ```bash
   py -m venv .venv
   source .venv/Scripts/activate
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

5. Install Django:
   ```bash
   pip install -r requirements.txt
   ```

6. Run the initial setup:
   ```bash
   python manage.py migrate
   python manage.py check
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

8. Open:
   `http://127.0.0.1:8000/`

## Main files

- `website/templates/website/home.html`
- `website/static/website/css/style.css`
- `website/static/website/js/main.js`
- `website/static/website/images/edgar-portrait.png`

## Personalize

Replace the placeholder LinkedIn `href="#"` values in `home.html` with your real LinkedIn URL.

The page uses a Google Fonts import for Inter and Birthstone. Remove the `@import`
line in `style.css` if you later choose to self-host fonts.
