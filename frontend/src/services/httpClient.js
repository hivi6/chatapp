const URL = "http://localhost:8000";
const CREDENTIALS = "include";

async function ping() {
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

async function register({ username, password, fullname }) {
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

async function login({ username, password }) {
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

async function verify() {
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

export { ping, register, login, verify };
