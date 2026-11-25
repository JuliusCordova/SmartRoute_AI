import http from "node:http";
import fs from "node:fs";
import path from "node:path";

const PORT = Number(process.env.PORT || "8080");
const ROOT = process.cwd();
const GATEWAY_URL = process.env.GATEWAY_URL || "";
const APPROVED_GATEWAYS = new Set([
  "https://smartroute-gateway-staging-913797829604.us-central1.run.app",
  "https://smartroute-gateway-staging-mkqutd4koq-uc.a.run.app"
]);
const MIME = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".svg": "image/svg+xml"
};
const MAX_BODY = 4096;
const json = (res, status, data) => {
  res.writeHead(status, {"Content-Type":"application/json; charset=utf-8"});
  res.end(JSON.stringify(data));
};

function serveStatic(req, res, url) {
  if (req.method !== "GET" && req.method !== "HEAD") {
    res.writeHead(405, {"Allow":"GET, HEAD"});
    return res.end();
  }
  const files = new Map([
    ["/", "index.html"],
    ["/index.html", "index.html"],
    ["/main.js", "main.js"],
    ["/tracking.js", "tracking.js"],
    ["/style.css", "style.css"]
  ]);
  const filename = files.get(url.pathname);
  if (!filename) {
    res.writeHead(404);
    return res.end();
  }
  const file = path.join(ROOT, filename);
  res.writeHead(200, {"Content-Type": MIME[path.extname(file)] || "text/plain; charset=utf-8"});
  if (req.method === "HEAD") return res.end();
  fs.createReadStream(file).on("error", () => res.destroy()).pipe(res);
}

async function proxyTracking(req, res) {
  if (req.method !== "POST") {
    res.writeHead(405, {"Allow":"POST"});
    return res.end();
  }
  if (!APPROVED_GATEWAYS.has(GATEWAY_URL)) {
    return json(res, 503, {detail:"Seguimiento no disponible"});
  }
  const chunks = [];
  let count = 0;
  try {
    for await (const chunk of req) {
      count += chunk.length;
      if (count > MAX_BODY) return json(res, 413, {detail:"Solicitud demasiado grande"});
      chunks.push(chunk);
    }
    const body = JSON.parse(Buffer.concat(chunks).toString("utf8"));
    if (!body || typeof body.token !== "string" ||
        !/^[A-Za-z0-9_-]{32,256}$/.test(body.token) ||
        Object.keys(body).length !== 1) {
      return json(res, 400, {detail:"Solicitud inválida"});
    }
    const upstream = await fetch(GATEWAY_URL + "/api/v1/public/tracking", {
      method:"POST",
      redirect:"manual",
      headers:{"Content-Type":"application/json","Accept":"application/json"},
      body:JSON.stringify({token:body.token}),
      signal:AbortSignal.timeout(10000)
    });
    if (upstream.status !== 200) {
      // Do not reveal internal infrastructure or whether a token exists.
      return json(res, 404, {detail:"Seguimiento no disponible"});
    }
    const text = await upstream.text();
    if (text.length > 8192) return json(res, 502, {detail:"Respuesta no disponible"});
    res.writeHead(200, {"Content-Type":"application/json; charset=utf-8"});
    return res.end(text);
  } catch {
    return json(res, 503, {detail:"Seguimiento no disponible"});
  }
}

http.createServer((req, res) => {
  // Do not log URLs, fragments, bodies or tracking tokens.
  res.setHeader("Cache-Control","no-store");
  res.setHeader("Referrer-Policy","no-referrer");
  res.setHeader("X-Robots-Tag","noindex, nofollow");
  res.setHeader("X-Content-Type-Options","nosniff");
  res.setHeader("Content-Security-Policy","default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'");
  const url = new URL(req.url, "http://localhost");
  if (url.pathname === "/health") return json(res, 200, {status:"ok", service:"smartroute-customer-tracking"});
  if (url.pathname === "/api/v1/public/tracking") {
    void proxyTracking(req, res);
    return;
  }
  serveStatic(req, res, url);
}).listen(PORT, "0.0.0.0");
