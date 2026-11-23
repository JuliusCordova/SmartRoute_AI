/** US-016: read-only operator projection. Never synthesize events, GPS, or ETA. */
const ORDER_LABELS={PENDING:"Pendiente",ASSIGNED:"Asignado",IN_TRANSIT:"En recorrido",DELIVERED:"Entregado",FAILED:"No entregado"};
export function projectOrderTracking(route,orders=[]) {
  if(!route || !Array.isArray(route.order_ids)) return [];
  const byId=new Map(orders.map(o=>[o.id,o]));
  const stops=new Map((route.stops||[]).map(s=>[s.order_id||s.id,s]));
  return route.order_ids.map((id,index)=>{
    const order=byId.get(id), stop=stops.get(id);
    const status=order?.status||null;
    return {
      id,sequence:Number.isInteger(stop?.sequence)?stop.sequence:index+1,
      address:stop?.address_label||order?.address_label||"Dirección no disponible",
      status, label:ORDER_LABELS[status]||"Estado no disponible",
      terminal:status==="DELIVERED"||status==="FAILED",
      confirmed:Boolean(order),
    };
  }).sort((a,b)=>a.sequence-b.sequence);
}
export function trackingSummary(items) {
  const known=items.filter(item=>item.confirmed);
  return {
    total:items.length,confirmed:known.length,
    delivered:known.filter(item=>item.status==="DELIVERED").length,
    failed:known.filter(item=>item.status==="FAILED").length,
    unresolved:known.filter(item=>!item.terminal).length,
    partial:known.length!==items.length,
  };
}
