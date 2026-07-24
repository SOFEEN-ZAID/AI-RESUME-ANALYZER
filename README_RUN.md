# Run Backend in VS Code

Use these commands in the VS Code terminal.

```powershell
cd C:\Users\HP\Documents\Codex\2026-07-07\i\outputs\ai-resume-job-match-analyzer\backend
py -3.13 -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --reload
```

Open the API test page:

```text
http://127.0.0.1:8000/docs
```

Then open the frontend file:

```text
C:\Users\HP\Documents\Codex\2026-07-07\i\outputs\ai-resume-job-match-analyzer\frontend\index.html
```
