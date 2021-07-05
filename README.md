# account-backend
AVWX account management backend service

## Develop

```bash
uvicorn account.main:app --reload --port 8080
```

## Test

```bash
docker run -d mongo
```

```bash
pytest
```
