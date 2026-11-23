import {tokenFromPath,customerView} from "./tracking.js";
const root=document.getElementById("content");
function el(tag,text,cls){const x=document.createElement(tag);x.textContent=text;if(cls)x.className=cls;return x;}
function message(title,description){
  root.replaceChildren(el("h2",title),el("p",description,"hint"));
}
async function init(){
  const token=tokenFromPath(window.location.pathname);
  if(!token){message("Enlace inválido","Revisa el enlace original de seguimiento.");return;}
  const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),10000);
  try{
    // Este endpoint no existe todavía: debe implementarse en el backend con validación del token y respuesta acotada.
    const resp=await fetch("/api/v1/public/tracking/"+encodeURIComponent(token),{
      method:"GET",cache:"no-store",credentials:"omit",referrerPolicy:"no-referrer",
      headers:{"Accept":"application/json"},signal:controller.signal
    });
    if(!resp.ok){message("Seguimiento no disponible","El enlace puede haber caducado o el servicio no está habilitado. Solicita uno nuevo al operador.");return;}
    const view=customerView(await resp.json());
    const wrap=document.createElement("div");
    wrap.append(el("div","PEDIDO "+view.reference,"reference"),el("h2",view.label,"status"));
    if(view.eta!==null)wrap.append(el("div","Llegada estimada: "+view.eta+" min","eta"),el("p","Tiempo estimado, sujeto a variaciones.","hint"));
    else wrap.append(el("p","No hay una estimación de llegada disponible para este estado.","hint"));
    wrap.append(el("p","Información limitada a este pedido. No se comparte posición GPS ni el recorrido del repartidor.","privacy-note"));
    root.replaceChildren(wrap);
  }catch{message("No se pudo consultar","Comprueba tu conexión e intenta abrir nuevamente el enlace.");}
  finally{clearTimeout(timeout);}
}
init();
