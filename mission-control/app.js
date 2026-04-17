import * as DB from './db.js';

const TYPES = [
  { id: 'character', label: 'Character' },
  { id: 'scenario',  label: 'Scenario' },
  { id: 'prop',      label: 'Prop' },
  { id: 'mechanic',  label: 'Mechanic' },
  { id: 'feature',   label: 'Feature' },
  { id: 'reference', label: 'Reference' },
  { id: 'note',      label: 'Note' },
];

const STATUSES = [
  { id: 'idea',    label: 'Idea' },
  { id: 'active',  label: 'In Progress' },
  { id: 'done',    label: 'Done' },
  { id: 'blocked', label: 'Blocked' },
];

const state = {
  entries: [],
  filterType: null,
  filterStatus: null,
  search: '',
  editing: null,       // entry being edited (copy), or null
  editingImages: [],   // [{ id, url, name, isNew?, blob? }]
  viewing: null,       // entry being viewed
  imageUrlCache: new Map(), // imageId -> object url
};

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);

init();

async function init() {
  populateSelect($('#f-type'), TYPES);
  populateSelect($('#f-status'), STATUSES);

  state.entries = await DB.getAllEntries();
  renderFilters();
  renderGrid();
  wireEvents();
}

function populateSelect(el, options) {
  el.innerHTML = options.map((o) => `<option value="${o.id}">${o.label}</option>`).join('');
}

// --- rendering --------------------------------------------------------------
function renderFilters() {
  const counts = (key, list) => {
    const counts = {};
    for (const e of state.entries) counts[e[key]] = (counts[e[key]] || 0) + 1;
    return list.map((o) => ({ ...o, count: counts[o.id] || 0 }));
  };
  renderFilterList($('#filter-type'), counts('type', [{ id: null, label: 'All' }, ...TYPES]), 'filterType');
  renderFilterList($('#filter-status'), counts('status', [{ id: null, label: 'All' }, ...STATUSES]), 'filterStatus');
}

function renderFilterList(el, options, stateKey) {
  el.innerHTML = options.map((o) => {
    const active = state[stateKey] === o.id ? 'active' : '';
    const count = o.id === null
      ? state.entries.length
      : (o.count ?? 0);
    return `<li data-val="${o.id ?? ''}" class="${active}">
      <span>${o.label}</span><span class="count">${count}</span>
    </li>`;
  }).join('');
  el.querySelectorAll('li').forEach((li) => {
    li.addEventListener('click', () => {
      const v = li.dataset.val || null;
      state[stateKey] = v;
      renderFilters();
      renderGrid();
    });
  });
}

function renderGrid() {
  const grid = $('#grid');
  const empty = $('#empty');
  const q = state.search.trim().toLowerCase();

  const filtered = state.entries.filter((e) => {
    if (state.filterType && e.type !== state.filterType) return false;
    if (state.filterStatus && e.status !== state.filterStatus) return false;
    if (q) {
      const hay = (e.title + ' ' + e.description + ' ' + (e.tags || []).join(' ')).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  }).sort((a, b) => b.updatedAt - a.updatedAt);

  $('#entry-count').textContent = `${filtered.length} of ${state.entries.length}`;
  $('#main-title').textContent = headerTitle();

  if (!filtered.length) {
    grid.innerHTML = '';
    empty.classList.remove('hidden');
    return;
  }
  empty.classList.add('hidden');
  grid.innerHTML = '';
  for (const e of filtered) grid.appendChild(renderCard(e));
}

function headerTitle() {
  const parts = [];
  if (state.filterType) parts.push(TYPES.find((t) => t.id === state.filterType)?.label || state.filterType);
  if (state.filterStatus) parts.push(STATUSES.find((s) => s.id === state.filterStatus)?.label || state.filterStatus);
  return parts.length ? parts.join(' · ') : 'All entries';
}

function renderCard(entry) {
  const el = document.createElement('article');
  el.className = 'card';
  el.tabIndex = 0;

  const thumb = document.createElement('div');
  thumb.className = 'card-thumb';
  if (entry.imageIds && entry.imageIds.length) {
    loadImageUrl(entry.imageIds[0]).then((url) => {
      if (url) thumb.style.backgroundImage = `url(${url})`;
    });
  } else {
    thumb.textContent = labelFor(TYPES, entry.type).toUpperCase();
  }
  el.appendChild(thumb);

  const body = document.createElement('div');
  body.className = 'card-body';
  body.innerHTML = `
    <div class="card-title"></div>
    <div class="card-desc"></div>
    <div class="card-meta">
      <span class="pill type">${labelFor(TYPES, entry.type)}</span>
      <span class="pill status-${entry.status}">${labelFor(STATUSES, entry.status)}</span>
    </div>
  `;
  body.querySelector('.card-title').textContent = entry.title || 'Untitled';
  body.querySelector('.card-desc').textContent = entry.description || '';
  el.appendChild(body);

  el.addEventListener('click', () => openViewer(entry.id));
  return el;
}

function labelFor(list, id) {
  return (list.find((x) => x.id === id) || {}).label || id;
}

async function loadImageUrl(imageId) {
  if (state.imageUrlCache.has(imageId)) return state.imageUrlCache.get(imageId);
  const img = await DB.getImage(imageId);
  if (!img) return null;
  const url = URL.createObjectURL(img.blob);
  state.imageUrlCache.set(imageId, url);
  return url;
}

// --- editor -----------------------------------------------------------------
function openEditor(entry = null) {
  state.editing = entry ? JSON.parse(JSON.stringify(entry)) : {
    id: DB.uid(),
    title: '',
    description: '',
    type: 'character',
    status: 'idea',
    tags: [],
    imageIds: [],
    createdAt: Date.now(),
    updatedAt: Date.now(),
  };
  state.editingImages = [];

  $('#editor-title').textContent = entry ? 'Edit entry' : 'New entry';
  $('#f-title').value = state.editing.title || '';
  $('#f-description').value = state.editing.description || '';
  $('#f-type').value = state.editing.type;
  $('#f-status').value = state.editing.status;
  $('#f-tags').value = (state.editing.tags || []).join(', ');
  $('#delete-entry').classList.toggle('hidden', !entry);

  (async () => {
    state.editingImages = [];
    for (const id of state.editing.imageIds || []) {
      const url = await loadImageUrl(id);
      if (url) state.editingImages.push({ id, url });
    }
    renderThumbs();
  })();

  showModal('editor');
}

function renderThumbs() {
  const el = $('#thumbs');
  el.innerHTML = '';
  state.editingImages.forEach((img, i) => {
    const t = document.createElement('div');
    t.className = 'thumb';
    t.innerHTML = `
      <img src="${img.url}" alt="" />
      <button class="remove" type="button" aria-label="Remove">×</button>
    `;
    t.querySelector('img').addEventListener('click', () => showLightbox(img.url));
    t.querySelector('.remove').addEventListener('click', (ev) => {
      ev.stopPropagation();
      state.editingImages.splice(i, 1);
      renderThumbs();
    });
    el.appendChild(t);
  });
}

async function saveEntry() {
  const e = state.editing;
  if (!e) return;

  const newTitle = $('#f-title').value.trim();
  if (!newTitle) { $('#f-title').focus(); return; }

  const newDesc = $('#f-description').value.trim();
  const newType = $('#f-type').value;
  const newStatus = $('#f-status').value;
  const newTags = $('#f-tags').value.split(',').map((t) => t.trim()).filter(Boolean);

  const existing = await DB.getEntry(e.id);
  const diff = computeDiff(existing, { title: newTitle, description: newDesc, type: newType, status: newStatus, tags: newTags });

  // Persist any new image blobs
  const persistedImageIds = [];
  for (const img of state.editingImages) {
    if (img.isNew && img.blob) {
      const id = await DB.putImage(img.blob, img.name || 'image');
      persistedImageIds.push(id);
    } else {
      persistedImageIds.push(img.id);
    }
  }

  const prevImages = new Set(existing?.imageIds || []);
  const nextImages = new Set(persistedImageIds);
  const removed = [...prevImages].filter((id) => !nextImages.has(id));
  const added   = [...nextImages].filter((id) => !prevImages.has(id));
  for (const id of removed) await DB.deleteImage(id);

  const entry = {
    ...e,
    title: newTitle,
    description: newDesc,
    type: newType,
    status: newStatus,
    tags: newTags,
    imageIds: persistedImageIds,
    createdAt: existing?.createdAt || e.createdAt || Date.now(),
    updatedAt: Date.now(),
  };

  await DB.putEntry(entry);

  if (!existing) {
    await DB.appendLog({ entryId: entry.id, action: 'created', message: `Created "${entry.title}"` });
  } else {
    for (const part of diff) {
      await DB.appendLog({ entryId: entry.id, action: 'updated', message: part });
    }
    if (added.length) await DB.appendLog({ entryId: entry.id, action: 'image-added', message: `Added ${added.length} image(s)` });
    if (removed.length) await DB.appendLog({ entryId: entry.id, action: 'image-removed', message: `Removed ${removed.length} image(s)` });
    if (!diff.length && !added.length && !removed.length) {
      await DB.appendLog({ entryId: entry.id, action: 'saved', message: 'Saved (no changes)' });
    }
  }

  state.entries = await DB.getAllEntries();
  hideModal('editor');
  renderFilters();
  renderGrid();
}

function computeDiff(oldE, newE) {
  if (!oldE) return [];
  const msgs = [];
  if (oldE.title !== newE.title) msgs.push(`Title: "${oldE.title}" → "${newE.title}"`);
  if (oldE.type !== newE.type) msgs.push(`Type: ${oldE.type} → ${newE.type}`);
  if (oldE.status !== newE.status) msgs.push(`Status: ${oldE.status} → ${newE.status}`);
  if ((oldE.description || '') !== (newE.description || '')) msgs.push('Description updated');
  const oldTags = (oldE.tags || []).join(','), newTags = (newE.tags || []).join(',');
  if (oldTags !== newTags) msgs.push(`Tags: [${oldTags}] → [${newTags}]`);
  return msgs;
}

async function deleteCurrent() {
  if (!state.editing) return;
  if (!confirm(`Delete "${state.editing.title}"? This cannot be undone.`)) return;
  const entry = await DB.getEntry(state.editing.id);
  if (entry) {
    for (const id of entry.imageIds || []) await DB.deleteImage(id);
  }
  await DB.deleteEntry(state.editing.id);
  await DB.appendLog({ entryId: null, action: 'deleted', message: `Deleted "${state.editing.title}"` });
  state.entries = await DB.getAllEntries();
  hideModal('editor');
  renderFilters();
  renderGrid();
}

// --- viewer -----------------------------------------------------------------
async function openViewer(id) {
  const entry = await DB.getEntry(id);
  if (!entry) return;
  state.viewing = entry;

  $('#viewer-title').textContent = entry.title;
  $('#viewer-type').textContent = labelFor(TYPES, entry.type);
  $('#viewer-status').textContent = labelFor(STATUSES, entry.status);
  $('#viewer-status').className = `pill status-${entry.status}`;
  $('#viewer-description').textContent = entry.description || '(No description)';

  const tags = $('#viewer-tags');
  tags.innerHTML = (entry.tags || []).map((t) => `<span class="tag">${escapeHtml(t)}</span>`).join('');

  const imgs = $('#viewer-images');
  imgs.innerHTML = '';
  for (const imgId of entry.imageIds || []) {
    const url = await loadImageUrl(imgId);
    if (!url) continue;
    const img = document.createElement('img');
    img.src = url;
    img.addEventListener('click', () => showLightbox(url));
    imgs.appendChild(img);
  }

  const dates = document.querySelector('.viewer-dates');
  dates.textContent = `Created ${fmtDate(entry.createdAt)} · Updated ${fmtDate(entry.updatedAt)}`;

  const log = await DB.getLog({ entryId: entry.id, limit: 50 });
  $('#viewer-log').innerHTML = log.length
    ? log.map(renderLogItem).join('')
    : '<li class="subtle">No activity yet.</li>';

  showModal('viewer');
}

function renderLogItem(l) {
  return `<li><span class="when">${fmtDate(l.at)}</span><span class="who">${l.action}</span> ${escapeHtml(l.message)}</li>`;
}

function fmtDate(ts) {
  const d = new Date(ts);
  return d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
}

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

// --- image input ------------------------------------------------------------
async function addFiles(fileList) {
  for (const file of fileList) {
    if (!file.type.startsWith('image/')) continue;
    const url = URL.createObjectURL(file);
    state.editingImages.push({
      id: 'new_' + Math.random().toString(36).slice(2),
      url, blob: file, name: file.name, isNew: true,
    });
  }
  renderThumbs();
}

function showLightbox(url) {
  const lb = $('#lightbox');
  $('#lightbox-img').src = url;
  lb.classList.remove('hidden');
  lb.setAttribute('aria-hidden', 'false');
}
function hideLightbox() {
  $('#lightbox').classList.add('hidden');
  $('#lightbox-img').src = '';
}

// --- modals -----------------------------------------------------------------
function showModal(id) {
  $('#' + id).classList.remove('hidden');
  $('#' + id).setAttribute('aria-hidden', 'false');
}
function hideModal(id) {
  $('#' + id).classList.add('hidden');
  $('#' + id).setAttribute('aria-hidden', 'true');
}

// --- export / import --------------------------------------------------------
async function exportData() {
  const payload = await DB.exportAll();
  const blob = new Blob([JSON.stringify(payload, null, 2)], { type: 'application/json' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `mission-control-${new Date().toISOString().slice(0, 10)}.json`;
  a.click();
  URL.revokeObjectURL(a.href);
}

async function importData(file) {
  try {
    const text = await file.text();
    const payload = JSON.parse(text);
    await DB.importAll(payload);
    await DB.appendLog({ entryId: null, action: 'imported', message: `Imported backup (${(payload.entries || []).length} entries)` });
    state.entries = await DB.getAllEntries();
    renderFilters();
    renderGrid();
    alert('Import complete.');
  } catch (err) {
    alert('Import failed: ' + err.message);
  }
}

// --- global log -------------------------------------------------------------
async function openGlobalLog() {
  const log = await DB.getLog({ entryId: null, limit: 300 });
  $('#global-log').innerHTML = log.length
    ? log.map(renderLogItem).join('')
    : '<li class="subtle">No activity yet.</li>';
  showModal('log-modal');
}

// --- wiring -----------------------------------------------------------------
function wireEvents() {
  $('#new-entry').addEventListener('click', () => openEditor(null));
  $('#save-entry').addEventListener('click', saveEntry);
  $('#delete-entry').addEventListener('click', deleteCurrent);
  $('#viewer-edit').addEventListener('click', () => {
    hideModal('viewer');
    openEditor(state.viewing);
  });
  $('#view-log').addEventListener('click', openGlobalLog);

  $('#search').addEventListener('input', (e) => { state.search = e.target.value; renderGrid(); });

  $('#browse-btn').addEventListener('click', () => $('#file-input').click());
  $('#file-input').addEventListener('change', (e) => { if (e.target.files) addFiles(e.target.files); e.target.value = ''; });

  const dz = $('#dropzone');
  ['dragenter', 'dragover'].forEach((evt) => dz.addEventListener(evt, (e) => { e.preventDefault(); dz.classList.add('drag'); }));
  ['dragleave', 'drop'].forEach((evt) => dz.addEventListener(evt, (e) => { e.preventDefault(); dz.classList.remove('drag'); }));
  dz.addEventListener('drop', (e) => { if (e.dataTransfer?.files) addFiles(e.dataTransfer.files); });

  $('#export').addEventListener('click', exportData);
  $('#import').addEventListener('click', () => $('#import-file').click());
  $('#import-file').addEventListener('change', (e) => { if (e.target.files[0]) importData(e.target.files[0]); e.target.value = ''; });

  // close buttons inside modals + backdrop click
  document.body.addEventListener('click', (e) => {
    if (e.target.matches('[data-close]')) {
      const modal = e.target.closest('.modal');
      if (modal) hideModal(modal.id);
    } else if (e.target.classList.contains('modal')) {
      hideModal(e.target.id);
    }
  });

  $('#lightbox').addEventListener('click', hideLightbox);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      $$('.modal').forEach((m) => { if (!m.classList.contains('hidden')) hideModal(m.id); });
      if (!$('#lightbox').classList.contains('hidden')) hideLightbox();
    }
    if (e.key === 'n' && !e.target.matches('input, textarea, select')) openEditor(null);
  });
}
