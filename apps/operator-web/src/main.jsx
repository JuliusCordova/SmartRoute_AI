import React, {useEffect, useRef, useState} from "react";
import {createRoot} from "react-dom/client";
import {initializeApp} from "firebase/app";
import {getAuth, GoogleAuthProvider, signInWithPopup, onAuthStateChanged, signOut} from "firebase/auth";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./style.css";
import {ORDER_STATES,ROUTE_STATES,stateLabel,filterOrders,filterRoutes,summarizeOperations,fetchPaged,projectRouteIndicators} from "./operations.js";
import {distributionCenterReady,distributionCenterPayload} from "./distributionCenter.js";

const cfg = window.__SMARTROUTE_CONFIG__ || {};
const configured = Boolean(cfg.firebase?.apiKey && cfg.firebase?.appId && cfg.gatewayUrl);
const auth = configured ? getAuth(initializeApp(cfg.firebase)) : null;
const GATEWAY = (cfg.gatewayUrl || "").replace(/\/$/, "");
const CUSTOMER_TRACKING_URL = (cfg.customerTrackingUrl || "").replace(/\/$/, "");
const LIMA = [-12.095, -77.035];
const inside = (lat,lng) => lat>=-12.30&&lat<=-11.80&&lng>=-77.20&&lng<=-76.80;
const mins = v=>Math.round(v/60).toLocaleString("es-PE")+" min";
const km = v=>(v/1000).toLocaleString("es-PE",{maximumFractionDigits:2})+" km";
const starting = {address_label:"",latitude:null,longitude:null,precision:null};
const initialCenter={label:"Ubicación inicial del centro (preconfigurada)",latitude:-12.095,longitude:-77.035,precision:"legacy"};

async function api(path, method, token, data){
  const resp=await fetch(GATEWAY+path,{method,headers:{"Authorization":"Bearer "+token, ...(data?{"Content-Type":"application/json"}:{})},body:data?JSON.stringify(data):undefined,cache:"no-store"});
  const body=await resp.json().catch(()=>({}));
  if(!resp.ok) throw new Error(typeof body.detail==="string"?body.detail:"Error HTTP "+resp.status);
  return body;
}

function MapPanel({orders,depot,preview,chosen,savedRoute,centerLabel,gps}){
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
    if(savedRoute){
      const d=[savedRoute.depot.latitude,savedRoute.depot.longitude];
      const path=[d];
      L.circleMarker(d,{radius:10,color:"#102739",fillColor:"#f0b43d",fillOpacity:1})
        .bindPopup("Centro de distribución de la ruta guardada").addTo(group);
      (savedRoute.stops||[]).forEach(stop=>{
        const position=[stop.geo.latitude,stop.geo.longitude];
        path.push(position);
        L.circleMarker(position,{radius:9,color:"#143d4b",fillColor:"#31a8b4",fillOpacity:1})
          .bindPopup(stop.sequence+". "+stop.address_label).addTo(group);
      });
      path.push(d);
      if(gps&&gps.route_id===savedRoute.id){
        L.circleMarker([gps.latitude,gps.longitude],{
          radius:10,color:gps.status==="STALE"?"#9c6c21":"#216bda",
          fillColor:gps.status==="STALE"?"#ffcc74":"#63b6ff",fillOpacity:.9,weight:3
        }).bindPopup("GPS "+gps.status+" · precisión "+Math.round(gps.accuracy_m)+" m").addTo(group);
      }
      if(savedRoute.route_geometry?.length){
        L.polyline(savedRoute.route_geometry.map(([lng,lat])=>[lat,lng]),
          {color:"#e5a219",weight:5,opacity:.9}).addTo(group);
      }else if(path.length>2){
        L.polyline(path,{color:"#e5a219",weight:4,dashArray:"7 8"}).addTo(group);
      }
      if(path.length>2)map.current.fitBounds(L.latLngBounds(path).pad(.25),{maxZoom:14});
      else map.current.setView(d,13);
      return;
    }
    const selected=orders.filter(o=>o.checked);
    const valid=selected.filter(o=>inside(o.geo.latitude,o.geo.longitude));
    const points=[[Number(depot.latitude),Number(depot.longitude)]];
    if(inside(...points[0]))L.circleMarker(points[0],{radius:9,color:"#102739",fillColor:"#f0b43d",fillOpacity:1}).bindPopup(centerLabel||"Centro de distribución").addTo(group);
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
      // Comparación del prototipo: las dos secuencias sobre el mismo mapa.
      // La base es una referencia esquemática; no se presenta como ruta vial real.
      if(points.length>2){
        L.polyline([...points,points[0]],{
          color:"#64748b",weight:3,dashArray:"7 7",opacity:.9
        }).bindPopup("Secuencia base · conectores esquemáticos").addTo(group);
      }
      if(preview.route_geometry?.length){
        L.polyline(preview.route_geometry.map(([lng,lat])=>[lat,lng]),{
          color:"#e5a219",weight:5,opacity:.9
        }).bindPopup("Secuencia optimizada · geometría vial estimada").addTo(group);
      }else{
        const p=[points[0],...preview.ordered_order_ids.map(id=>byId[id]).filter(Boolean),points[0]];
        if(p.length>2)L.polyline(p,{
          color:"#e5a219",weight:4,dashArray:"2 5"
        }).bindPopup("Secuencia optimizada · conectores esquemáticos").addTo(group);
      }
    } else if(points.length>1) {
      L.polyline([...points,points[0]],{color:"#758c9d",weight:2,dashArray:"5 7"}).addTo(group);
    }
    if(points.length>1) map.current.fitBounds(L.latLngBounds(points).pad(.25),{maxZoom:14});
  },[orders,depot,preview,chosen,savedRoute,centerLabel,gps]);
  return <div className="mapWrap"><div ref={ref} className="map" />
    {preview&&!savedRoute&&<div className="map-comparison-legend" aria-label="Comparación de rutas">
      <span><i className="map-base-line"/>Base · secuencia esquemática</span>
      <span><i className="map-optimized-line"/>Optimizada · {preview.route_geometry?"vial estimada":"esquemática"}</span>
    </div>}
    <span className="mapCaption">{savedRoute ? (savedRoute.geometry_origin==="openrouteservice"?"Ruta guardada · recorrido vial estimado":"Ruta guardada · conectores esquemáticos, NO recorrido vial") : preview ? "Comparación base vs. optimizada · ambas secuencias estimadas" : "Orden original · conectores esquemáticos"}</span>
  </div>;
}


function ExecutiveDashboard({orders,routes,coverage,refresh,busy,user}) {
  const [state,setState]=useState("ALL");
  const scope=filterRoutes(routes,state), k=summarizeOperations(orders,scope);
  const indicators=projectRouteIndicators(scope).slice(0,8);
  const orderStates=["PENDING","ASSIGNED","IN_TRANSIT","DELIVERED","FAILED"];
  const shades=["#ffc75c","#6daefa","#9b88fd","#36d9a8","#ff7d91"];
  const ratio=n=>k.orderCount?((100*n/k.orderCount).toFixed(2)+"%"):"0%";
  return <section className="executive" aria-label="Centro de control ejecutivo">
    <div className="executive-top">
      <div><span className="eyebrow">SMARTROUTE INTELLIGENCE / COMMAND CENTER</span>
        <h1>La operación, <em>en una mirada.</em></h1>
        <p>Centro de control del piloto · Firebase + Firestore · Indicadores calculados únicamente desde datos consultados.</p></div>
      <div className="executive-actions"><span className="signal"><span className="signal-dot"/>{user?"SESIÓN AUTENTICADA":"SIN SESIÓN"}</span>
        <button disabled={!user||busy} onClick={refresh}>{busy?"Actualizando…":"↻ Actualizar tablero"}</button></div>
    </div>
    <div className="executive-kpis">
      <div className="executive-kpi"><span>PEDIDOS</span><strong>{k.orderCount}</strong><small>Registros recuperados</small></div>
      <div className="executive-kpi"><span>RUTAS</span><strong>{k.routeCount}</strong><small>{state==="ALL"?"Todas las consultadas":stateLabel[state]}</small></div>
      <div className="executive-kpi"><span>EFECTIVIDAD</span><strong>{k.deliveryRate===null?"—":k.deliveryRate.toFixed(1)+"%"}</strong><small>Entregadas / resueltas</small></div>
      <div className="executive-kpi accent-kpi"><span>MEJORA ESTIMADA</span><strong>{k.estimatedImprovement===null?"—":k.estimatedImprovement.toFixed(1)+"%"}</strong><small>{k.estimatedRoutes} rutas · tiempos de matriz vial</small></div>
    </div>
    <div className="executive-panels">
      <div className="exec-chart">
        <div className="exec-chart-title"><div><b>Pipeline de pedidos</b><span>Distribución por estado</span></div><span className="live-tag">FIRESTORE</span></div>
        <div className="stacked-meter" role="img" aria-label="Distribución de pedidos por estado">
          {orderStates.map((st,i)=><span key={st} style={{width:ratio(k.ordersByState[st]),background:shades[i]}}/>)}
        </div>
        <div className="exec-bars">{orderStates.map((st,i)=><div className="exec-bar-line" key={st}>
          <div className="exec-bar-name"><i style={{background:shades[i]}}/>{stateLabel[st]}</div>
          <div className="exec-track"><div style={{width:ratio(k.ordersByState[st]),background:shades[i]}}/></div><b>{k.ordersByState[st]}</b>
        </div>)}</div>
      </div>
      <div className="exec-chart">
        <div className="exec-chart-title"><div><b>Estado de rutas</b><span>Filtro ejecutivo interactivo</span></div><span className="live-tag">OPERACIÓN</span></div>
        <div className="route-chips" role="group" aria-label="Filtrar rutas del tablero">
          {ROUTE_STATES.map(st=><button key={st} className={state===st?"chip selected":"chip"} aria-pressed={state===st} onClick={()=>setState(st)}>{stateLabel[st]}</button>)}
        </div>
        <div className="route-mini-grid">{["PLANNED","ACTIVE","COMPLETED","CANCELLED"].map(st=><div className="route-mini" key={st}>
          <span>{stateLabel[st]}</span><strong>{k.routesByState[st]}</strong></div>)}</div>
        <div className="exec-note">{k.resolved} pedidos resueltos · {k.delivered} entregados · {k.failed} fallidos.</div>
      </div>
    </div>
    <section className="operator-indicators" aria-label="US-011 Indicadores de rutas y evidencia">
      <div className="operator-indicators-head">
        <div><span className="eyebrow">US-011 · MÉTRICAS VERIFICABLES</span>
          <h2>Rendimiento de las rutas</h2>
          <p>Comparación de tiempo y distancia para el mismo conjunto de paradas. Son <strong>estimaciones de matriz vial</strong>, no desplazamientos observados.</p></div>
        <span className="operator-scope">{indicators.length} de {scope.length} rutas visibles</span>
      </div>
      {indicators.length ? <div className="operator-table-scroll">
        <table className="operator-metrics-table">
          <thead><tr><th scope="col">Ruta / estado</th><th scope="col">Paradas</th><th scope="col">Tiempo base → optimizado</th><th scope="col">Mejora tiempo</th><th scope="col">Distancia base → optimizada</th><th scope="col">Mejora distancia</th><th scope="col">Origen</th></tr></thead>
          <tbody>{indicators.map(item=><tr key={item.id}>
            <td><strong title={item.id}>{item.id.slice(0,8)}…</strong><small>{stateLabel[item.status]||item.status}</small></td>
            <td>{item.stopCount}</td>
            <td>{item.baselineSeconds===null?"Sin dato":`${mins(item.baselineSeconds)} → ${mins(item.optimizedSeconds)}`}<small>{item.baselineSeconds===null?"—":`${item.baselineSeconds} → ${item.optimizedSeconds} s exactos`}</small></td>
            <td className="operator-highlight">{item.timeImprovement===null?"—":item.timeImprovement.toFixed(2)+" %"}</td>
            <td>{item.baselineMeters===null?"Sin dato":`${km(item.baselineMeters)} → ${km(item.optimizedMeters)}`}</td>
            <td className="operator-highlight">{item.distanceImprovement===null?"—":item.distanceImprovement.toFixed(2)+" %"}</td>
            <td><span className="estimate-label">ESTIMADO</span></td>
          </tr>)}</tbody>
        </table>
      </div> : <p className="operator-no-data">Aún no hay rutas consultadas para este filtro. Actualiza el tablero para ver las métricas disponibles.</p>}
      <p className="operator-indicators-foot">No se dispone aquí de tiempos observados ni de medición de puntualidad. No se calcula semáforo, no se exportan resultados y los porcentajes no prueban ahorro real. {coverage.routesTruncated?"La consulta tiene páginas pendientes: la cobertura es parcial.":""}</p>
    </section>
    <div className="executive-footer"><span>{coverage.ordersTruncated||coverage.routesTruncated?"ATENCIÓN: datos parciales por límite de páginas":"Vista calculada sobre todas las páginas recuperadas"}</span>
      <span>Sin GPS observado · sin puntualidad medida · ahorros estimados</span></div>
  </section>;
}

function App(){
  const [user,setUser]=useState(null),[busy,setBusy]=useState(false),[error,setError]=useState(""),[orders,setOrders]=useState([]),[form,setForm]=useState(starting),[depot,setDepot]=useState({latitude:"-12.095",longitude:"-77.035"}),[preview,setPreview]=useState(null),[status,setStatus]=useState("Inicia sesión para consultar pedidos.");
  const [suggestions,setSuggestions]=useState([]),[searchState,setSearchState]=useState(""),[confirmed,setConfirmed]=useState(false),[searching,setSearching]=useState(false);
  const [savedRoutes,setSavedRoutes]=useState([]),[savedRoute,setSavedRoute]=useState(null);
  const [gpsPosition,setGpsPosition]=useState(null),[gpsNotice,setGpsNotice]=useState("");
  const [drivers,setDrivers]=useState([]),[selectedDriver,setSelectedDriver]=useState("");
  const [centerName,setCenterName]=useState("Centro de distribución");
  const [centerQuery,setCenterQuery]=useState(initialCenter.label),[centerChoice,setCenterChoice]=useState(initialCenter);
  const [centerSuggestions,setCenterSuggestions]=useState([]),[centerSearchState,setCenterSearchState]=useState(""),[centerSearching,setCenterSearching]=useState(false);
  const [centerConfirmed,setCenterConfirmed]=useState(true);
  const [centers,setCenters]=useState([]),[centerListPartial,setCenterListPartial]=useState(false);
  const [centerCode,setCenterCode]=useState(""),[editingCenter,setEditingCenter]=useState(null);
  const [currentCenterId,setCurrentCenterId]=useState(null),[centerMasterQuery,setCenterMasterQuery]=useState("");
  const [centerMasterNotice,setCenterMasterNotice]=useState("");
  const pendingSaveKey=useRef(null),pendingAssignmentKey=useRef(null);
  const [orderState,setOrderState]=useState("ALL"),[orderSearch,setOrderSearch]=useState("");
  const [routeListState,setRouteListState]=useState("ALL");
  const [trackingLink,setTrackingLink]=useState(null);
  const [trackingNotice,setTrackingNotice]=useState("");
  const [coverage,setCoverage]=useState({ordersTruncated:false,routesTruncated:false});
  useEffect(()=>auth?onAuthStateChanged(auth,u=>{setUser(u);setPreview(null);setOrders([]);setSavedRoutes([]);setSavedRoute(null);setDrivers([]);setSelectedDriver("");setCenters([]);setEditingCenter(null);setCurrentCenterId(null);setTrackingLink(null);setTrackingNotice("");pendingSaveKey.current=null;pendingAssignmentKey.current=null;setStatus(u?"Sesión iniciada. Consulta tus pedidos.":"Inicia sesión para consultar pedidos.");},e=>setError(e.code)):undefined,[]);
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
  useEffect(()=>{
    if(!user||centerChoice||centerQuery.trim().length<3){
      setCenterSuggestions([]);setCenterSearchState("");setCenterSearching(false);return;
    }
    let active=true;setCenterSearching(true);setCenterSearchState("Buscando direcciones…");
    const timer=setTimeout(async()=>{
      try{
        const data=await api("/api/v1/geocoding/autocomplete?q="+encodeURIComponent(centerQuery.trim()),"GET",await user.getIdToken());
        if(active){setCenterSuggestions(data.items||[]);setCenterSearchState(data.notice||(data.items?.length?"Selecciona una ubicación.":"Sin coincidencias."));}
      }catch(e){if(active){setCenterSuggestions([]);setCenterSearchState("Error: "+e.message);}}
      finally{if(active)setCenterSearching(false);}
    },500);
    return ()=>{active=false;clearTimeout(timer);};
  },[user,centerQuery,centerChoice]);
  function selectCenter(c){
    if(!inside(c.latitude,c.longitude)){setError("Centro de distribución fuera del área del piloto");return;}
    setCenterChoice({label:c.label,latitude:c.latitude,longitude:c.longitude,precision:c.precision});
    setCurrentCenterId(null);
    setCenterQuery(c.label);setDepot({latitude:String(c.latitude),longitude:String(c.longitude)});
    setCenterConfirmed(c.precision==="precise");setCenterSuggestions([]);setCenterSearchState("");
    setPreview(null);setSavedRoute(null);pendingSaveKey.current=null;
    setStatus(c.precision==="precise"?"Centro de distribución seleccionado.":"Confirma la ubicación aproximada antes de optimizar.");
  }
  function chooseSavedCenter(center){
    if(!center.active)return;
    setCurrentCenterId(center.id);setEditingCenter(null);
    setCenterCode(center.code);setCenterName(center.name);setCenterQuery(center.address_label);
    setCenterChoice({label:center.address_label,latitude:center.geo.latitude,longitude:center.geo.longitude,precision:center.location_precision});
    setDepot({latitude:String(center.geo.latitude),longitude:String(center.geo.longitude)});
    setCenterConfirmed(true);setCenterSuggestions([]);setCenterSearchState("");
    setPreview(null);setSavedRoute(null);pendingSaveKey.current=null;
    setStatus("Sede "+center.code+" seleccionada como origen de futuras rutas.");
  }
  function beginCenterEdit(center){
    setEditingCenter(center);setCurrentCenterId(null);
    setCenterCode(center.code);setCenterName(center.name);
    setCenterQuery(center.address_label);
    setCenterChoice({label:center.address_label,latitude:center.geo.latitude,longitude:center.geo.longitude,precision:center.location_precision});
    setDepot({latitude:String(center.geo.latitude),longitude:String(center.geo.longitude)});
    setCenterConfirmed(true);setCenterSuggestions([]);setCenterSearchState("");
    setPreview(null);setSavedRoute(null);pendingSaveKey.current=null;
    setStatus("Editando sede "+center.code+". Guarda los cambios o cancela.");
  }
  function resetCenterEditor(){
    setEditingCenter(null);setCenterCode("");setCurrentCenterId(null);
    setCenterName("Centro de distribución");setCenterQuery("");setCenterChoice(null);
    setCenterConfirmed(false);setCenterSuggestions([]);setCenterSearchState("");
    setPreview(null);setSavedRoute(null);pendingSaveKey.current=null;
  }
  async function fetchCenters(tkn){
    return fetchPaged((limit,cursor)=>api("/api/v1/distribution-centers?limit="+limit+
      (cursor?"&cursor="+encodeURIComponent(cursor):""),"GET",tkn),{limit:50,maxPages:10});
  }
  useEffect(()=>{
    if(!user)return;
    let live=true;
    user.getIdToken().then(fetchCenters).then(result=>{
      if(live){setCenters(result.items);setCenterListPartial(result.truncated);}
    }).catch(e=>{if(live)setCenterMasterNotice("No se pudo cargar catálogo: "+e.message);});
    return ()=>{live=false;};
  },[user]);
  const refreshCenters=()=>run(async()=>{
    const result=await fetchCenters(await token());
    setCenters(result.items);setCenterListPartial(result.truncated);
    setCenterMasterNotice(result.items.length+" sedes recuperadas."+(result.truncated?" Lista parcial.":""));
  });
  const persistCenter=()=>run(async()=>{
    if(!distributionCenterReady(centerChoice,centerConfirmed,centerName,inside))
      throw new Error("Selecciona y confirma una dirección válida para guardar la sede.");
    if(!/^[A-Za-z0-9][A-Za-z0-9_-]{1,23}$/.test(centerCode.trim()))
      throw new Error("Código: de 2 a 24 letras, dígitos, guiones o guion bajo.");
    const payload={
      code:centerCode.trim().toUpperCase(),name:centerName.trim(),address_label:centerChoice.label,
      geo:distributionCenterPayload(centerChoice),location_precision:centerChoice.precision==="approximate"?"approximate":"precise",
      approximate_confirmed:centerConfirmed,
    };
    const wasEditing=Boolean(editingCenter);
    const tkn=await token();
    const saved=wasEditing
      ?await api("/api/v1/distribution-centers/"+encodeURIComponent(editingCenter.id),"PUT",tkn,{...payload,expected_version:editingCenter.version})
      :await api("/api/v1/distribution-centers","POST",tkn,payload);
    const refreshed=await fetchCenters(tkn);
    setCenters(refreshed.items);setCenterListPartial(refreshed.truncated);
    chooseSavedCenter(saved);
    setCenterMasterNotice("Sede "+saved.code+(wasEditing?" actualizada.":" creada.")+" Ya se puede elegir para planificar.");
  });
  const deactivateCenter=(center)=>run(async()=>{
    if(!window.confirm("¿Desactivar la sede "+center.name+"? Sus rutas guardadas no cambiarán."))return;
    const tkn=await token();
    await api("/api/v1/distribution-centers/"+encodeURIComponent(center.id),"DELETE",tkn,{expected_version:center.version});
    const fresh=await fetchCenters(tkn);setCenters(fresh.items);setCenterListPartial(fresh.truncated);
    if(currentCenterId===center.id||editingCenter?.id===center.id)resetCenterEditor();
    setCenterMasterNotice("Sede desactivada. No puede elegirse para nuevas rutas.");
  });
  function selectAddress(s){
    setForm({address_label:s.label,latitude:s.latitude,longitude:s.longitude,precision:s.precision});
    setSuggestions([]);setSearchState("");setConfirmed(s.precision==="precise");setPreview(null);pendingSaveKey.current=null;
  }
  async function run(fn){setBusy(true);setError("");try{await fn()}catch(e){setError(e.message)}finally{setBusy(false)}}
  async function token(){if(!auth?.currentUser) throw new Error("Inicia sesión primero");return auth.currentUser.getIdToken();}
  async function getAllOrders(tkn) {
    return fetchPaged((limit,cursor)=>api("/api/v1/orders?limit="+limit+(cursor?"&cursor="+encodeURIComponent(cursor):""),"GET",tkn),{limit:50,maxPages:10});
  }
  async function getAllRoutes(tkn) {
    return fetchPaged((limit,cursor)=>api("/api/v1/optimized-routes?limit="+limit+(cursor?"&cursor="+encodeURIComponent(cursor):""),"GET",tkn),{limit:20,maxPages:10});
  }
  const refreshExecutive=()=>run(async()=>{
    const tkn=await token();
    const [o,r]=await Promise.all([getAllOrders(tkn),getAllRoutes(tkn)]);
    setOrders(o.items.map(x=>({...x,checked:false})));setSavedRoutes(r.items);
    setCoverage({ordersTruncated:o.truncated,routesTruncated:r.truncated});
    setPreview(null);pendingSaveKey.current=null;
    setStatus("Centro de control actualizado: "+o.items.length+" pedidos y "+r.items.length+" rutas."+(o.truncated||r.truncated?" Consulta parcial.":""));
  });
  useEffect(()=>{
    if(!user)return;
    let live=true;
    (async()=>{
      try{
        const tkn=await user.getIdToken();
        const [o,r]=await Promise.all([getAllOrders(tkn),getAllRoutes(tkn)]);
        if(!live)return;
        setOrders(o.items.map(x=>({...x,checked:false})));
        setSavedRoutes(r.items);
        setCoverage({ordersTruncated:o.truncated,routesTruncated:r.truncated});
        setStatus("Centro de control conectado: "+o.items.length+" pedidos y "+r.items.length+" rutas recuperadas."+(o.truncated||r.truncated?" Vista parcial.":""));
      }catch(e){if(live)setError("No se pudo cargar el tablero: "+e.message);}
    })();
    return ()=>{live=false};
  },[user]);
  const load=()=>run(async()=>{const x=await getAllOrders(await token());setOrders(x.items.map(o=>({...o,checked:false})));setCoverage(old=>({...old,ordersTruncated:x.truncated}));setPreview(null);pendingSaveKey.current=null;setStatus(x.items.length+" pedidos recuperados de Firestore."+(x.truncated?" Consulta parcial.":""));});
  const create=()=>run(async()=>{
    if(form.latitude===null||form.longitude===null) throw new Error("Selecciona una dirección de las sugerencias antes de guardar");
    const lat=Number(form.latitude),lng=Number(form.longitude);
    if(!inside(lat,lng))throw new Error("ALERTA: destino fuera de la zona del piloto en Lima");
    if(form.precision!=="precise"&&!confirmed)throw new Error("ALERTA: ubicación aproximada; confirma el punto del mapa antes de guardar");
    await api("/api/v1/orders","POST",await token(),{address_label:form.address_label.trim(),geo:{latitude:lat,longitude:lng}});
    setForm(starting);setConfirmed(false);setSuggestions([]);
    const x=await getAllOrders(await token());
    setOrders(x.items.map(o=>({...o,checked:false})));setCoverage(old=>({...old,ordersTruncated:x.truncated}));setPreview(null);pendingSaveKey.current=null;setStatus("Pedido creado y consultado desde Firestore.");
  });
  const optimize=()=>run(async()=>{
    const picked=orders.filter(o=>o.checked);
    if(!picked.length||picked.length>10)throw new Error("Selecciona entre 1 y 10 pedidos");
    if(!currentCenterId||!distributionCenterReady(centerChoice,centerConfirmed,centerName,inside))throw new Error("Elige una sede activa del catálogo antes de optimizar");
    const p=await api("/api/v1/optimization/preview","POST",await token(),{
      depot:{id:"depot",...distributionCenterPayload(centerChoice)},
      stops:picked.map(o=>({id:o.id,latitude:o.geo.latitude,longitude:o.geo.longitude}))
    });
    setPreview(p);setSavedRoute(null);pendingSaveKey.current=crypto.randomUUID();setStatus("Secuencia optimizada con matriz vial. Resultado estimado, no observado.");
  });
    const refreshSaved=()=>run(async()=>{
    const x=await getAllRoutes(await token());
    setSavedRoutes(x.items);setCoverage(old=>({...old,routesTruncated:x.truncated}));
    setStatus(x.items.length+" rutas optimizadas recuperadas de Firestore."+(x.truncated?" Consulta parcial.":""));
  });
  async function showSavedRoute(id){
    const detail=await api("/api/v1/optimized-routes/"+encodeURIComponent(id),"GET",await token());
    setSavedRoute(detail);
    setGpsPosition(null);setGpsNotice("");
    setSelectedDriver("");
    pendingAssignmentKey.current=null;
    setPreview(null);
    setStatus("Ruta "+detail.id.slice(0,8)+" recuperada con "+detail.stops.length+" paradas en secuencia.");
  }
  const loadGps=()=>run(async()=>{
    if(!savedRoute||savedRoute.status!=="ACTIVE")throw new Error("GPS disponible solo en ruta ACTIVE");
    try {
      const gps=await api("/api/v1/routes/"+encodeURIComponent(savedRoute.id)+"/location","GET",await token());
      setGpsPosition(gps);
      setGpsNotice(gps.status==="STALE"?"Última posición caducada (>2 min).":"Última posición registrada (observada).");
    }catch(e){
      setGpsPosition(null);
      if(e.message.includes("404")){setGpsNotice("Aún no existe posición GPS para esta ruta.");return;}
      throw e;
    }
  });
  const loadDrivers=()=>run(async()=>{
    const candidates=await api("/api/v1/drivers?available=true&limit=20","GET",await token());
    setDrivers(candidates.items||[]);
    setSelectedDriver("");
    pendingAssignmentKey.current=null;
    setStatus((candidates.items||[]).length+" conductores disponibles encontrados.");
  });
  const assignDriver=()=>run(async()=>{
    if(!savedRoute||savedRoute.status!=="PLANNED"||savedRoute.driver_id)
      throw new Error("Selecciona una ruta PLANNED sin conductor");
    if(!selectedDriver||!drivers.some(d=>d.uid===selectedDriver))
      throw new Error("Selecciona un conductor disponible");
    if(!pendingAssignmentKey.current) pendingAssignmentKey.current=crypto.randomUUID();
    const id=savedRoute.id;
    const assigned=await api("/api/v1/optimized-routes/"+encodeURIComponent(id)+"/assign-driver",
      "POST",await token(),{
        driver_id:selectedDriver,
        expected_version:savedRoute.version,
        idempotency_key:pendingAssignmentKey.current,
      });
    const tkn=await token();
    const [detail,routes]=await Promise.all([
      api("/api/v1/optimized-routes/"+encodeURIComponent(id),"GET",tkn),
      getAllRoutes(tkn),
    ]);
    setSavedRoute(detail);
    setSavedRoutes(routes.items);setCoverage(old=>({...old,routesTruncated:routes.truncated}));
    setDrivers(old=>old.filter(d=>d.uid!==assigned.driver_id));
    setSelectedDriver("");
    pendingAssignmentKey.current=null;
    setStatus("Conductor asignado a la ruta "+id.slice(0,8)+". Sigue PLANNED hasta iniciar recorrido.");
  });
  const saveOptimized=()=>run(async()=>{
    if(!preview || !pendingSaveKey.current) throw new Error("Primero optimiza los pedidos");
    const picked=orders.filter(o=>o.checked);
    if(!picked.length || picked.length>10) throw new Error("Selecciona de 1 a 10 pedidos");
    if(!currentCenterId||!distributionCenterReady(centerChoice,centerConfirmed,centerName,inside)) throw new Error("Elige una sede activa del catálogo antes de guardar");
    const saved=await api("/api/v1/optimized-routes","POST",await token(),{
      depot:distributionCenterPayload(centerChoice),
      distribution_center_id:currentCenterId,
      order_ids:picked.map(o=>o.id),
      idempotency_key:pendingSaveKey.current,
    });
    setSavedRoute(saved);setPreview(null);pendingSaveKey.current=null;
    const tkn=await token();
    const [ordersResult,routesResult]=await Promise.all([
      getAllOrders(tkn),
      getAllRoutes(tkn),
    ]);
    setOrders(ordersResult.items.map(o=>({...o,checked:false})));
    setSavedRoutes(routesResult.items);setCoverage({ordersTruncated:ordersResult.truncated,routesTruncated:routesResult.truncated});
    setStatus("Ruta "+saved.id.slice(0,8)+" guardada en Firestore como PLANNED. Pedidos reservados.");
    try { await showSavedRoute(saved.id); }
    catch { setStatus("Ruta guardada; vuelve a seleccionarla en Rutas guardadas para ver el mapa."); }
  });
  const issueTrackingLink=order=>run(async()=>{
    // Operator Firebase identity is required at the gateway and API.
    setTrackingLink(null);setTrackingNotice("");
    if(!CUSTOMER_TRACKING_URL)throw new Error("La URL web del cliente no está configurada");
    const result=await api("/api/v1/orders/"+encodeURIComponent(order.id)+"/tracking-link","POST",await token());
    if(typeof result.token!=="string" || !/^[A-Za-z0-9_-]{32,256}$/.test(result.token))
      throw new Error("El servidor no devolvió un enlace válido");
    setTrackingLink({orderId:order.id, token:result.token, expiresAt:result.expires_at,
      url:CUSTOMER_TRACKING_URL+"/#/t/"+result.token});
    setTrackingNotice("Enlace generado solo para este pedido. Compártelo únicamente con su destinatario.");
  });
  const revokeTrackingLink=()=>run(async()=>{
    if(!trackingLink)return;
    await api("/api/v1/orders/tracking-link/revoke","POST",await token(),{token:trackingLink.token});
    setTrackingLink(null);setTrackingNotice("Enlace revocado. Ya no permite consultar el pedido.");
  });
  const copyTrackingLink=async()=>{
    if(!trackingLink)return;
    try{await navigator.clipboard.writeText(trackingLink.url);setTrackingNotice("Enlace copiado. Compártelo únicamente con el destinatario.");}
    catch{setTrackingNotice("Copia el enlace desde el campo de texto.");}
  };
  const selected=orders.filter(o=>o.checked);
  const visibleOrders=filterOrders(orders,orderState,orderSearch);
  const visibleRoutes=filterRoutes(savedRoutes,routeListState);
  return <div className="app">
    <header><div className="brand"><span className="brandmark">↝</span><div><b>SmartRoute <em>AI</em></b><small>CENTRO DE OPERACIONES · PILOTO</small></div></div><div className="identity">{user?<><span>{user.email}</span><button className="outline" onClick={()=>run(()=>signOut(auth))}>Salir</button></>:<button onClick={()=>run(()=>signInWithPopup(auth,new GoogleAuthProvider()))} disabled={!configured||busy}>Entrar con Google</button>}</div></header>
    <div className="subhead"><span>UPN Capstone · Lima Metropolitana</span><span className="tag">DATOS DE PEDIDOS SINTÉTICOS · MATRIZ ESTIMADA</span></div>
    {!configured&&<div className="notice error">El frontend aún no tiene configuración Firebase/gateway. Revisa las variables del servicio Cloud Run.</div>}
    {error&&<div className="notice error" role="alert">{error}</div>}
    <div className="notice" role="status">{status}</div>
    <ExecutiveDashboard orders={orders} routes={savedRoutes} coverage={coverage} refresh={refreshExecutive} busy={busy} user={user}/>
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
          <div className="filter-grid"><label>Estado del pedido<select aria-label="Filtrar pedidos por estado" value={orderState} onChange={e=>setOrderState(e.target.value)}>
            {ORDER_STATES.map(st=><option key={st} value={st}>{stateLabel[st]}</option>)}
          </select></label><label>Buscar dirección o ID<input type="search" aria-label="Buscar pedidos" placeholder="Buscar pedido…" value={orderSearch} onChange={e=>setOrderSearch(e.target.value)}/></label></div>
          <p className="filter-result" role="status">{visibleOrders.length} de {orders.length} pedidos visibles{coverage.ordersTruncated?" · Consulta parcial":""}</p>
          <div className="orders">{visibleOrders.length?visibleOrders.map(o=><div className="order" key={o.id}>
            <label className="order-identity"><input type="checkbox" checked={o.checked} disabled={busy||o.status!=="PENDING"} onChange={e=>{setOrders(old=>old.map(x=>x.id===o.id?{...x,checked:e.target.checked}:x));setPreview(null);pendingSaveKey.current=null}}/><span><strong>{o.address_label}</strong><small>{stateLabel[o.status]||o.status} · {o.id.slice(0,8)}</small></span></label>
            <button type="button" className="outline tracking-action" disabled={!user||busy||!CUSTOMER_TRACKING_URL} onClick={()=>issueTrackingLink(o)} title="Solo pedidos sintéticos; requiere habilitación de US-016 en API y gateway">Crear enlace</button>
          </div>): <p className="empty">{orders.length?"No hay pedidos con este filtro.":"No hay pedidos cargados. Pulsa Actualizar."}</p>}</div>
          {trackingNotice&&<p className="tracking-notice" role="status">{trackingNotice}</p>}
          {trackingLink&&<div className="tracking-share" aria-label="Enlace temporal de seguimiento">
            <strong>Seguimiento · pedido {trackingLink.orderId.slice(0,8)}</strong>
            <p>Enlace privado temporal. Caduca: {trackingLink.expiresAt?new Date(trackingLink.expiresAt).toLocaleString("es-PE"):"según el servidor"}.</p>
            <input type="text" aria-label="Enlace de seguimiento del destinatario" readOnly value={trackingLink.url} onFocus={e=>e.target.select()}/>
            <div className="tracking-share-actions">
              <button type="button" disabled={busy} onClick={copyTrackingLink}>Copiar enlace</button>
              <button type="button" className="outline" disabled={busy} onClick={revokeTrackingLink}>Revocar enlace</button>
            </div>
            <small>El enlace permite consultar el estado del pedido sin iniciar sesión. No lo publiques.</small>
          </div>}
        </section>
        <section className="panel">
          <div className="panelhead"><h2>02 · Centro de distribución</h2><span className="count">ORIGEN Y RETORNO · 1 VEHÍCULO</span></div>
          <div className="center-master">
            <div className="panelhead"><h3>Catálogo de sedes</h3><button type="button" className="outline" disabled={!user||busy} onClick={refreshCenters}>↻ Actualizar</button></div>
            <label>Buscar sede<input type="search" aria-label="Buscar sedes registradas" value={centerMasterQuery} onChange={e=>setCenterMasterQuery(e.target.value)} placeholder="Código, nombre o dirección"/></label>
            <p className="fineprint" role="status">{centerMasterNotice}{centerListPartial?" · Vista parcial por paginación":""}</p>
            <div className="center-master-list">
              {centers.filter(c=>[c.name,c.code,c.address_label].some(v=>String(v).toLocaleLowerCase("es-PE").includes(centerMasterQuery.trim().toLocaleLowerCase("es-PE")))).map(c=><div className="center-master-item" key={c.id}>
                <div className="center-master-description"><strong>{c.name}</strong><small>{c.code} · {c.active?"ACTIVA":"INACTIVA"} · {c.address_label}</small></div>
                <div className="center-master-actions">
                  <button type="button" disabled={busy||!c.active} onClick={()=>chooseSavedCenter(c)}>Elegir</button>
                  <button type="button" className="outline" disabled={busy||!c.active} onClick={()=>beginCenterEdit(c)}>Editar</button>
                  <button type="button" className="outline" disabled={busy||!c.active} onClick={()=>deactivateCenter(c)}>Desactivar</button>
                </div>
              </div>)}
              {!centers.length&&<p className="empty">No hay sedes consultadas. Usa Actualizar o registra una nueva.</p>}
            </div>
            <button type="button" className="outline" disabled={busy} onClick={resetCenterEditor}>+ Nueva sede</button>
          </div>
          <div className="distribution-form">
            <div className="panelhead"><h3>{editingCenter?"Editar sede":"Registrar sede"}</h3><span className="count">{currentCenterId?"SEDE ELEGIDA":"CATÁLOGO"}</span></div>
            <label>Código de sede<input type="text" aria-label="Código de sede" maxLength={24} value={centerCode} disabled={Boolean(editingCenter)||busy} onChange={e=>setCenterCode(e.target.value.toUpperCase())} placeholder="Ej. CD-LIMA-01"/></label>
            <label>Nombre del centro<input type="text" aria-label="Nombre del centro de distribución" maxLength={80} value={centerName} onChange={e=>setCenterName(e.target.value)} placeholder="Centro de distribución"/></label>
            <label htmlFor="distribution-search">Buscar dirección del centro</label>
            <input id="distribution-search" type="search" autoComplete="off" minLength={3} maxLength={120}
              value={centerQuery} onChange={e=>{setCenterQuery(e.target.value);setCenterChoice(null);setCurrentCenterId(null);setCenterConfirmed(false);setCenterSuggestions([]);setCenterSearchState("");setPreview(null);setSavedRoute(null);pendingSaveKey.current=null;}}
              placeholder="Ej. Av. Universitaria, Lima" role="combobox" aria-autocomplete="list" aria-expanded={centerSuggestions.length>0} aria-controls="distribution-suggestions"/>
            {centerSearching&&<span className="lookup-status">Buscando…</span>}
            {centerSuggestions.length>0&&<div className="suggestions" id="distribution-suggestions" role="listbox" aria-label="Ubicaciones sugeridas del centro">
              {centerSuggestions.map(c=><button type="button" role="option" aria-selected="false" key={c.id} className="suggestion" onClick={()=>selectCenter(c)}>
                <span>📍 {c.label}</span><small>{c.precision==="precise"?"Ubicación precisa":"Ubicación aproximada · requiere confirmación"}</small></button>)}
            </div>}
            {!centerChoice&&centerSearchState&&!centerSearching&&<p className="lookup-status" role="status">{centerSearchState}</p>}
            {centerChoice&&<div className={centerChoice.precision==="approximate"?"location-warning":"location-ok"} role="status">
              <strong>{centerChoice.precision==="legacy"?"Ubicación inicial no verificada":centerChoice.precision==="precise"?"Centro geolocalizado":"Ubicación aproximada"}</strong>
              <span>{centerChoice.label}</span>
              <span>{Number(depot.latitude).toFixed(5)}, {Number(depot.longitude).toFixed(5)}</span>
              {centerChoice.precision==="approximate"&&<label className="location-confirm"><input type="checkbox" checked={centerConfirmed} onChange={e=>setCenterConfirmed(e.target.checked)}/>Confirmo este punto como origen de ruta</label>}
            </div>}
            <div className="center-editor-actions">
              <button type="button" disabled={!user||busy||Boolean(currentCenterId&&!editingCenter)||!distributionCenterReady(centerChoice,centerConfirmed,centerName,inside)||!centerCode.trim()} onClick={persistCenter}>{editingCenter?"Guardar cambios":"Guardar nueva sede"}</button>
              {editingCenter&&<button type="button" className="outline" disabled={busy} onClick={resetCenterEditor}>Cancelar edición</button>}
              {currentCenterId&&!editingCenter&&<span className="lookup-status">Sede guardada y elegida. Usa Editar para modificarla.</span>}
            </div>
            <p className="fineprint">Las sedes se guardan en Firestore. Sólo las activas se pueden elegir para planificar; las rutas históricas conservan las coordenadas originales.</p>
          </div>
          <div className="panelhead"><h3>Optimizar paradas</h3><span className="count">Máx. 10 paradas</span></div>
          <button className="accent" disabled={!user||busy||selected.length<1||selected.length>10||!currentCenterId||!distributionCenterReady(centerChoice,centerConfirmed,centerName,inside)} onClick={optimize}>{busy?"Procesando…":"Optimizar con OR-Tools"}</button>
          {preview&&<button disabled={!user||busy||!currentCenterId||!distributionCenterReady(centerChoice,centerConfirmed,centerName,inside)} onClick={saveOptimized}>Guardar ruta optimizada</button>}
          <p className="fineprint">Al guardar, el servidor vuelve a calcular y valida los pedidos; las métricas guardadas pueden diferir de la previsualización.</p>
          <p className="fineprint">Matrices obtenidas desde openrouteservice en el backend; requieren una clave configurada de forma segura en GCP.</p>
        </section>
        <section className="panel">
          <div className="panelhead"><h2>04 · Rutas guardadas</h2><button className="outline" disabled={!user||busy} onClick={refreshSaved}>Actualizar rutas</button></div>
          <p>Rutas optimizadas guardadas en Firestore: PLANNED (planificadas), ACTIVE (en recorrido) y COMPLETED (finalizadas).</p>
          <div className="filter-grid"><label>Estado de ruta<select aria-label="Filtrar rutas por estado" value={routeListState} onChange={e=>setRouteListState(e.target.value)}>
            {ROUTE_STATES.map(st=><option key={st} value={st}>{stateLabel[st]}</option>)}
          </select></label></div><p className="filter-result">{visibleRoutes.length} de {savedRoutes.length} rutas visibles{coverage.routesTruncated?" · Consulta parcial":""}</p>
          {visibleRoutes.length? <div className="orders">{visibleRoutes.map(r=>
            <button className="outline" style={{textAlign:"left",width:"100%",marginBottom:8}} key={r.id}
              onClick={()=>run(()=>showSavedRoute(r.id))}>
              {r.id.slice(0,8)} · {r.order_ids.length} entregas · {mins(r.optimized_seconds)} · {km(r.optimized_meters)} · {r.status} · {r.driver_id?"Asignada":"Sin conductor"}
            </button>
          )}</div> : <p className="empty">{savedRoutes.length?"No hay rutas con este filtro.":"No se han consultado rutas. Pulsa Actualizar rutas."}</p>}
        </section>
      </aside>
      <article>
        <section className="panel mapSection"><div className="panelhead"><div><h2>Mapa de operaciones</h2><p>OpenStreetMap · puntos seleccionados · recorridos</p></div><span className="count">Lima, Perú</span></div><MapPanel orders={orders} depot={depot} centerLabel={centerName.trim()||"Centro de distribución"} preview={preview} savedRoute={savedRoute} gps={gpsPosition} chosen={form.latitude===null?null:{...form,label:form.address_label}}/></section>
        <section className="panel results"><div className="panelhead"><h2>03 · Comparación</h2><span className="count">{preview?"ESTIMADO":"PENDIENTE DE CÁLCULO"}</span></div>
          {preview?<><div className="metrics">
            <div className="metric"><small>Orden original</small><strong>{mins(preview.baseline_seconds)}</strong><span>{km(preview.baseline_meters)} · {preview.baseline_seconds} s exactos</span></div>
            <div className="metric chosen"><small>OR-Tools</small><strong>{mins(preview.optimized_seconds)}</strong><span>{km(preview.optimized_meters)} · {preview.optimized_seconds} s exactos</span></div>
            <div className="metric"><small>Mejora estimada de tiempo</small><strong>{preview.improvement_pct.toFixed(2)}%</strong><span>Calculada con segundos exactos</span></div>
          </div><div className="sequence"><b>Secuencia calculada:</b> Centro de distribución → {preview.ordered_order_ids.map(id=>orders.find(o=>o.id===id)?.address_label||id).join(" → ")} → Centro de distribución</div><p className="fineprint">Fuente: {preview.matrix_provider} · Huella matriz: {preview.matrix_fingerprint.slice(0,12)}… · {preview.warnings.join(". ")}. Los minutos visibles se redondean; el porcentaje se calcula sobre los segundos exactos anteriores. No hay ahorro real observado.</p></>:<div className="empty">Selecciona pedidos y solicita una optimización para comparar recorridos. No se genera ninguna cifra sin datos de la matriz vial.</div>}
        </section>
        {savedRoute&&<section className="panel results">
          <div className="panelhead"><h2>05 · Ruta persistida</h2><div><span className="count">{savedRoute.status}</span> <button className="outline" disabled={!user||busy} onClick={()=>run(()=>showSavedRoute(savedRoute.id))}>Actualizar estado</button></div></div>
          <p><strong>ID:</strong> {savedRoute.id}</p>
          {savedRoute.status==="ACTIVE"&&<div className="gps-operator">
            <button type="button" className="outline" disabled={!user||busy} onClick={loadGps}>📍 Consultar GPS del repartidor</button>
            {gpsNotice&&<p role="status">{gpsNotice}</p>}
            {gpsPosition&&<p><strong>{gpsPosition.status}</strong> · {gpsPosition.latitude.toFixed(5)}, {gpsPosition.longitude.toFixed(5)} ·
              ±{Math.round(gpsPosition.accuracy_m)} m · Capturada {new Date(gpsPosition.captured_at).toLocaleString("es-PE")}</p>}
          </div>}
          {savedRoute.distribution_center_id&&<p><strong>Centro de distribución:</strong> {savedRoute.distribution_center_name||savedRoute.distribution_center_id} · {savedRoute.distribution_center_id.slice(0,8)}</p>}
          <div className="metrics">
            <div className="metric"><small>Orden original</small><strong>{mins(savedRoute.baseline_seconds)}</strong><span>{km(savedRoute.baseline_meters)} · {savedRoute.baseline_seconds} s exactos</span></div>
            <div className="metric chosen"><small>Ruta guardada</small><strong>{mins(savedRoute.optimized_seconds)}</strong><span>{km(savedRoute.optimized_meters)} · {savedRoute.optimized_seconds} s exactos</span></div>
            <div className="metric"><small>Mejora estimada de tiempo</small><strong>{savedRoute.improvement_pct.toFixed(2)}%</strong><span>Segundos exactos · openrouteservice</span></div>
          </div>
          <div className="sequence"><b>Secuencia persistida:</b> Centro de distribución → {(savedRoute.stops?.length?savedRoute.stops.map(s=>s.sequence+". "+s.address_label):savedRoute.ordered_order_ids).join(" → ")} → Depósito</div>
          <p className="fineprint">Mapa: {savedRoute.geometry_origin==="openrouteservice"?"trazado vial estimado de openrouteservice":"conectores esquemáticos entre paradas; no representan la vialidad"}.</p>
          {savedRoute.detail_warnings?.length>0&&<p className="fineprint">{savedRoute.detail_warnings.join(". ")}</p>}
          <p className="fineprint">Origen: {savedRoute.data_origin}. Minutos redondeados para lectura; porcentaje sobre segundos exactos. {savedRoute.driver_id?"Conductor asignado: "+savedRoute.driver_id+" · "+(savedRoute.status==="ACTIVE"?"recorrido iniciado.":savedRoute.status==="COMPLETED"?"recorrido finalizado.":"pendiente de activación."):"Esta ruta aún no está asignada a un conductor."}</p>
          {savedRoute.started_at&&<p className="fineprint">Inicio registrado: {new Date(savedRoute.started_at).toLocaleString("es-PE")} · versión {savedRoute.version}. Las métricas mostradas siguen siendo estimaciones, no tiempos observados.</p>}
        </section>}
        {savedRoute&&<section className="panel results">
          <div className="panelhead"><h2>06 · Asignar conductor</h2><span className="count">{savedRoute.driver_id?"ASIGNADA":"PENDIENTE"}</span></div>
          {savedRoute.driver_id?<p>Ruta asignada a un conductor. {savedRoute.status==="ACTIVE"?"El conductor inició el recorrido; seguimiento en modo consulta.":savedRoute.status==="COMPLETED"?"Recorrido finalizado.":"Continúa en estado PLANNED hasta que el conductor lo inicie."}</p>:<>
            <p>Selecciona un conductor activo y disponible. La asignación será validada de forma transaccional.</p>
            <button className="outline" disabled={!user||busy} onClick={loadDrivers}>Consultar conductores disponibles</button>
            <label className="driverPicker">Conductor
              <select value={selectedDriver} disabled={busy||!drivers.length} onChange={e=>{
                setSelectedDriver(e.target.value);pendingAssignmentKey.current=null;
              }}>
                <option value="">Selecciona un conductor</option>
                {drivers.map(d=><option key={d.uid} value={d.uid}>{d.display_name} · {d.uid.slice(0,8)}</option>)}
              </select>
            </label>
            <button className="accent" disabled={!user||busy||!selectedDriver} onClick={assignDriver}>Confirmar asignación</button>
            {!drivers.length&&<p className="fineprint">No hay candidatos cargados. Consulta conductores disponibles; puede no haber perfiles DRIVER creados todavía.</p>}
          </>}
        </section>}
      </article>
    </main><footer>SmartRoute AI · MVP académico · La previsualización no reserva pedidos; al guardar se crea una ruta PLANNED; la asignación posterior no inicia el recorrido.</footer>
  </div>;
}
createRoot(document.getElementById("root")).render(<App/>);
