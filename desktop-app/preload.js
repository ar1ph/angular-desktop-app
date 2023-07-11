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
  startBenchmark: (
    selectedModel,
    selectedStrategy,
    query,
    selectedPath,
    selectedSource,
    lines
  ) =>
    ipcRenderer.send(
      "start-benchmark",
      selectedModel,
      selectedStrategy,
      query,
      selectedPath,
      selectedSource,
      lines
    ),
  onBenchmarkData: (callback) => {
    ipcRenderer.on("benchmark-data", (event, message) => callback(message));
  },
  removeBenchmarkDataListener: () => {
    ipcRenderer.removeAllListeners("benchmark-data");
  },
  generateQuery: (path, source) =>
    ipcRenderer.send("generate-query", path, source),
  onQuery: (callback) => {
    ipcRenderer.on("query", (event, query) => callback(query));
  },
  removeQueryListener: () => {
    ipcRenderer.removeAllListeners("query");
  },
});
