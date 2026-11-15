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
const starting = {address_label:"",latitude:null,longitude:null,precision:null};

async function api(path, method, token, data){
  const resp=await fetch(GATEWAY+path,{method,headers:{"Authorization":"Bearer "+token, ...(data?{"Content-Type":"application/json"}:{})},body:data?JSON.stringify(data):undefined,cache:"no-store"});
  const body=await resp.json().catch(()=>({}));
  if(!resp.ok) throw new Error(typeof body.detail==="string"?body.detail:"Error HTTP "+resp.status);
  return body;
}

function MapPanel({orders,depot,preview,chosen}){
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
    const refreshSaved=()=>run(async()=>{
    const x=await api("/api/v1/optimized-routes?limit=20","GET",await token());
    setSavedRoutes(x.items||[]);
    setStatus((x.items||[]).length+" rutas optimizadas recuperadas de Firestore.");
  });
  const saveOptimized=()=>run(async()=>{
    if(!preview || !pendingSaveKey.current) throw new Error("Primero optimiza los pedidos");
    const picked=orders.filter(o=>o.checked);
    if(!picked.length || picked.length>10) throw new Error("Selecciona de 1 a 10 pedidos");
    if(!inside(Number(depot.latitude),Number(depot.longitude))) throw new Error("Depósito fuera de Lima piloto");
    const saved=await api("/api/v1/optimized-routes","POST",await token(),{
      depot:{latitude:Number(depot.latitude),longitude:Number(depot.longitude)},
      order_ids:picked.map(o=>o.id),
      idempotency_key:pendingSaveKey.current,
    });
    setSavedRoute(saved);setPreview(null);pendingSaveKey.current=null;
    const tkn=await token();
    const [ordersResult,routesResult]=await Promise.all([
      api("/api/v1/orders?limit=50","GET",tkn),
      api("/api/v1/optimized-routes?limit=20","GET",tkn),
    ]);
    setOrders(ordersResult.items.map(o=>({...o,checked:false})));
    setSavedRoutes(routesResult.items||[]);
    setStatus("Ruta "+saved.id.slice(0,8)+" guardada en Firestore como PLANNED. Pedidos reservados.");
  });
  const selected=orders.filter(o=>o.checked);
    const valid=selected.filter(o=>inside(o.geo.latitude,o.geo.longitude));
    const points=[[Number(depot.latitude),Number(depot.longitude)]];
    if(inside(...points[0]))L.circleMarker(points[0],{radius:9,color:"#102739",fillColor:"#f0b43d",fillOpacity:1}).bindPopup("Depósito").addTo(group);
    valid.forEach((o,i)=>{
      const pt=[o.geo.latitude,o.geo.longitude];points.push(pt);
      L.circleMarker(pt,{radius:8,color:"#143d4b",fillColor:"#31a8b4",fillOpacity:1}).bindPopup(String(i+1)+". "+o.address_label).addTo(group);
    });
    if(chosen && inside(chosen.latitude,chosen.longitude)) {
      const pt=[chosen.latitude,chosen.longitude];points.push(pt);
      L.circleMarker(pt,{radius:11,color:"#1d6a5f",fillColor:"#94e2a9",fillOpacity:1,weight:3}).bindPopup("Nuevo destino por confirmar: "+chosen.label).addTo(group);
    }
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
  },[orders,depot,preview,chosen]);
  return <div className="mapWrap"><div ref={ref} className="map" /><span className="mapCaption">{preview ? (preview.route_geometry?"Recorrido vial estimado":"Conectores esquemáticos; matriz vial estimada"):"Orden original · conectores esquemáticos"}</span></div>;
}

function App(){
  const [user,setUser]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(""),[orders,setOrders]=useState([]),[form,setForm]=useState(starting),[depot,setDepot]=useState({latitude:"-12.095",longitude:"-77.035"}),[preview,setPreview]=useState(null),[status,setStatus]=useState("Inicia sesión para consultar pedidos.");
  const [suggestions,setSuggestions]=useState([]),[searchState,setSearchState]=useState(""),[confirmed,setConfirmed]=useState(false),[searching,setSearching]=useState(false);
  const [savedRoutes,setSavedRoutes]=useState([]),[savedRoute,setSavedRoute]=useState(null);
  const pendingSaveKey=useRef(null);
  useEffect(()=>auth?onAuthStateChanged(auth,u=>{setUser(u);setPreview(null);setOrders([]);setSavedRoutes([]);setSavedRoute(null);pendingSaveKey.current=null;setStatus(u?"Sesión iniciada. Consulta tus pedidos.":"Inicia sesión para consultar pedidos.");},e=>setError(e.code)):undefined,[]);
  useEffect(()=>{
    if(!user||form.latitude!==null||form.address_label.trim().length<3){
      setSuggestions([]);setSearchState("");setSearching(false);return;
    }
    let live=true;
    setSearching(true);setSearchState("Buscando direcciones…");
    const t=setTimeout(async()=>{
      try{
        const tkn=await user.getIdToken();
        const result=await api("/api/v1/geocoding/autocomplete?q="+encodeURIComponent(form.address_label.trim()),"GET",tkn);
        if(live){setSuggestions(result.items||[]);setSearchState(result.notice||(result.items?.length?"Selecciona una dirección de la lista.":"Sin resultados en el área piloto."));}
      }catch(e){if(live){setSuggestions([]);setSearchState("No se pudo buscar: "+e.message);}}
      finally{if(live)setSearching(false);}
    },500);
    return ()=>{live=false;clearTimeout(t);};
  },[form.address_label,form.latitude,user]);
  function selectAddress(s){
    setForm({address_label:s.label,latitude:s.latitude,longitude:s.longitude,precision:s.precision});
    setSuggestions([]);setSearchState("");setConfirmed(s.precision==="precise");setPreview(null);pendingSaveKey.current=null;
  }
  async function run(fn){setBusy(true);setError("");try{await fn()}catch(e){setError(e.message)}finally{setBusy(false)}}
  async function token(){if(!auth?.currentUser) throw new Error("Inicia sesión primero");return auth.currentUser.getIdToken();}
  const load=()=>run(async()=>{const x=await api("/api/v1/orders?limit=50","GET",await token());setOrders(x.items.map(o=>({...o,checked:o.status==="PENDING"})));setPreview(null);pendingSaveKey.current=null;setStatus(x.items.length+" pedidos recuperados de Firestore.");});
  const create=()=>run(async()=>{
    if(form.latitude===null||form.longitude===null) throw new Error("Selecciona una dirección de las sugerencias antes de guardar");
    const lat=Number(form.latitude),lng=Number(form.longitude);
    if(!inside(lat,lng))throw new Error("ALERTA: destino fuera de la zona del piloto en Lima");
    if(form.precision!=="precise"&&!confirmed)throw new Error("ALERTA: ubicación aproximada; confirma el punto del mapa antes de guardar");
    await api("/api/v1/orders","POST",await token(),{address_label:form.address_label.trim(),geo:{latitude:lat,longitude:lng}});
    setForm(starting);setConfirmed(false);setSuggestions([]);
    const x=await api("/api/v1/orders?limit=50","GET",await token());
    setOrders(x.items.map(o=>({...o,checked:o.status==="PENDING"})));setPreview(null);pendingSaveKey.current=null;setStatus("Pedido creado y consultado desde Firestore.");
  });
  const optimize=()=>run(async()=>{
    const picked=orders.filter(o=>o.checked);
    if(!picked.length||picked.length>10)throw new Error("Selecciona entre 1 y 10 pedidos");
    if(!inside(Number(depot.latitude),Number(depot.longitude)))throw new Error("Depósito fuera de Lima piloto");
    const p=await api("/api/v1/optimization/preview","POST",await token(),{
      depot:{id:"depot",latitude:Number(depot.latitude),longitude:Number(depot.longitude)},
      stops:picked.map(o=>({id:o.id,latitude:o.geo.latitude,longitude:o.geo.longitude}))
    });
    setPreview(p);pendingSaveKey.current=crypto.randomUUID();setStatus("Secuencia optimizada con matriz vial. Resultado estimado, no observado.");
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
          <p>Busca una dirección ficticia, selecciona una sugerencia y confirma el punto sobre el mapa. No necesitas ingresar coordenadas.</p>
          <form onSubmit={e=>{e.preventDefault();create()}} className="form">
            <label htmlFor="address-search">Buscar dirección (piloto Lima)</label>
            <input id="address-search" required minLength={3} maxLength={120} autoComplete="off" value={form.address_label}
              onChange={e=>{setForm({address_label:e.target.value,latitude:null,longitude:null,precision:null});setConfirmed(false);setSuggestions([]);}}
              placeholder="Ej. Av. Arequipa 1200, Lima" role="combobox" aria-autocomplete="list" aria-expanded={suggestions.length>0} aria-controls="address-options"/>
            {searching&&<span className="lookup-status">Buscando…</span>}
            {suggestions.length>0&&<div id="address-options" className="suggestions" role="listbox" aria-label="Direcciones encontradas">
              {suggestions.map(s=><button type="button" role="option" aria-selected="false" key={s.id} className="suggestion"
                onClick={()=>selectAddress(s)}><span>📍 {s.label}</span><small>{s.precision==="precise"?"Número identificado":"Ubicación aproximada"}</small></button>)}
            </div>}
            {!form.precision&&searchState&&!searching&&<div className="lookup-status" role="status">{searchState}</div>}
            {form.latitude!==null&&<div className={form.precision==="precise"?"location-ok":"location-warning"} role="status">
              <strong>{form.precision==="precise"?"✓ Dirección seleccionada":"⚠ Ubicación aproximada"}</strong>
              <span>{form.latitude.toFixed(5)}, {form.longitude.toFixed(5)}</span>
              {form.precision!=="precise"&&<label className="location-confirm"><input type="checkbox" checked={confirmed} onChange={e=>setConfirmed(e.target.checked)}/>Confirmo que el punto es válido para la entrega ficticia</label>}
            </div>}
            <button type="submit" disabled={!user||busy||form.latitude===null||(form.precision!=="precise"&&!confirmed)}>Guardar pedido</button>
          </form>
          <div className="panelhead"><h3>Pedidos en Firestore</h3><span className="count">{selected.length} seleccionados</span></div>
          <div className="orders">{orders.length?orders.map(o=><label className="order" key={o.id}><input type="checkbox" checked={o.checked} disabled={busy||o.status!=="PENDING"} onChange={e=>{setOrders(old=>old.map(x=>x.id===o.id?{...x,checked:e.target.checked}:x));setPreview(null);pendingSaveKey.current=null}}/><span><strong>{o.address_label}</strong><small>{o.status} · {o.id.slice(0,8)}</small></span></label>):<p className="empty">No hay pedidos cargados. Pulsa Actualizar.</p>}</div>
        </section>
        <section className="panel">
          <div className="panelhead"><h2>02 · Optimizar ruta</h2><span className="count">1 vehículo · máx. 10 paradas</span></div>
          <div className="duo"><label>Depósito · latitud<input type="number" step="any" value={depot.latitude} onChange={e=>{setDepot({...depot,latitude:e.target.value});setPreview(null);pendingSaveKey.current=null}}/></label><label>Longitud<input type="number" step="any" value={depot.longitude} onChange={e=>{setDepot({...depot,longitude:e.target.value});setPreview(null);pendingSaveKey.current=null}}/></label></div>
          <button className="accent" disabled={!user||busy||selected.length<1||selected.length>10} onClick={optimize}>{busy?"Procesando…":"Optimizar con OR-Tools"}</button>
          {preview&&<button disabled={!user||busy} onClick={saveOptimized}>Guardar ruta optimizada</button>}
          <p className="fineprint">Al guardar, el servidor vuelve a calcular y valida los pedidos; las métricas guardadas pueden diferir de la previsualización.</p>
          <p className="fineprint">Matrices obtenidas desde openrouteservice en el backend; requieren una clave configurada de forma segura en GCP.</p>
        </section>
        <section className="panel">
          <div className="panelhead"><h2>04 · Rutas guardadas</h2><button className="outline" disabled={!user||busy} onClick={refreshSaved}>Actualizar rutas</button></div>
          <p>Rutas PLANNED guardadas en Firestore. No están asignadas a un conductor.</p>
          {savedRoutes.length? <div className="orders">{savedRoutes.map(r=>
            <button className="outline" style={{textAlign:"left",width:"100%",marginBottom:8}} key={r.id}
              onClick={()=>setSavedRoute(r)}>
              {r.id.slice(0,8)} · {r.order_ids.length} entregas · {mins(r.optimized_seconds)} · {km(r.optimized_meters)}
            </button>
          )}</div> : <p className="empty">No se han consultado rutas. Pulsa Actualizar rutas.</p>}
        </section>
      </aside>
      <article>
        <section className="panel mapSection"><div className="panelhead"><div><h2>Mapa de operaciones</h2><p>OpenStreetMap · puntos seleccionados · recorridos</p></div><span className="count">Lima, Perú</span></div><MapPanel orders={orders} depot={depot} preview={preview} chosen={form.latitude===null?null:{...form,label:form.address_label}}/></section>
        <section className="panel results"><div className="panelhead"><h2>03 · Comparación</h2><span className="count">{preview?"ESTIMADO":"PENDIENTE DE CÁLCULO"}</span></div>
          {preview?<><div className="metrics">
            <div className="metric"><small>Orden original</small><strong>{mins(preview.baseline_seconds)}</strong><span>{km(preview.baseline_meters)}</span></div>
            <div className="metric chosen"><small>OR-Tools</small><strong>{mins(preview.optimized_seconds)}</strong><span>{km(preview.optimized_meters)}</span></div>
            <div className="metric"><small>Mejora estimada</small><strong>{preview.improvement_pct.toFixed(2)}%</strong><span>Sobre la misma matriz</span></div>
          </div><div className="sequence"><b>Secuencia calculada:</b> Depósito → {preview.ordered_order_ids.map(id=>orders.find(o=>o.id===id)?.address_label||id).join(" → ")} → Depósito</div><p className="fineprint">Fuente: {preview.matrix_provider} · Huella matriz: {preview.matrix_fingerprint.slice(0,12)}… · {preview.warnings.join(". ")}. No hay ahorro real observado.</p></>:<div className="empty">Selecciona pedidos y solicita una optimización para comparar recorridos. No se genera ninguna cifra sin datos de la matriz vial.</div>}
        </section>
        {savedRoute&&<section className="panel results">
          <div className="panelhead"><h2>05 · Ruta persistida</h2><span className="count">{savedRoute.status}</span></div>
          <p><strong>ID:</strong> {savedRoute.id}</p>
          <div className="metrics">
            <div className="metric"><small>Orden original</small><strong>{mins(savedRoute.baseline_seconds)}</strong><span>{km(savedRoute.baseline_meters)}</span></div>
            <div className="metric chosen"><small>Ruta guardada</small><strong>{mins(savedRoute.optimized_seconds)}</strong><span>{km(savedRoute.optimized_meters)}</span></div>
            <div className="metric"><small>Mejora estimada</small><strong>{savedRoute.improvement_pct.toFixed(2)}%</strong><span>openrouteservice</span></div>
          </div>
          <div className="sequence"><b>Secuencia persistida:</b> {savedRoute.ordered_order_ids.join(" → ")}</div>
          <p className="fineprint">Origen: {savedRoute.data_origin}. Esta ruta aún no está asignada a un conductor.</p>
        </section>}
      </article>
    </main><footer>SmartRoute AI · MVP académico · La previsualización no reserva pedidos; al guardar se crea una ruta PLANNED, todavía sin conductor asignado.</footer>
  </div>;
}
createRoot(document.getElementById("root")).render(<App/>);
