import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getRoom,
  getRoomParticipants,
  setReady,
  getQuestion
} from "../services/api";

function Room() {
  const { roomId } = useParams();

  const [room, setRoom] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [gameStarted, setGameStarted] = useState(false);
  const [questionId, setQuestionId] = useState(null);
  const [question, setQuestion] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [wsStatus, setWsStatus] =
    useState("Подключение...");

  async function loadRoom() {
    try {
      const data = await getRoom(roomId);

      setRoom(data);
    } catch (error) {
      console.error("Ошибка загрузки комнаты:", error);

      setError(
        error.message || "Ошибка загрузки комнаты"
      );
    }
  }

  async function loadParticipants() {
    try {
      const data =
        await getRoomParticipants(roomId);

      setParticipants(data);
    } catch (error) {
      console.error(
        "Ошибка загрузки участников:",
        error
      );

      setError(
        error.message ||
        "Ошибка загрузки участников"
      );
    } finally {
      setLoading(false);
    }
  }
  async function handleReady() {
  try {
    await setReady(roomId);

    await loadRoom();
    await loadParticipants();
  } catch (error) {
    setError(
      error.message || "Не удалось подтвердить готовность"
    );
  }
}
  useEffect(() => {
    if (!roomId) {
      setError("ID комнаты отсутствует");
      setLoading(false);
      return;
    }

    loadRoom();
    loadParticipants();
  }, [roomId]);

  useEffect(() => {
    if (!roomId) {
      return;
    }

    const userId =
      localStorage.getItem("user_id");

    if (!userId) {
      setWsStatus(
        "Ошибка: пользователь не авторизован"
      );
      return;
    }

    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/rooms/${roomId}?user_id=${userId}`
    );

    socket.onopen = () => {
      console.log(
        "WebSocket подключен"
      );

      setWsStatus("Подключено");
    };

    socket.onmessage = (event) => {
      const message =
        JSON.parse(event.data);

      console.log(
        "WebSocket сообщение:",
        message
      );

      if (
        message.type ===
        "player_connected"
      ) {
        loadParticipants();
      }

      if (
        message.type ===
        "player_disconnected"
      ) {
        loadParticipants();
      }
      if (message.type === "game_started") {
        setGameStarted(true);
        setQuestionId(message.question_id);
      
        console.log(
          "Игра началась. Первый вопрос:",
          message.question_id
  );
}
    };

    socket.onerror = (error) => {
      console.error(
        "WebSocket ошибка:",
        error
      );

      setWsStatus(
        "Ошибка подключения"
      );
    };

    socket.onclose = () => {
      console.log(
        "WebSocket отключен"
      );

      setWsStatus("Отключено");
    };

    return () => {
      socket.close();
    };
  }, [roomId]);

  if (loading) {
    return (
      <div>
        <h1>BrainPlizz</h1>
        <p>Загрузка комнаты...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h1>BrainPlizz</h1>

        <h2>Ошибка</h2>

        <p>{error}</p>
      </div>
    );
  }

  if (!room) {
    return (
      <div>
        <h1>BrainPlizz</h1>

        <h2>Комната не найдена</h2>
      </div>
    );
  }

  return (
    <div>
      <h1>BrainPlizz</h1>

      <h2>Игровая комната</h2>

      <p>Код комнаты:</p>

      <h3>{room.code}</h3>

      <p>
        WebSocket: {wsStatus}
      </p>

      <p>
        Игроки: {participants.length} /{" "}
        {room.max_players}
      </p>

      {error && (
        <p>{error}</p>
      )}

      <ul>
        {participants.map(
          (participant) => (
            <li key={participant.id}>
              {participant.user_id}
            </li>
          )
        )}
      </ul>

      {room.status === "waiting" && (
        <p>
          Ожидание игроков...
        </p>
      )}
      {room.status === "waiting" && (
        <button onClick={handleReady}>
          Я готов
        </button>
)}
      {room.status === "playing" && (
        <p>
          Игра началась!
        </p>
      )}
    </div>
  );
}

export default Room;