# Clarity — React Frontend

Vite + React + TypeScript app using Framer Motion and Lucide (shadcn icons).

## Quick start

```bash
# Terminal 1 — API server
cd /c/Users/admin/token-hackathon
python web/api/server.py

# Terminal 2 — Frontend dev server
cd /c/Users/admin/token-hackathon/web/frontend
npm run dev
```

The app runs on `http://localhost:5173` and proxies `/api/*` to the API server on port `8000`.

## Stack

- **Vite 8** with React 19 + TypeScript 6
- **Framer Motion** — page/card/hover/scroll animations
- **Lucide React** — shadcn icon set
- **Tailwind CSS v4** with Ventriloc design tokens
- **React Router** — landing `/`, dashboard `/dashboard`

## Build

```bash
npm run build
```

Output goes to `dist/`.
