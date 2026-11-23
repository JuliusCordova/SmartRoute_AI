import test from "node:test";import assert from "node:assert/strict";
import {tokenFromPath,customerView} from "../tracking.js";
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
