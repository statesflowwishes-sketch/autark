import express from "express";
import { WebSocketServer } from "ws";
import Redis from "ioredis";

const app = express();
const server = app.listen(8080, () => console.log("Overlay server 8080"));
const wss = new WebSocketServer({ server });
const redis = new Redis(process.env.REDIS_URL || "redis://redis:6379");

interface SessionClient { taskId?: string; ws: any }
const clients: SessionClient[] = [];

wss.on("connection", (ws) => {
  const client: SessionClient = { ws };
  clients.push(client);
  ws.on("message", (msg: string) => {
    try {
      const data = JSON.parse(msg);
      if (data.subscribeTask) client.taskId = data.subscribeTask;
    } catch {}
  });
  ws.on("close", () => {
    const idx = clients.indexOf(client);
    if (idx >= 0) clients.splice(idx, 1);
  });
});

redis.subscribe("pty-stream");

redis.on("message", (_channel, message) => {
  const evt = JSON.parse(message);
  clients.forEach(c => {
    if (!c.taskId || c.taskId === evt.taskId) {
      c.ws.send(JSON.stringify(evt));
    }
  });
});