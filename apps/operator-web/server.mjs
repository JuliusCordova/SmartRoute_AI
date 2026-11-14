import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const root = path.resolve("./dist");
const PORT = Number(process.env.PORT || "8080");
const MIME = {".html":"text/html; charset=utf-8",".js":"text/javascript; charset=utf-8",".css":"text/css; charset=utf-8",".svg":"image/svg+xml",".png":"image/png",".ico":"image/x-icon"};
const config = {
  gatewayUrl: process.env.GATEWAY_URL || "",
  tileUrl: process.env.OSM_TILE_URL || "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
  firebase: {
    apiKey: process.env.FIREBASE_API_KEY || "",
    appId: process.env.FIREBASE_APP_ID || "",
    authDomain: process.env.FIREBASE_AUTH_DOMAIN || "",
    messagingSenderId: process.env.FIREBASE_MESSAGING_SENDER_ID || "",
    projectId: "proyectopersonal-480420"
  }
};
if (process.env.GOOGLE_CLOUD_PROJECT && process.env.GOOGLE_CLOUD_PROJECT !== "proyectopersonal-480420") {
  throw Error("Wrong GCP project for SmartRoute");
}
const serve = http.createServer((req,res)=>{
  const url = new URL(req.url,"http://localhost");
  res.setHeader("X-Content-Type-Options","nosniff");
  res.setHeader("Referrer-Policy","strict-origin-when-cross-origin");
  res.setHeader("Cache-Control","no-store");
  if(url.pathname==="/health"){res.writeHead(200,{"Content-Type":"application/json"});return res.end(JSON.stringify({status:"ok",service:"smartroute-web"}));}
  if(url.pathname==="/config.js"){
    res.writeHead(200,{"Content-Type":"text/javascript; charset=utf-8"});
    return res.end("window.__SMARTROUTE_CONFIG__ = "+JSON.stringify(config).replace(/</g,"\\u003c")+";");
  }
  const normalized = path.posix.normalize(url.pathname);
  if(normalized.includes("..")){res.writeHead(400);return res.end();}
  const requested = path.resolve(root,"."+normalized);
  const file = requested.startsWith(root+path.sep)&&fs.existsSync(requested)&&fs.statSync(requested).isFile()?requested:path.join(root,"index.html");
  if(!fs.existsSync(file)){res.writeHead(404);return res.end();}
  res.writeHead(200,{"Content-Type":MIME[path.extname(file)]||"application/octet-stream"});
  fs.createReadStream(file).pipe(res);
});
serve.listen(PORT,"0.0.0.0",()=>console.log("SmartRoute web listening",PORT));
