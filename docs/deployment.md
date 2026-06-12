# Deployment

Version 1 is local-first:

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Qdrant: `http://localhost:6333`

A static frontend may be deployed to Vercel or Netlify, but the API and Qdrant should remain
private unless authentication, rate limiting, managed secrets, and persistence are added.
