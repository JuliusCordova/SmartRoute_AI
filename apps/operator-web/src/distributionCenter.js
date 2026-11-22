/** Pure validation of an operator-selected origin. Existing routes are immutable. */
export function distributionCenterReady(choice, confirmed, name, insideArea) {
  return Boolean(choice && confirmed && String(name||"").trim() &&
    Number.isFinite(Number(choice.latitude)) && Number.isFinite(Number(choice.longitude)) &&
    insideArea(Number(choice.latitude), Number(choice.longitude)));
}
export function distributionCenterPayload(choice) {
  if(!choice) throw new Error("Centro de distribución no seleccionado");
  return {latitude:Number(choice.latitude),longitude:Number(choice.longitude)};
}
