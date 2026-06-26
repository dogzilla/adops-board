# Kanban Board — Mobile Responsive Implementation Plan

## Scope
Apply mobile responsive design to the Kanban board using patterns from the AdXactBot WebUI. Desktop experience remains **completely untouched**.

## Files Modified
**One file only**: `/home/desi/kanban/frontend/index.html`
- CSS additions in `<style>` block
- 2 new HTML elements in body
- ~30 lines of JS in `<script>` block

## Docker Deployment
After editing `index.html`:
```bash
cd /home/desi/kanban && docker build -t kanban .
docker stop kanban && docker rm kanban
docker run -d --name kanban -p 8889:8000 -v kanban-data:/app/data kanban
docker update --restart=unless-stopped kanban
```

---

## Implementation Steps

### Step 1: Inject Header Element (HTML)

Insert after `<body>` opening tag, before `#sidebar`:
```html
<header id="board-header">
    <button id="hamburger-btn" class="hamburger">&#x2630;</button>
    <span id="header-title">AdXact <span>Board</span></span>
    <button class="mobile-new-btn" onclick="openNewCardForTodo()">+ New</button>
</header>
```
- Hidden on desktop via CSS (`display: none`)
- Visible on mobile (`≤768px`)
- Hamburger toggles sidebar
- "+ New" provides mobile card creation access

### Step 2: Inject Sidebar Backdrop (HTML)

Insert after `#board-container`, before modals:
```html
<div id="sidebar-backdrop"></div>
```
- Hidden by default
- Shown when sidebar is open
- Clicking dismisses sidebar

### Step 3: Restructure Flex Layout

**Body layout:**
- Desktop: `flex-direction: row` — sidebar + board side-by-side
- Mobile: `flex-direction: column` — header on top, board below

**Fix `#board` height bug:**
- Remove `height: 0` from `#board` CSS
- Keep `flex: 1` + `min-height: 0` for proper flex scrolling

**Add `100dvh` fallback:**
- Body: `height: 100vh; height: 100dvh` (handles mobile address bars)

### Step 4: Sidebar Toggle (CSS + JS)

**CSS (mobile only, `@media (max-width: 768px)`):**
```css
#sidebar {
    position: fixed;
    top: 0;
    left: 0;
    width: 260px;
    height: 100vh;
    transform: translateX(-100%);
    transition: transform 0.3s ease;
    z-index: 25;
}
#sidebar.mobile-open {
    transform: translateX(0);
}
```

**Backdrop CSS (mobile only):**
```css
#sidebar-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.4);
    z-index: 20;
    display: none;
}
#sidebar-backdrop.active {
    display: block;
}
```

**Z-index stacking:** board < backdrop(20) < sidebar(25) < header(30)

### Step 5: JS Toggle Logic (~30 lines)

1. **Hamburger click**: toggle `mobile-open` class on sidebar + `active` class on backdrop
2. **Backdrop click**: close sidebar + backdrop
3. **Card modal open/close**: auto-close sidebar
4. **Column modal open/close**: auto-close sidebar
5. **Header title sync**: update on column rename (if applicable)

### Step 6: Column Width (Mobile)

```css
@media (max-width: 768px) {
    .column {
        min-width: 280px;
        width: 280px;
    }
}
```

### Step 7: Modal Bottom Sheet (Mobile)

```css
@media (max-width: 768px) {
    .modal-content {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        width: 100%;
        max-width: 100%;
        max-height: 85vh;
        border-radius: 16px 16px 0 0;
        margin: 0;
    }
}
```
On mobile: slides up from bottom as a sheet. On desktop: centered (no change).

### Step 8: Padding Adjustments

```css
@media (max-width: 768px) {
    #board {
        padding: 68px 8px 16px 8px; /* top accounts for fixed header */
    }
}
```

---

## What Does NOT Change

- Desktop experience: zero visual or behavioral difference
- All API endpoints and data structures
- Drag-and-drop logic
- Card edit form fields and subtask management
- Column admin functionality
- Database schema or data
- Backend code (main.py)

## Known Limitations (Not Addressed in This Plan)

- **Touch drag-and-drop**: The existing `draggable` + drag events don't work on iOS. This is a pre-existing limitation not introduced or fixed by this mobile plan.
- **Column reordering via drag**: Also drag-based, same iOS limitation.

## Verification Checklist (Post-Deploy)

- [ ] Desktop: page looks identical to pre-change state
- [ ] Mobile (≤768px): sidebar hidden, hamburger visible
- [ ] Mobile: hamburger opens sidebar (slides in from left)
- [ ] Mobile: tapping backdrop closes sidebar
- [ ] Mobile: "+ New" button creates cards
- [ ] Mobile: columns scroll horizontally at 280px width
- [ ] Mobile: card edit modal becomes bottom sheet
- [ ] Mobile: modals close sidebar automatically
- [ ] Drag-and-drop still works on desktop
- [ ] Docker container survives `docker restart`

## Rollback

See `BACKUP_RESTORE_PLAN.md` for full restore procedures. Frontend-only rollback:
```bash
cp /home/desi/kanban/backup_20260626_094129/index.html.pre-mobile.bak /home/desi/kanban/frontend/index.html
cd /home/desi/kanban && docker build -t kanban . && docker restart kanban
```
