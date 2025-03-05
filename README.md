## Development

```bash
pyenv local 3.8.20
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

Tests:
```bash
pytest standalone.py
pytest with_client.py
```

```bash
python -i tests/interactive.py
```