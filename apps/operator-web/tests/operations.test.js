import test from "node:test";
import assert from "node:assert/strict";
import {filterOrders,filterRoutes,summarizeOperations,fetchPaged} from "../src/operations.js";

const orders=[
  {id:"a",address_label:"Av. Arequipa",status:"PENDING"},
  {id:"b",address_label:"Miraflores",status:"DELIVERED",route_id:"r1"},
  {id:"c",address_label:"Av. Arequipa Sur",status:"FAILED",route_id:"r2"},
  {id:"d",address_label:"Los Olivos",status:"ASSIGNED"},
  {id:"e",address_label:"Lince",status:"IN_TRANSIT"},
];
const routes=[
  {id:"r1",status:"COMPLETED",baseline_seconds:2400,optimized_seconds:1800},
  {id:"r2",status:"PLANNED",baseline_seconds:1200,optimized_seconds:900},
  {id:"r3",status:"ACTIVE",baseline_seconds:0,optimized_seconds:0},
];
test("US-004 filtra por cada estado sin alterar la fuente",()=>{
  for(const state of ["PENDING","DELIVERED","FAILED","ASSIGNED","IN_TRANSIT"])
    assert.equal(filterOrders(orders,state).length,1);
  assert.equal(filterOrders(orders,"ALL").length,5);
  assert.equal(orders.length,5);
});
test("US-004 combina estado, dirección e ID, no depende de mayúsculas",()=>{
  assert.deepEqual(filterOrders(orders,"FAILED","arequipa").map(o=>o.id),["c"]);
  assert.deepEqual(filterOrders(orders,"ALL","R1").map(o=>o.id),["b"]);
  assert.equal(filterOrders(orders,"DELIVERED","arequipa").length,0);
});
test("dashboard respeta conteos y no inventa porcentaje sin resueltos",()=>{
  const s=summarizeOperations(orders,routes);
  assert.equal(s.ordersByState.PENDING,1);
  assert.equal(s.delivered,1);assert.equal(s.failed,1);assert.equal(s.deliveryRate,50);
  assert.equal(s.routesByState.COMPLETED,1);
  assert.equal(s.estimatedRoutes,2);
  assert.equal(s.estimatedImprovement,25);
  assert.equal(summarizeOperations([],[]).deliveryRate,null);
  assert.equal(summarizeOperations([],[]).estimatedImprovement,null);
  assert.equal(filterRoutes(routes,"COMPLETED").length,1);
});
test("paginación recorre cursores y expone límite de cobertura",async()=>{
  const a=await fetchPaged(async(_,cursor)=>cursor?{items:[{id:"2"}],next_cursor:null}:{items:[{id:"1"}],next_cursor:"1"}, {maxPages:2});
  assert.deepEqual(a.items.map(x=>x.id),["1","2"]);assert.equal(a.truncated,false);
  const b=await fetchPaged(async()=>({items:[{id:"x"}],next_cursor:"more"}),{maxPages:1});
  assert.equal(b.truncated,true);
});
test("detecta repetición de cursor y no la interpreta como cobertura total",async()=>{
  await assert.rejects(()=>fetchPaged(async()=>({items:[],next_cursor:"same"}),{maxPages:3}),/repetido/);
});
