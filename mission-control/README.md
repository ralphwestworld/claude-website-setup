# Mission Control

A local, single-page project tracker for the VR game. Log characters, scenarios, props, mechanics, features, references, and notes. Attach reference images. Tracks dates and an automatic change log.

All data lives in your browser (IndexedDB). No server, no account, no cloud.

## Run it

```bash
cd mission-control
python3 -m http.server 8000
# open http://localhost:8000
```

Or just open `index.html` directly in a modern browser. (Serving over HTTP is more reliable for some browsers.)

## How to use it

- **+ New Entry** — opens the editor. Pick a Type (Character / Scenario / Prop / Mechanic / Feature / Reference / Note), a Status (Idea / In Progress / Done / Blocked), add tags, write a description.
- **Reference images** — click **Browse…** or drag files onto the image dropzone. Images are stored locally; click a thumbnail to open it full-screen. Use the × on a thumbnail to remove it.
- **Sidebar filters** — narrow the grid by type or status. Click a filter again to clear (or pick "All").
- **Search** — top bar searches titles, descriptions, and tags.
- **Click a card** — opens the read-only viewer with the full description, images, and the entry's change log. Hit **Edit** to modify.
- **Global change log** — sidebar → "Open change log" shows every action across the whole project.
- **Export / Import** — top bar. Export writes a JSON file with every entry, image (base64-encoded), and log line. Import restores it. Use this to back up or move between machines.

### Keyboard

- `N` — new entry (when not typing in a field).
- `Esc` — close any open modal.

## Data storage

Everything is stored in IndexedDB under the database name `mission-control`:

- `entries` — one record per entry (id, title, description, type, status, tags, imageIds, createdAt, updatedAt).
- `images`  — image blobs referenced by entries.
- `log`     — append-only list of actions (create, update, delete, image add/remove, import).

**Clearing browser data or "site storage" will erase everything.** Export regularly.

## File layout

- `index.html` — page shell, modals, lightbox.
- `styles.css` — dark UI theme.
- `app.js` — rendering, editor, viewer, filters, export/import.
- `db.js` — IndexedDB wrapper.
