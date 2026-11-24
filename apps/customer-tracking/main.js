import {tokenFromPath,customerView,progressForStatus} from "./tracking.js";
const root=document.getElementById("content");
function el(tag,text,cls){
  const x=document.createElement(tag);
  x.textContent=text;
  if(cls)x.className=cls;
  return x;
}
function message(title,description){
  root.replaceChildren(el("h2",title),el("p",description,"hint"));
}
function render(view){
  const wrap=el("div","","tracking-result");
  const hero=el("section","","status-hero status-"+view.status.toLowerCase());
  const heading=el("div","","status-heading");
  heading.append(el("span","Estado actual del pedido","status-kicker"),el("span","●","status-dot"));
  hero.append(
    el("div","PEDIDO "+view.reference,"reference"),
    heading,
    el("h2",view.label,"status")
  );
  if(view.eta!==null){
    hero.append(
      el("div","Llegada estimada: "+view.eta+" min","eta"),
      el("p","Estimación sujeta a variaciones.","eta-note")
    );
  } else {
    hero.append(el("p","Tiempo estimado de llegada no disponible.","eta-note"));
  }
  wrap.append(hero);

  const progress=progressForStatus(view.status);
  const panel=el("section","","progress-panel");
  panel.append(el("h3","Progreso de la entrega","progress-title"));
  if(progress.failure){
    panel.append(el("p","La entrega no se completó. No hay detalles adicionales disponibles en este enlace.","progress-info"));
  } else {
    const steps=el("ol","","progress-list");
    for(const stage of progress.steps){
      const item=el("li","","progress-step "+stage.phase);
      const symbol=stage.phase==="previous"?"✓":stage.phase==="current"?"●":"○";
      item.append(el("span",symbol,"step-marker"),el("span",stage.label,"step-label"));
      if(stage.phase==="current")item.setAttribute("aria-current","step");
      steps.append(item);
    }
    panel.append(steps,el("p","Etapas orientativas según el estado actual; no representan un historial de eventos.","progress-hint"));
  }
  wrap.append(panel);
  wrap.append(el("p","Información limitada a este pedido. No se comparte posición GPS ni el recorrido del repartidor.","privacy-note"));
  root.replaceChildren(wrap);
}
async function init(){
  const token=tokenFromPath(window.location.hash.startsWith("#") ? window.location.hash.slice(1) : window.location.pathname);
  if(!token){message("Enlace inválido","Revisa el enlace original de seguimiento.");return;}
  const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),10000);
  try{
    // El gateway enruta esta consulta pública al backend solo cuando el feature gate está habilitado.
    const resp=await fetch("/api/v1/public/tracking",{
      method:"POST",cache:"no-store",credentials:"omit",referrerPolicy:"no-referrer",
      headers:{"Accept":"application/json","Content-Type":"application/json"},body:JSON.stringify({token}),signal:controller.signal
    });
    if(!resp.ok){message("Seguimiento no disponible","El enlace puede haber caducado o el servicio no está habilitado. Solicita uno nuevo al operador.");return;}
    render(customerView(await resp.json()));
  }catch{message("No se pudo consultar","Comprueba tu conexión e intenta abrir nuevamente el enlace.");}
  finally{clearTimeout(timeout);}
}
init();
