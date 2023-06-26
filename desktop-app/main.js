const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const fs = require("fs");

let win;

function createWindow() {
  win = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      enableRemoteModule: true,
      preload: __dirname + "/preload.js",
    },
  });

  win.loadFile("dist/desktop-app/index.html");

  win.on("closed", () => {
    win = null;
  });
}

app.on("ready", createWindow);

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") {
    app.quit();
  }
});

app.on("activate", () => {
  if (win === null) {
    createWindow();
  }
});

ipcMain.on("open-dir-dialog", (event) => {
  dialog
    .showOpenDialog(win, {
      properties: ["openDirectory"],
    })
    .then((result) => {
      if (!result.canceled) {
        event.sender.send("selected-directory", result.filePaths[0]);
      }
    })
    .catch((err) => {
      console.log(err);
    });
});

ipcMain.on("display-files", (event, path) => {
  let content = [];
  fs.readdir(path, (err, files) => {
    files.forEach((file) => {
      console.log(file);
      content.push(file);
    });
    console.log("Content", content);
    event.sender.send("directory-files", content);
  });
});
