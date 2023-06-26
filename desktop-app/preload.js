const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("electron", {
  openDirectory: () => ipcRenderer.send("open-dir-dialog"),
  onDirectorySelected: (callback) => {
    ipcRenderer.on("selected-directory", (event, path) => callback(path));
  },
  removeDirectorySelectedListener: () => {
    ipcRenderer.removeAllListeners("selected-directory");
  },
  displayFiles: (path) => ipcRenderer.send("display-files", path),
  onDirectoryFiles: (callback) => {
    ipcRenderer.on("directory-files", (event, content) => callback(content));
  },
  removeDirectoryFilesListener: () => {
    ipcRenderer.removeAllListeners("directory-files");
  },
});
