const express = require("express");
const path = require("path");
const os = require("os");

const app = express();
const PORT = process.env.PORT || 3000;

function getLocalIp() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === "IPv4" && !iface.internal) {
        return iface.address;
      }
    }
  }
  return "127.0.0.1";
}

// Serve static frontend files
app.use(express.static(path.join(__dirname, "public")));

// Route all requests to index.html
app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "public", "index.html"));
});

const localIp = getLocalIp();

app.listen(PORT, "0.0.0.0", () => {
  console.log(`=======================================================`);
  console.log(`🚀 Dalal Street AI Trading Dashboard running at:`);
  console.log(`👉 Local PC:   http://localhost:${PORT}`);
  console.log(`👉 Phone/LAN:  http://${localIp}:${PORT}`);
  console.log(`🔗 Backend:    http://${localIp}:8000`);
  console.log(`=======================================================`);
});
