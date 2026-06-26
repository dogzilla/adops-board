<!DOCTYPE html>
<html>
<head>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: sans-serif;
    height: 100vh;
    overflow: hidden;
    display: flex;
}
#sidebar {
    width: 260px;
    background: #fff;
    border-right: 1px solid #e0e0e0;
    display: flex;
    flex-direction: column;
    flex-shrink: 0;
}
#board-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    overflow: hidden;
}
#board {
    flex: 1;
    overflow-x: auto;
    overflow-y: hidden;
    min-height: 0;
    padding: 24px;
    display: flex;
    gap: 16px;
    align-items: stretch;
}
.column {
    width: 320px;
    flex-shrink: 0;
    min-height: 0;
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    display: flex;
    flex-direction: column;
}
.column-cards {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
}
.card {
    background: #fff;
    border: 1px solid #e0e0e0;
    border-radius: 8px;
    margin-bottom: 12px;
    height: 60px;
}
</style>
</head>
<body>
<div id="sidebar">
    <div style="padding: 20px; border-bottom: 1px solid #e0e0e0;">
        <h1 style="font-size: 18px; font-weight: 700;">AdXact <span style="color: #f97316;">AdOps Board</span></h1>
    </div>
    <div style="flex: 1;"></div>
</div>
<div id="board-container">
    <div id="board">
        <div class="column">
            <div style="padding: 16px; border-bottom: 1px solid #e0e0e0;">
                <span style="font-size: 15px; font-weight: 600;">To Do</span>
            </div>
            <div class="column-cards" id="cards">
                <!-- 30 cards -->
            </div>
        </div>
    </div>
</div>
<script>
const container = document.getElementById('cards');
for (let i = 1; i <= 30; i++) {
    const card = document.createElement('div');
    card.className = 'card';
    card.textContent = `Card ${i}`;
    container.appendChild(card);
}

// Log computed styles
const col = document.querySelector('.column');
const cards = document.querySelector('.column-cards');
const board = document.getElementById('board');

setTimeout(() => {
    console.log('=== Computed Styles ===');
    console.log('body height:', getComputedStyle(document.body).height);
    console.log('board-container height:', getComputedStyle(document.getElementById('board-container')).height);
    console.log('board height:', getComputedStyle(board).height);
    console.log('board min-height:', getComputedStyle(board).minHeight);
    console.log('board display:', getComputedStyle(board).display);
    console.log('board align-items:', getComputedStyle(board).alignItems);
    console.log('column height:', getComputedStyle(col).height);
    console.log('column min-height:', getComputedStyle(col).minHeight);
    console.log('column flex-shrink:', getComputedStyle(col).flexShrink);
    console.log('column display:', getComputedStyle(col).display);
    console.log('column-cards height:', getComputedStyle(cards).height);
    console.log('column-cards overflow-y:', getComputedStyle(cards).overflowY);
    console.log('column-cards flex:', getComputedStyle(cards).flex);
    console.log('=== Actual Dimensions ===');
    console.log('body clientHeight:', document.body.clientHeight);
    console.log('board-container clientHeight:', document.getElementById('board-container').clientHeight);
    console.log('board clientHeight:', board.clientHeight);
    console.log('board scrollHeight:', board.scrollHeight);
    console.log('column clientHeight:', col.clientHeight);
    console.log('column scrollHeight:', col.scrollHeight);
    console.log('cards clientHeight:', cards.clientHeight);
    console.log('cards scrollHeight:', cards.scrollHeight);
    console.log('cards has scrollbar:', cards.scrollHeight > cards.clientHeight);
}, 100);
</script>
</body>
</html>
