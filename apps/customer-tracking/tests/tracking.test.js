import test from "node:test";import assert from "node:assert/strict";
import {tokenFromPath,customerView,progressForStatus} from "../tracking.js";
test("requires opaque token, rejects guesses and path traversal",()=>{
 const token="X".repeat(43);assert.equal(tokenFromPath("/t/"+token),token);
 for(const path of ["/t/123","/t/../orders","/orders/"+token,"/t/%2e%2e"]) assert.equal(tokenFromPath(path),null);
});
test("only exposes allowlisted order fields",()=>{
 const projected=customerView({order_reference:"SR-2038",status:"IN_TRANSIT",eta_minutes:12.2,driver_id:"private",latitude:-12.1,route_id:"secret",orders:[{id:"other"}]});
 assert.deepEqual(projected,{reference:"SR-2038",status:"IN_TRANSIT",label:"Pedido en camino",eta:12});
 assert.equal("driver_id" in projected,false);assert.equal("latitude" in projected,false);
});
test("does not invent ETA or accept unknown states",()=>{
 assert.equal(customerView({order_reference:"SR-1",status:"PENDING",eta_minutes:9}).eta,null);
 assert.equal(customerView({order_reference:"SR-1",status:"IN_TRANSIT",eta_minutes:null}).eta,null);
 assert.throws(()=>customerView({order_reference:"SR-1",status:"UNKNOWN"}));
});

test("rechaza referencias incorrectas y payloads malformados",()=>{
 for(const payload of [null,[],{}, {order_reference:"SR 123",status:"PENDING"},{order_reference:"SR-1",status:"__proto__"},{order_reference:"SR-1",status:"constructor"}]){
   assert.throws(()=>customerView(payload));
 }
});
test("protege contra ETA inválida y no la calcula para pedidos finalizados",()=>{
 for(const value of [-1,Infinity,NaN,"17",1441]) {
   assert.equal(customerView({order_reference:"SR-1",status:"IN_TRANSIT",eta_minutes:value}).eta,null);
 }
 for(const status of ["PENDING","ASSIGNED","DELIVERED","FAILED"]) {
   assert.equal(customerView({order_reference:"SR-1",status,eta_minutes:15}).eta,null);
 }
});
test("token de longitud límite y caracteres permitidos",()=>{
 const min="a".repeat(32),max="b".repeat(256);
 assert.equal(tokenFromPath("/t/"+min),min);
 assert.equal(tokenFromPath("/t/"+max),max);
 assert.equal(tokenFromPath("/t/"+min+"/"),min);
 assert.equal(tokenFromPath("/t/"+"c".repeat(257)),null);
 assert.equal(tokenFromPath("/t/"+"d".repeat(31)),null);
 assert.equal(tokenFromPath("/t/"+min+"?next=other"),null);
});

test("progreso orientativo consistente con estados permitidos",()=>{
 const pending=progressForStatus("PENDING");
 assert.equal(pending.failure,false);
 assert.deepEqual(pending.steps.map(x=>x.phase),["current","upcoming","upcoming","upcoming"]);
 assert.deepEqual(progressForStatus("ASSIGNED").steps.map(x=>x.phase),["previous","current","upcoming","upcoming"]);
 assert.deepEqual(progressForStatus("IN_TRANSIT").steps.map(x=>x.phase),["previous","previous","current","upcoming"]);
 assert.deepEqual(progressForStatus("DELIVERED").steps.map(x=>x.phase),["previous","previous","previous","current"]);
});
test("entrega fallida no inventa etapas cumplidas y estados invalidos se rechazan",()=>{
 assert.deepEqual(progressForStatus("FAILED"),{failure:true,steps:[]});
 assert.throws(()=>progressForStatus("UNKNOWN"));
 assert.throws(()=>progressForStatus("__proto__"));
});
