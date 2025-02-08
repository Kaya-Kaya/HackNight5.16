const generateButton = document.getElementById('generate');
const subgrids = document.getElementsByClassName('subgrid');

generateButton.addEventListener('click', async () => {
    const board = await window.sudoku.generate();

    for (let i = 0; i < subgrids.length; i++) {
        const cells = subgrids[i].getElementsByClassName('cell');
        for (let j = 0; j < cells.length; j++) {
            cells[j].innerText = board[i][j] == 0 ? '' : board[i][j];
        }
    }
});