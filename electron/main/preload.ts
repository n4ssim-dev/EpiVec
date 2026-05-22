import { contextBridge } from "electron";

// Expose uniquement ce qui est nécessaire au renderer
// Ne jamais exposer ipcRenderer directement (sécurité Electron)
contextBridge.exposeInMainWorld("electronAPI", {
  platform: process.platform,
  version: process.env.npm_package_version ?? "0.1.0",
});
