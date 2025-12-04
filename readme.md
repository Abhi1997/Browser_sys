# Browser_sys

Current progress (as of 2025-12-04)

- Project contains a simple PyQt6-based browser UI split across two files:
	- `browser.py` — module containing the UI classes: `BrowserTab` and `MainWindow`.
	- `main.py` — application entry point that creates the `QApplication` and runs the `MainWindow`.

- A virtual environment is present at `.venv/` and was used to install runtime dependencies.

- Key packages installed in the venv (captured in `requirements.txt`):
	- `PyQt6==6.10.0`
	- `PyQt6-WebEngine==6.10.0`
	- plus related Qt and sip bindings (see `requirements.txt` for full list).

What I changed

- Converted the original `browser.py` so it only defines classes and no longer starts the app directly.
- Added `main.py` to launch the application.
- Added workspace `.vscode/settings.json` to point VS Code to the workspace venv.

How to run (Windows PowerShell)

1. Activate the venv (PowerShell):

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
& 'D:\Browser_sys\.venv\Scripts\Activate.ps1'
```

2. Run the app:

```powershell
python D:\Browser_sys\main.py
```

Or using the full venv python path:

```powershell
D:/Browser_sys/.venv/Scripts/python.exe D:/Browser_sys/main.py
```

Editor tips

- In VS Code, select the interpreter `D:/Browser_sys/.venv/Scripts/python.exe` (bottom-right) and restart the Python language server if imports show as unresolved.

Notes & next steps

- If you want `pip` available system-wide (outside the venv), re-install or repair your system Python; for now using the venv is recommended.
- I can optionally:
	- Add a small README badge and license.
	- Create a `run.ps1` helper script to activate the venv and launch the app.
	- Commit these files to git.

See `requirements.txt` for the full pinned dependency list.

