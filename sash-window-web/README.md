# Skylon Elements – Sash Window Web Suite

Migrated version of the PyQt6 Skylon Elements sash window designer, now split into a FastAPI backend and a responsive web frontend.

## Project structure

```
sash-window-web/
├── backend/
│   ├── app/
│   │   ├── api/                # FastAPI routers (calculations, exports)
│   │   ├── core/               # Legacy calculation logic and data models
│   │   ├── graphics/           # Rendering & exporter modules (DXF, SVG, PNG, etc.)
│   │   ├── services/           # PDF, Excel, drawings, Supabase integration
│   │   └── main.py             # FastAPI application factory
│   ├── requirements.txt        # Backend dependencies
│   └── .env.example            # Environment variables template
├── frontend/
│   ├── index.html              # Tailwind-based UI
│   ├── css/styles.css          # Custom styles
│   └── js/                     # Vanilla JS modules (API, renderer, viewer)
├── output/                     # Generated exports (PDF, Excel, DXF, SVG, PNG)
└── README.md                   # This file
```

## Backend setup

```bash
cd sash-window-web/backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is exposed at `http://localhost:8000/api`. The key endpoints are:

- `POST /api/calculate` – run full geometry, materials and preview calculations.
- `POST /api/export/{pdf|excel|dxf|svg|png}` – generate export packages (DXF/SVG/PNG are returned as ZIP archives).
- `GET /api/download/{file_id}` – download previously generated exports.
- `GET /api/health` – basic service health check.

Optional Supabase credentials can be configured through environment variables defined in `.env.example`.

## Frontend setup

The frontend is a static bundle and can be served by any web server. During development you can use `vite`, `http-server`, or even Python’s `http.server`:

```bash
cd sash-window-web/frontend
python -m http.server 5173
```

Navigate to `http://localhost:5173` (adjust the port if needed). The UI communicates with the backend using the relative `/api` path, so host both layers on the same domain (configure a proxy in production if required).

### Features

- Full replication of the PyQt6 configuration options (dimensions, finishes, glazing, glazing bars, timber selection).
- Real-time SVG preview with pan/zoom controls powered by Panzoom.js.
- Tabbed panels for graphics, calculation results (cutting lists, hardware, summaries) and export management.
- Export workflow with progress feedback and download history.

## Security & operations

- CORS is enabled with permissive defaults – tighten the `allow_origins` list for production deployments.
- SlowAPI rate limiting is configured (120 requests/minute). Adjust via the `API_RATE_LIMIT` environment variable.
- Generated exports are stored inside `sash-window-web/output/` and registered in-memory for download. A background cleanup removes missing files from the registry.

## Testing

Existing pytest suites from the desktop version can be adapted by pointing imports to `app.core` and `app.graphics`. New API-level tests can be written using `httpx.AsyncClient`.

## Notes

- Graphics exporters depend on optional libraries (`ezdxf`, `cairosvg`). API responses will signal `503 Service Unavailable` if a dependency is missing.
- The original calculation algorithms and exporter logic are preserved verbatim within `app/core` and `app/graphics`.

Enjoy the new web-native experience!🚀
