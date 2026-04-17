// IndexedDB wrapper. Stores:
//   entries: { id, title, description, type, status, tags[], imageIds[], createdAt, updatedAt }
//   images:  { id, blob, name, addedAt }
//   log:     { id(auto), entryId|null, action, message, at }

const DB_NAME = 'mission-control';
const DB_VERSION = 1;

let _db = null;

function open() {
  if (_db) return Promise.resolve(_db);
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION);
    req.onupgradeneeded = (e) => {
      const db = e.target.result;
      if (!db.objectStoreNames.contains('entries')) {
        const s = db.createObjectStore('entries', { keyPath: 'id' });
        s.createIndex('updatedAt', 'updatedAt');
        s.createIndex('type', 'type');
        s.createIndex('status', 'status');
      }
      if (!db.objectStoreNames.contains('images')) {
        db.createObjectStore('images', { keyPath: 'id' });
      }
      if (!db.objectStoreNames.contains('log')) {
        const s = db.createObjectStore('log', { keyPath: 'id', autoIncrement: true });
        s.createIndex('at', 'at');
        s.createIndex('entryId', 'entryId');
      }
    };
    req.onsuccess = () => { _db = req.result; resolve(_db); };
    req.onerror = () => reject(req.error);
  });
}

function tx(stores, mode = 'readonly') {
  return open().then((db) => db.transaction(stores, mode));
}

function reqToPromise(req) {
  return new Promise((resolve, reject) => {
    req.onsuccess = () => resolve(req.result);
    req.onerror = () => reject(req.error);
  });
}

export function uid() {
  return 'e_' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
}

// Entries
export async function getAllEntries() {
  const t = await tx(['entries']);
  const store = t.objectStore('entries');
  return reqToPromise(store.getAll());
}

export async function getEntry(id) {
  const t = await tx(['entries']);
  return reqToPromise(t.objectStore('entries').get(id));
}

export async function putEntry(entry) {
  const t = await tx(['entries'], 'readwrite');
  await reqToPromise(t.objectStore('entries').put(entry));
  return entry;
}

export async function deleteEntry(id) {
  const t = await tx(['entries', 'log'], 'readwrite');
  await reqToPromise(t.objectStore('entries').delete(id));
}

// Images
export async function putImage(blob, name) {
  const id = 'img_' + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
  const t = await tx(['images'], 'readwrite');
  await reqToPromise(t.objectStore('images').put({ id, blob, name, addedAt: Date.now() }));
  return id;
}

export async function getImage(id) {
  const t = await tx(['images']);
  return reqToPromise(t.objectStore('images').get(id));
}

export async function deleteImage(id) {
  const t = await tx(['images'], 'readwrite');
  await reqToPromise(t.objectStore('images').delete(id));
}

// Log
export async function appendLog({ entryId = null, action, message }) {
  const t = await tx(['log'], 'readwrite');
  await reqToPromise(t.objectStore('log').add({ entryId, action, message, at: Date.now() }));
}

export async function getLog({ entryId = null, limit = 200 } = {}) {
  const t = await tx(['log']);
  const idx = t.objectStore('log').index('at');
  const out = [];
  return new Promise((resolve, reject) => {
    const req = idx.openCursor(null, 'prev');
    req.onerror = () => reject(req.error);
    req.onsuccess = (e) => {
      const cursor = e.target.result;
      if (!cursor || out.length >= limit) { resolve(out); return; }
      if (entryId === null || cursor.value.entryId === entryId) out.push(cursor.value);
      cursor.continue();
    };
  });
}

// Export / import
export async function exportAll() {
  const [entries, t] = await Promise.all([getAllEntries(), tx(['images', 'log'])]);
  const imagesStore = t.objectStore('images');
  const logStore = t.objectStore('log');
  const [rawImages, log] = await Promise.all([
    reqToPromise(imagesStore.getAll()),
    reqToPromise(logStore.getAll()),
  ]);
  const images = await Promise.all(rawImages.map(async (img) => ({
    id: img.id,
    name: img.name,
    addedAt: img.addedAt,
    data: await blobToDataUrl(img.blob),
  })));
  return { version: 1, exportedAt: Date.now(), entries, images, log };
}

export async function importAll(payload) {
  if (!payload || !payload.entries) throw new Error('Invalid backup file.');
  const t = await tx(['entries', 'images', 'log'], 'readwrite');
  const entriesStore = t.objectStore('entries');
  const imagesStore = t.objectStore('images');
  const logStore = t.objectStore('log');

  for (const entry of payload.entries) await reqToPromise(entriesStore.put(entry));
  for (const img of (payload.images || [])) {
    const blob = await (await fetch(img.data)).blob();
    await reqToPromise(imagesStore.put({ id: img.id, blob, name: img.name, addedAt: img.addedAt }));
  }
  for (const entry of (payload.log || [])) {
    // Drop the existing auto-increment id so we don't collide
    const { id, ...rest } = entry;
    await reqToPromise(logStore.add(rest));
  }
}

function blobToDataUrl(blob) {
  return new Promise((resolve, reject) => {
    const r = new FileReader();
    r.onload = () => resolve(r.result);
    r.onerror = () => reject(r.error);
    r.readAsDataURL(blob);
  });
}
