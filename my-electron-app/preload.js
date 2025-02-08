const { contextBridge, ipcRenderer } = require('electron/renderer');

contextBridge.exposeInMainWorld('sudoku', {
    generate: () => ipcRenderer.invoke('generate')
})