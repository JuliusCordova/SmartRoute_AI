/** Validaciones y proyección del contrato público mínimo. No confiar en datos de cliente para autorizar. */
export function tokenFromPath(pathname) {
  const match=String(pathname).match(/^\/t\/([A-Za-z0-9_-]{32,256})\/?$/);
  return match ? match[1] : null;
}
const STATUSES={PENDING:"Pedido registrado",ASSIGNED:"Pedido asignado",IN_TRANSIT:"Pedido en camino",DELIVERED:"Pedido entregado",FAILED:"Entrega no completada"};
export function customerView(payload) {
  if(!payload || typeof payload!=="object" || Array.isArray(payload)) throw new Error("Respuesta inválida");
  if(typeof payload.order_reference!=="string" || !/^[a-zA-Z0-9_-]{1,40}$/.test(payload.order_reference)) throw new Error("Referencia inválida");
  if(!Object.hasOwn(STATUSES,payload.status)) throw new Error("Estado inválido");
  // Allowlist: nunca mostrar campos adicionales entregados por error (driver_id, lat/lng, route_id, otras órdenes).
  const eta=Number.isFinite(payload.eta_minutes) && payload.eta_minutes>=0 && payload.eta_minutes<=1440?Math.round(payload.eta_minutes):null;
  return {reference:payload.order_reference,status:payload.status,label:STATUSES[payload.status],
    eta:payload.status==="IN_TRANSIT"?eta:null};
}
