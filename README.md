# Chartbook

This project ingests poultry and egg market data into SQLite and builds two static dashboards:

- `egg-dashboard.html`
- `broiler-dashboard.html`

The dashboards are powered by `docs/data.json`, which is generated from `chartbook.db` and committed so the site can be hosted directly on GitHub Pages.

## Repository Layout

- `src/chartbook/`: source code for ingestion, data shaping, templates, and front-end assets
- `docs/`: published GitHub Pages site output
- `docs/data/`: CSV snapshots exported from SQLite for download/reference
- `docs/assets/`: CSS and JavaScript copied into the published site
- `references/`: research notes, PDFs, and one-off reference artifacts
- `notes/`: planning and handoff notes
- root `build.py`, `build_dashboard.py`, `ingest.py`: thin convenience wrappers so the old commands still work

## Setup

Python's standard library is enough for the core pipeline. Python 3.9+ is recommended.

Optional environment variables:

- `MARS_API_KEY`
- `NASS_API_KEY`
- `FRED_API_KEY`
- `BLS_API_KEY`

You can keep local secrets in a `.env` file if you want, but it is gitignored.

## Common Commands

Ingest the most frequently updated sources:

```bash
python3 ingest.py --update --frequent-only
```

Run all incremental ingests:

```bash
python3 ingest.py --update
```

Build the dashboards:

```bash
python3 build_dashboard.py
```

Export CSV snapshots and rebuild everything:

```bash
python3 build.py
```

Serve the dashboards locally:

```bash
python3 -m http.server 8011 -d docs
```

Then open:

- `http://localhost:8011/`
- `http://localhost:8011/egg-dashboard.html`
- `http://localhost:8011/broiler-dashboard.html`

## Generated Files

Some build outputs are committed on purpose so the site can be hosted directly from this repository, including:

- `docs/data.json`
- `docs/index.html`
- `docs/egg-dashboard.html`
- `docs/broiler-dashboard.html`
- `docs/data/*.csv`
- `docs/assets/*`

The following local artifacts are intentionally gitignored because they are environment-specific or easy to regenerate:

- `chartbook.db` and SQLite sidecar files
- Python cache directories and local virtual environments
- `.pdf_pages/` image extraction artifacts

For GitHub Pages deployments, rebuild locally and commit the refreshed `docs/` output alongside the source changes in `src/chartbook/`.
