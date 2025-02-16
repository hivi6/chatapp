const URL = "http://localhost:8000";
const CREDENTIALS = "include";

let WS = null;
let WS_MESSAGE_HANDLER = {};

export async function ping() {
  try {
    // Check if server is pingable
    const res = await fetch(`${URL}/misc/ping`);
    if (res.status !== 200) {
      return { error: await res.text() };
    }

    // Send the server response
    return { data: await res.text() };
  } catch (e) {
    return { error: "unable to connect to server" };
  }
}

export async function register({ username, password, fullname }) {
  try {
    // Register an user
    const res = await fetch(`${URL}/register`, {
      method: "POST",
      body: JSON.stringify({ username, password, fullname }),
    });
    if (res.status !== 201) {
      return { error: await res.text() };
    }

    return { data: await res.text() };
  } catch (e) {
    return { error: "unable to connect to server" };
  }
}

export async function login({ username, password }) {
  try {
    // Register an user
    const res = await fetch(`${URL}/auth/login`, {
      method: "POST",
      credentials: CREDENTIALS,
      body: JSON.stringify({ username, password }),
    });
    if (res.status !== 202) {
      return { error: await res.text() };
    }

    return { data: await res.text() };
  } catch (e) {
    return { error: "unable to connect to server" };
  }
}

export async function verify() {
  try {
    // Register an user
    const res = await fetch(`${URL}/auth/verify`, {
      method: "GET",
      credentials: CREDENTIALS,
    });
    if (res.status !== 200) {
      return { error: await res.text() };
    }

    return { data: await res.text() };
  } catch (e) {
    return { error: "unable to connect to server" };
  }
}

export function connectWs() {
  if (WS !== null) {
    WS.close();
    WS_MESSAGE_HANDLER = {};
  }

  // Handle create a new websocket connection
  const ws = new WebSocket(`${URL}/ws`);

  ws.onmessage = (e) => {
    const event = JSON.parse(e.data);
    if (WS_MESSAGE_HANDLER[event.type] === undefined) {
      console.log("No such handler");
      console.log(event);
    } else {
      // Call the handler
      WS_MESSAGE_HANDLER[event.type](event);
    }
  };

  WS = ws;
  WS_MESSAGE_HANDLER = {};
}

export function sendWSPingEvent() {
  if (WS) {
    WS.send(JSON.stringify({ type: "ping" }));
  }
}

export function addWSEventHandler(eventType, handler) {
  WS_MESSAGE_HANDLER[eventType] = handler;
}

export function deleteWSEventHandler(eventType) {
  delete WS_MESSAGE_HANDLER[eventType];
}
