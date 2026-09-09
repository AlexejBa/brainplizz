const API_URL = "http://127.0.0.1:8000";

export async function login(email, password) {
  const response = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Ошибка авторизации");
  }

  return data;
}


export async function register(username, email, password) {
  const response = await fetch(`${API_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Ошибка регистрации");
  }

  return data;
}
export async function getMe() {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_URL}/auth/me`, {
    method: "GET",
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Ошибка проверки авторизации");
  }

  return data;
}
export async function createRoom(maxPlayers = 4) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_URL}/rooms`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      max_players: maxPlayers,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Ошибка создания комнаты"
    );
  }

  return data;
}
export async function getRoom(roomId) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_URL}/rooms/${roomId}`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Ошибка получения комнаты"
    );
  }

  return data;
}

export async function joinRoom(code) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_URL}/rooms/join`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({
      code: code.toUpperCase(),
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Ошибка присоединения к комнате"
    );
  }

  return data;
}

export async function getRoomParticipants(roomId) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_URL}/rooms/${roomId}/participants`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Ошибка получения участников"
    );
  }

  return data;
}
