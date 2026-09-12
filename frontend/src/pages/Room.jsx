import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getRoom,
  getRoomParticipants,
  setReady,
  getQuestion,
  submitAnswer
} from "../services/api";

function Room() {
  const { roomId } = useParams();

  const [room, setRoom] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [gameStarted, setGameStarted] = useState(false);
  const [gameFinished, setGameFinished] = useState(false);
  const [questionId, setQuestionId] = useState(null);
  const [question, setQuestion] = useState(null);
  const questionIdRef = useRef(null);
  const [answerResult, setAnswerResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);
  const timerRef = useRef(null);
  const [currentParticipant, setCurrentParticipant] =
  useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [wsStatus, setWsStatus] =
    useState("Подключение...");
  

  function startLocalTimer() {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    setTimeLeft(30);

    timerRef.current = setInterval(() => {
      setTimeLeft((previousTime) => {
        if (previousTime <= 1) {
          clearInterval(timerRef.current);
          timerRef.current = null;
          return 0;
        }

        return previousTime - 1;
      });
    }, 1000);
  }
  
 
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
      console.log("Участники комнаты:", data);
      const userId =
        localStorage.getItem("user_id");

      const currentUserParticipant =
        data.find(
          (participant) =>
            participant.user_id === userId
        );

      console.log(
        "Мой участник:",
        currentUserParticipant
      );

      setCurrentParticipant(
        currentUserParticipant
      );
      console.log(
        "Мой participant_id:",
        currentUserParticipant?.id
      );

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

  async function handleAnswer(selectedAnswer) {
  try {
    const answeredQuestionId = question.id;
    const result = await submitAnswer(
      currentParticipant.id,
      answeredQuestionId,
      selectedAnswer
    );

    console.log("Результат ответа:", result);
    
    if (questionIdRef.current === answeredQuestionId) {
      setAnswerResult(result);
    }
  } catch (error) {
    console.error(
      "Ошибка отправки ответа:",
      error
    );
    console.log("ОШИБКА ОТВЕТА:", error);
    console.log("ТИП ОШИБКИ:", typeof error);
    setError(
      error?.message ||
      String(error) ||
      "Не удалось отправить ответ"
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
  if (!questionId) {
    return;
  }

  async function loadQuestion() {
    try {
      const data = await getQuestion(questionId);

      console.log("Получен вопрос:", data);

      setQuestion(data);
    } catch (error) {
      console.error(
        "Ошибка загрузки вопроса:",
        error
      );

      setError(
        error.message || "Ошибка загрузки вопроса"
      );
    }
  }

  loadQuestion();
}, [questionId]);

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
        setGameFinished(false);
        setQuestionId(message.question_id);
        questionIdRef.current = message.question_id;
        setAnswerResult(null);

        startLocalTimer();

        console.log(
          "Игра началась. Первый вопрос:",
          message.question_id
        );
      }
      if (message.type === "next_question") {
        setQuestionId(message.question_id);
        questionIdRef.current = message.question_id;
        setAnswerResult(null);
        
        startLocalTimer();

        console.log(
          "Следующий вопрос:",
          message.question_id
        );
      }
      if (message.type === "question_timeout") {
        setTimeLeft(0);
        setAnswerResult(null);
        console.log("Время на вопрос истекло");
      }
      if (message.type === "game_finished") {
        setGameFinished(true);
        setTimeLeft(0);
        setAnswerResult(null);

        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }

        console.log("Игра завершена");
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

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
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
      {gameFinished && (
        <div>
          <h2>Игра завершена!</h2>
          <p>Все вопросы закончились.</p>
          <p>Спасибо за участие!</p>
        </div>
      )}
      {gameStarted && question && !gameFinished && (
        <div>
          <h2>Вопрос</h2>
          {timeLeft !== null && (
            <p>Осталось времени: {timeLeft} сек.</p>
          )}
          <p>{question.text}</p>
          <button onClick={() => handleAnswer(1)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_1}
          </button>
          <button onClick={() => handleAnswer(2)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_2}
          </button>
          <button onClick={() => handleAnswer(3)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_3}
          </button>
          <button onClick={() => handleAnswer(4)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_4}
          </button>
          {answerResult && (
            <div>
              {answerResult.is_correct ? (
                <p>✅ Правильно!</p>
              ) : (
                <p>❌ Неправильно!</p>
              )}
              <p>Очки: {answerResult.score}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Room;