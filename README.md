# linkedin_jobsearch
Job search via LinkedIn using AI to match job descriptions to prompts and filter out unsuitable positions. Local LLMs (like Ollama) can be easily substituted with OpenAI or any other preferred model.
Install uv:
```
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Install python3.12
```bash
uv python install 3.12
```
Create virtualenv
```bash
uv venv linked
```
Pin python version to virtualenv
```bash
uv venv linked -p 3.12
```
Activate virtualenv
```bash
source linked/bin/activate
```
Install dependencies
```bash
uv pip install -r requirements.txt
```

Adjust **geoId**, **jobtype**, **timer** and **choice** parameters inside the script. Also, put your values for **session_cookie**, which is `li_at` cookie and **cssrftoken**, which is `Jsessionid` cookie with `ajax:` at the beginning.
The geoId can be found for your location as soon as you start the job search; simply check the URL bar for it. Other params you can find after line 212 with some examples.
