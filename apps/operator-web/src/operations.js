/** Pure, read-only projections for the operator center. */
export const ORDER_STATES = ["ALL", "PENDING", "ASSIGNED", "IN_TRANSIT", "DELIVERED", "FAILED"];
export const ROUTE_STATES = ["ALL", "PLANNED", "ACTIVE", "COMPLETED", "CANCELLED"];
export const stateLabel = {
  ALL:"Todos", PENDING:"Pendientes", ASSIGNED:"Asignados", IN_TRANSIT:"En camino",
  DELIVERED:"Entregados", FAILED:"No entregados", PLANNED:"Planificadas",
  ACTIVE:"En recorrido", COMPLETED:"Finalizadas", CANCELLED:"Canceladas",
};
export function filterOrders(orders, state="ALL", query="") {
  const term = String(query).trim().toLocaleLowerCase("es-PE");
  return orders.filter(o =>
    (state === "ALL" || o.status === state) &&
    (!term || [o.id, o.address_label, o.route_id].some(x => String(x || "").toLocaleLowerCase("es-PE").includes(term)))
  );
}
export function filterRoutes(routes, state="ALL") {
  return routes.filter(r => state === "ALL" || r.status === state);
}
export function summarizeOperations(orders, routes) {
  const ordersByState = Object.fromEntries(ORDER_STATES.filter(s=>s!=="ALL").map(s=>[s,0]));
  const routesByState = Object.fromEntries(ROUTE_STATES.filter(s=>s!=="ALL").map(s=>[s,0]));
  orders.forEach(o=>{if(Object.hasOwn(ordersByState,o.status))ordersByState[o.status]++;});
  routes.forEach(r=>{if(Object.hasOwn(routesByState,r.status))routesByState[r.status]++;});
  const resolved = ordersByState.DELIVERED + ordersByState.FAILED;
  const eligible = routes.filter(r=>Number.isFinite(r.baseline_seconds) && Number.isFinite(r.optimized_seconds) && r.baseline_seconds>0);
  const baseline = eligible.reduce((n,r)=>n+r.baseline_seconds,0);
  const optimized = eligible.reduce((n,r)=>n+r.optimized_seconds,0);
  return {
    ordersByState, routesByState, orderCount:orders.length, routeCount:routes.length,
    resolved, delivered:ordersByState.DELIVERED, failed:ordersByState.FAILED,
    deliveryRate:resolved ? 100*ordersByState.DELIVERED/resolved : null,
    estimatedImprovement:baseline>0 ? 100*(baseline-optimized)/baseline : null,
    estimatedRoutes:eligible.length,
  };
}
/** US-011: estimates use exact seconds/meters from persisted route records.
 * No GPS-derived duration, punctuality or savings are inferred.
 */
export function projectRouteIndicators(routes) {
  return routes.map(route => {
    const baselineSeconds = route.baseline_seconds;
    const optimizedSeconds = route.optimized_seconds;
    const baselineMeters = route.baseline_meters;
    const optimizedMeters = route.optimized_meters;
    const validTimes = Number.isFinite(baselineSeconds) && Number.isFinite(optimizedSeconds)
      && baselineSeconds > 0 && optimizedSeconds >= 0;
    const validDistances = Number.isFinite(baselineMeters) && Number.isFinite(optimizedMeters)
      && baselineMeters > 0 && optimizedMeters >= 0;
    return {
      id: route.id, status: route.status, stopCount: Array.isArray(route.order_ids) ? route.order_ids.length : 0,
      baselineSeconds:validTimes ? baselineSeconds : null,
      optimizedSeconds:validTimes ? optimizedSeconds : null,
      baselineMeters:validDistances ? baselineMeters : null,
      optimizedMeters:validDistances ? optimizedMeters : null,
      timeImprovement:validTimes ? 100*(baselineSeconds-optimizedSeconds)/baselineSeconds : null,
      distanceImprovement:validDistances ? 100*(baselineMeters-optimizedMeters)/baselineMeters : null,
      dataOrigin:"estimated",
      // No observed driving times are present in the read-only route list.
      observedDuration:null,
    };
  });
}

/** Pagination is explicit so client-side filters never masquerade as server-side aggregate counts. */
export async function fetchPaged(fetchPage,{limit=50,maxPages=10}={}) {
  const items=[];
  let cursor=null, truncated=false;
  for(let page=0;page<maxPages;page++){
    const response=await fetchPage(limit,cursor);
    if(!response || !Array.isArray(response.items)) throw new Error("Respuesta de paginación inválida");
    items.push(...response.items);
    if(!response.next_cursor) return {items,truncated:false};
    if(response.next_cursor===cursor) throw new Error("Cursor de paginación repetido");
    cursor=response.next_cursor;
    truncated=true;
  }
  return {items,truncated};
}
