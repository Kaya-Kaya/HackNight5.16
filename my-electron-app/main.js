const { app, BrowserWindow, ipcMain } = require('electron/main');
const { execFile } = require('node:child_process');
const path = require('node:path');

const createWindow = () => {
    const win = new BrowserWindow({
        show: false,
        webPreferences: {
            preload: path.join(__dirname, 'preload.js'),
        }
    });

    win.maximize();
    win.show();

    win.loadFile('index.html');
};

app.whenReady().then(() => {
    createWindow();
});

app.on('window-all-closed', () => {
    app.quit();
});

ipcMain.handle('generate', async () => {
    const board = generateSudokuBoard();
    return board;
});

function generateSudokuBoard() {
    return new Promise((resolve, reject) => {
        const executablePath = path.join(__dirname, 'dist', 'test');
        execFile(executablePath, (error, stdout, stderr) => {
            if (error) {
                reject(error);
                return;
            }
            resolve(JSON.parse(stdout));
        });
    });
};