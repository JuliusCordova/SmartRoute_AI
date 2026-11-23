import test from "node:test";
import assert from "node:assert/strict";
import {projectOrderTracking,trackingSummary} from "../src/tracking.js";
test("preserva secuencia y estados conocidos sin inventar ETA",()=>{
 const route={order_ids:["b","a"],stops:[{order_id:"a",sequence:2,address_label:"Calle A"},{order_id:"b",sequence:1,address_label:"Calle B"}]};
 const items=projectOrderTracking(route,[{id:"a",status:"DELIVERED"},{id:"b",status:"IN_TRANSIT"}]);
 assert.deepEqual(items.map(x=>x.id),["b","a"]);
 assert.deepEqual(items.map(x=>x.label),["En recorrido","Entregado"]);
 assert.equal(Object.hasOwn(items[0],"eta"),false);
 assert.deepEqual(trackingSummary(items),{total:2,confirmed:2,delivered:1,failed:0,unresolved:1,partial:false});
});
test("consulta parcial no asigna estado ni da por resuelto un pedido ausente",()=>{
 const items=projectOrderTracking({order_ids:["a","b"]},[{id:"a",status:"FAILED",address_label:"Calle A"}]);
 assert.equal(items[1].status,null);
 assert.equal(items[1].label,"Estado no disponible");
 assert.deepEqual(trackingSummary(items),{total:2,confirmed:1,delivered:0,failed:1,unresolved:0,partial:true});
});
test("sin ruta ni pedidos no genera resultados",()=>{
 assert.deepEqual(projectOrderTracking(null,[]),[]);
 assert.equal(trackingSummary([]).total,0);
});
