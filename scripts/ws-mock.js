// Simple WebSocket mock server that emits department queue updates periodically (ESM)
import { WebSocketServer } from 'ws';

const port = process.env.PORT || 8001;
const wss = new WebSocketServer({ port });

console.log(`WS mock server listening on ws://localhost:${port}`);

const makeQueue = (deptId) => ([
  { id: 1, ticket: 'A201', patient_name: 'Anna', service: 'Consult', wait_seconds: Math.floor(Math.random()*300), status: 'waiting', department_id: deptId },
  { id: 2, ticket: 'A202', patient_name: 'Ben', service: 'X-ray', wait_seconds: Math.floor(Math.random()*300), status: 'waiting', department_id: deptId }
]);

wss.on('connection', function connection(ws, req) {
  console.log('client connected');
  // send periodic updates
  const interval = setInterval(() => {
    const deptId = 1;
    const msg = JSON.stringify({ type: 'queue_update', department_id: deptId, queue: makeQueue(deptId) });
    try { ws.send(msg); } catch (e) { console.debug('send error', e); }
  }, 5000);

  ws.on('close', () => {
    clearInterval(interval);
  });
});
