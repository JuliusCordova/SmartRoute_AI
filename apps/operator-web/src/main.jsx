import React, {useEffect, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import {initializeApp} from "firebase/app";
import {getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut} from "firebase/auth";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./style.css";

const cfg = window.__SMARTROUTE_CONFIG__ || {};
const configured = Boolean(cfg.firebase?.apiKey && cfg.firebase?.appId && cfg.gatewayUrl);
const auth = configured ? getAuth(initializeApp(cfg.firebase)) : null;
const GATEWAY = (cfg.gatewayUrl || "").replace(/\/$/, "");
const LIMA = [-12.095, -77.035];
const inside = (lat,lng) => lat>=-12.30&&lat<=-11.80&&lng>=-77.20&&lng<=-76.80;
const mins = v=>Math.round(v/60).toLocaleString("es-PE")+" min";
const km = v=>(v/1000).toLocaleString("es-PE",{maximumFractionDigits:2})+" km";
const starting = {address_label:"",latitude:"-12.095",longitude:"-77.035"};

async function api(path, method, token, data){
  const resp=await fetch(GATEWAY+path,{method,headers:{"Authorization":"Bearer "+token, ...(data?{"Content-Type":"application/json"}:{})},body:data?JSON.stringify(data):undefined,cache:"no-store"});
  const body=await resp.json().catch(()=>({}));
  if(!resp.ok) throw new Error(typeof body.detail==="string"?body.detail:"Error HTTP "+resp.status);
  return body;
}

function MapPanel({orders,depot,preview}){
  const ref=useRef(null), map=useRef(null), layers=useRef(null);
  useEffect(()=>{
    if(!ref.current)return;
    const m=L.map(ref.current,{zoomControl:true}).setView(LIMA,12);
    const tile=cfg.tileUrl || "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
    L.tileLayer(tile,{maxZoom:19,attribution:'&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'}).addTo(m);
    const group=L.layerGroup().addTo(m);
    map.current=m;layers.current=group;
    setTimeout(()=>m.invalidateSize(),100);
    return ()=>{m.remove();map.current=null;layers.current=null;};
  },[]);
  useEffect(()=>{
    if(!map.current||!layers.current)return;
    const group=layers.current;group.clearLayers();
    const selected=orders.filter(o=>o.checked);
    const valid=selected.filter(o=>inside(o.geo.latitude,o.geo.longitude));
    const points=[[Number(depot.latitude),Number(depot.longitude)]];
    if(inside(...points[0]))L.circleMarker(points[0],{radius:9,color:"#102739",fillColor:"#f0b43d",fillOpacity:1}).bindPopup("Depósito").addTo(group);
    valid.forEach((o,i)=>{
      const pt=[o.geo.latitude,o.geo.longitude];points.push(pt);
      L.circleMarker(pt,{radius:8,color:"#143d4b",fillColor:"#31a8b4",fillOpacity:1}).bindPopup(String(i+1)+". "+o.address_label).addTo(group);
    });
    const byId=Object.fromEntries(valid.map(o=>[o.id,[o.geo.latitude,o.geo.longitude]]));
    if(preview){
      if(preview.route_geometry?.length){
        L.polyline(preview.route_geometry.map(([lng,lat])=>[lat,lng]),{color:"#e5a219",weight:5,opacity:.9}).addTo(group);
      }else{
        const p=[points[0],...preview.ordered_order_ids.map(id=>byId[id]).filter(Boolean),points[0]];
        if(p.length>2)L.polyline(p,{color:"#e5a219",weight:4,dashArray:"7 8"}).addTo(group);
      }
    } else if(points.length>1) {
      L.polyline([...points,points[0]],{color:"#758c9d",weight:2,dashArray:"5 7"}).addTo(group);
    }
    if(points.length>1) map.current.fitBounds(L.latLngBounds(points).pad(.25),{maxZoom:14});
  },[orders,depot,preview]);
  return <div className="mapWrap"><div ref={ref} className="map" /><span className="mapCaption">{preview ? (preview.route_geometry?"Recorrido vial estimado":"Conectores esquemáticos; matriz vial estimada"):"Orden original · conectores esquemáticos"}</span></div>;
}

function App(){
  const [user,setUser]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(""),[orders,setOrders]=useState([]),[form,setForm]=useState(starting),[depot,setDepot]=useState({latitude:"-12.095",longitude:"-77.035"}),[preview,setPreview]=useState(null),[status,setStatus]=useState("Inicia sesión para consultar pedidos.");
  useEffect(()=>auth?onAuthStateChanged(auth,u=>{setUser(u);setPreview(null);setOrders([]);setStatus(u?"Sesión iniciada. Consulta tus pedidos.":"Inicia sesión para consultar pedidos.");},e=>setError(e.code)):undefined,[]);
  async function run(fn){setBusy(true);setError("");try{await fn()}catch(e){setError(e.message)}finally{setBusy(false)}}
  async function token(){if(!auth?.currentUser) throw new Error("Inicia sesión primero");return auth.currentUser.getIdToken();}
  const load=()=>run(async()=>{const x=await api("/api/v1/orders?limit=50","GET",await token());setOrders(x.items.map(o=>({...o,checked:o.status==="PENDING"})));setPreview(null);setStatus(x.items.length+" pedidos recuperados de Firestore.");});
  const create=()=>run(async()=>{
    const lat=Number(form.latitude),lng=Number(form.longitude);
    if(form.address_label.trim().length<3 || !inside(lat,lng))throw new Error("Dirección mínima de 3 caracteres y coordenadas dentro del área piloto de Lima");
    await api("/api/v1/orders","POST",await token(),{address_label:form.address_label.trim(),geo:{latitude:lat,longitude:lng}});
    setForm(starting);
    const x=await api("/api/v1/orders?limit=50","GET",await token());
    setOrders(x.items.map(o=>({...o,checked:o.status==="PENDING"})));setPreview(null);setStatus("Pedido creado y consultado desde Firestore.");
  });
  const optimize=()=>run(async()=>{
    const picked=orders.filter(o=>o.checked);
    if(!picked.length||picked.length>10)throw new Error("Selecciona entre 1 y 10 pedidos");
    if(!inside(Number(depot.latitude),Number(depot.longitude)))throw new Error("Depósito fuera de Lima piloto");
    const p=await api("/api/v1/optimization/preview","POST",await token(),{
      depot:{id:"depot",latitude:Number(depot.latitude),longitude:Number(depot.longitude)},
      stops:picked.map(o=>({id:o.id,latitude:o.geo.latitude,longitude:o.geo.longitude}))
    });
    setPreview(p);setStatus("Secuencia optimizada con matriz vial. Resultado estimado, no observado.");
  });
  const selected=orders.filter(o=>o.checked);
  return <div className="app">
    <header><div className="brand"><span className="brandmark">↝</span><div><b>SmartRoute <em>AI</em></b><small>CENTRO DE OPERACIONES · PILOTO</small></div></div><div className="identity">{user?<><span>{user.email}</span><button className="outline" onClick={()=>run(()=>signOut(auth))}>Salir</button></>:<button onClick={()=>run(()=>signInWithPopup(auth,new GoogleAuthProvider()))} disabled={!configured||busy}>Entrar con Google</button>}</div></header>
    <div className="subhead"><span>UPN Capstone · Lima Metropolitana</span><span className="tag">DATOS DE PEDIDOS SINTÉTICOS · MATRIZ ESTIMADA</span></div>
    {!configured&&<div className="notice error">El frontend aún no tiene configuración Firebase/gateway. Revisa las variables del servicio Cloud Run.</div>}
    {error&&<div className="notice error" role="alert">{error}</div>}
    <div className="notice" role="status">{status}</div>
    <main>
      <aside>
        <section className="panel">
          <div className="panelhead"><h2>01 · Pedidos</h2><button className="outline" onClick={load} disabled={!user||busy}>Actualizar</button></div>
          <p>Registra destinos ficticios para el piloto. Las coordenadas se validan antes de persistir.</p>
          <form onSubmit={e=>{e.preventDefault();create()}} className="form">
            <label>Dirección ficticia<input required minLength={3} maxLength={200} value={form.address_label} onChange={e=>setForm({...form,address_label:e.target.value})} placeholder="Av. Ejemplo 123, Lima"/></label>
            <div className="duo"><label>Latitud<input type="number" step="any" value={form.latitude} onChange={e=>setForm({...form,latitude:e.target.value})}/></label><label>Longitud<input type="number" step="any" value={form.longitude} onChange={e=>setForm({...form,longitude:e.target.value})}/></label></div>
            <button type="submit" disabled={!user||busy}>Guardar pedido</button>
          </form>
          <div className="panelhead"><h3>Pedidos en Firestore</h3><span className="count">{selected.length} seleccionados</span></div>
          <div className="orders">{orders.length?orders.map(o=><label className="order" key={o.id}><input type="checkbox" checked={o.checked} disabled={busy||o.status!=="PENDING"} onChange={e=>{setOrders(old=>old.map(x=>x.id===o.id?{...x,checked:e.target.checked}:x));setPreview(null)}}/><span><strong>{o.address_label}</strong><small>{o.status} · {o.id.slice(0,8)}</small></span></label>):<p className="empty">No hay pedidos cargados. Pulsa Actualizar.</p>}</div>
        </section>
        <section className="panel">
          <div className="panelhead"><h2>02 · Optimizar ruta</h2><span className="count">1 vehículo · máx. 10 paradas</span></div>
          <div className="duo"><label>Depósito · latitud<input type="number" step="any" value={depot.latitude} onChange={e=>{setDepot({...depot,latitude:e.target.value});setPreview(null)}}/></label><label>Longitud<input type="number" step="any" value={depot.longitude} onChange={e=>{setDepot({...depot,longitude:e.target.value});setPreview(null)}}/></label></div>
          <button className="accent" disabled={!user||busy||selected.length<1||selected.length>10} onClick={optimize}>{busy?"Procesando…":"Optimizar con OR-Tools"}</button>
          <p className="fineprint">Matrices obtenidas desde openrouteservice en el backend; requieren una clave configurada de forma segura en GCP.</p>
        </section>
      </aside>
      <article>
        <section className="panel mapSection"><div className="panelhead"><div><h2>Mapa de operaciones</h2><p>OpenStreetMap · puntos seleccionados · recorridos</p></div><span className="count">Lima, Perú</span></div><MapPanel orders={orders} depot={depot} preview={preview}/></section>
        <section className="panel results"><div className="panelhead"><h2>03 · Comparación</h2><span className="count">{preview?"ESTIMADO":"PENDIENTE DE CÁLCULO"}</span></div>
          {preview?<><div className="metrics">
            <div className="metric"><small>Orden original</small><strong>{mins(preview.baseline_seconds)}</strong><span>{km(preview.baseline_meters)}</span></div>
            <div className="metric chosen"><small>OR-Tools</small><strong>{mins(preview.optimized_seconds)}</strong><span>{km(preview.optimized_meters)}</span></div>
            <div className="metric"><small>Mejora estimada</small><strong>{preview.improvement_pct.toFixed(2)}%</strong><span>Sobre la misma matriz</span></div>
          </div><div className="sequence"><b>Secuencia calculada:</b> Depósito → {preview.ordered_order_ids.map(id=>orders.find(o=>o.id===id)?.address_label||id).join(" → ")} → Depósito</div><p className="fineprint">Fuente: {preview.matrix_provider} · Huella matriz: {preview.matrix_fingerprint.slice(0,12)}… · {preview.warnings.join(". ")}. No hay ahorro real observado.</p></>:<div className="empty">Selecciona pedidos y solicita una optimización para comparar recorridos. No se genera ninguna cifra sin datos de la matriz vial.</div>}
        </section>
      </article>
    </main><footer>SmartRoute AI · MVP académico · La ruta calculada es una previsualización y no se publica ni asigna automáticamente.</footer>
  </div>;
}
createRoot(document.getElementById("root")).render(<App/>);
