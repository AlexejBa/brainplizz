import { useEffect, useRef, useState } from "react";
import { useParams } from "react-router-dom";
import {
  getRoom,
  getRoomParticipants,
  setReady,
  startGame,
  getQuestion,
  submitAnswer,
  getLeaderboard
} from "../services/api";

function Room() {
  const { roomId } = useParams();
  const currentUserId = localStorage.getItem("user_id");
  const [room, setRoom] = useState(null);
  const [participants, setParticipants] = useState([]);
  const [connectedPlayers, setConnectedPlayers] = useState([]);
  const [gameStarted, setGameStarted] = useState(false);
  const [gameFinished, setGameFinished] = useState(false);
  const [leaderboard, setLeaderboard] = useState([]);
  const [questionId, setQuestionId] = useState(null);
  const [question, setQuestion] = useState(null);
  const questionIdRef = useRef(null);
  const socketRef = useRef(null);
  const [answerResult, setAnswerResult] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);
  const timerRef = useRef(null);
  const [currentParticipant, setCurrentParticipant] =
  useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");


  const [wsStatus, setWsStatus] =
    useState("Подключение...");
  const isHost = room?.host_id === currentUserId;

  function getAnswerText(answerNumber) {
    if (!question) {
      return "";
    }

    const answers = {
      1: question.answer_1,
      2: question.answer_2,
      3: question.answer_3,
      4: question.answer_4
    };

    return answers[answerNumber] || "";
  }

  function getAnswerClass(answerNumber) {
    if (!answerResult) {
      return "";
    }

    const correctAnswer = Number(answerResult.correct_answer);
    const selectedAnswer = Number(answerResult.selected_answer);

    if (answerNumber === correctAnswer) {
      return "answer-correct";
    }

    if (
      answerNumber === selectedAnswer &&
      selectedAnswer !== correctAnswer
    ) {
      return "answer-wrong";
    }

    return "";
  }

  function startLocalTimer(initialSeconds = 30) {
    if (timerRef.current) {
      clearInterval(timerRef.current);
    }

    setTimeLeft(initialSeconds);

    if (initialSeconds <= 0) {
      timerRef.current = null;
      return;
    }

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

      if (data.status === "finished") {
        setGameStarted(false);
        setGameFinished(true);
        setQuestionId(null);
        setQuestion(null);
        setTimeLeft(0);

        if (timerRef.current) {
          clearInterval(timerRef.current);
          timerRef.current = null;
        }

        await loadLeaderboard();
      }
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
   

  async function loadLeaderboard() {
    try {
      const data = await getLeaderboard(roomId);

      console.log(
        "Итоговая таблица:",
        data
      );

      setLeaderboard(
        data.participants || []
      );
    } catch (error) {
      console.error(
        "Ошибка загрузки итоговой таблицы:",
        error
      );

      setError(
        error.message ||
        "Не удалось загрузить итоговую таблицу"
      );
    }
  }

  async function handleReady() {
    try {
      await setReady(roomId);

      await loadRoom();
      await loadParticipants();
    } catch (error) {
      setError(
        error.message ||
        "Не удалось подтвердить готовность"
      );
    }
  }

  async function handleStartGame() {
    try {
      setError("");

      await startGame(roomId);

      await loadRoom();
      await loadParticipants();
    } catch (error) {
      console.error(
        "Ошибка запуска игры:",
        error
      );

      setError(
        error.message ||
        "Не удалось начать игру"
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

    if (
      String(questionIdRef.current) ===
      String(answeredQuestionId)
    ) {
      setAnswerResult({
        ...result,
        selected_answer: selectedAnswer,
      });
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


async function handleNextQuestion() {

  console.log(
    "НАЖАТА КНОПКА СЛЕДУЮЩИЙ ВОПРОС"
  );

  console.log(
    "isHost:",
    isHost
  );

  console.log(
    "socket:",
    socketRef.current
  );

  console.log(
    "socket readyState:",
    socketRef.current?.readyState
  );
  try {
    setError("");

    if (!isHost) {
      setError(
        "Только ведущий может перейти к следующему вопросу"
      );
      return;
    }

    if (
      !socketRef.current ||
      socketRef.current.readyState !== WebSocket.OPEN
    ) {
      setError(
        "WebSocket не подключён"
      );
      return;
    }

    socketRef.current.send(
      JSON.stringify({
        type: "next_question"
      })
    );
  } catch (error) {
    console.error(
      "Ошибка перехода к следующему вопросу:",
      error
    );

    setError(
      error.message ||
      "Не удалось перейти к следующему вопросу"
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
      const data = await getQuestion(roomId);

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

  let isUnmounted = false;

  const socket = new WebSocket(
    `ws://127.0.0.1:8000/ws/rooms/${roomId}?user_id=${userId}`
  );

  socketRef.current = socket;
  socket.onopen = () => {
    if (isUnmounted) {
      return;
    }

    console.log(
      "WebSocket подключен"
    );

    setWsStatus("Подключено");
  };

  socket.onmessage = (event) => {
    if (isUnmounted) {
      return;
    }

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

    if (message.type === "presence_updated") {
      setConnectedPlayers(
        message.connected_user_ids || []
      );
    }

    if (message.type === "game_started") {
      setGameStarted(true);
      setGameFinished(false);
      setQuestion(null);
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
      setQuestion(null);
      setQuestionId(message.question_id);
      questionIdRef.current = message.question_id;
      setAnswerResult(null);

      startLocalTimer();

      console.log(
        "Следующий вопрос:",
        message.question_id
      );
    }

  if (message.type === "current_question") {
    setGameStarted(true);
    setGameFinished(false);
    setQuestion(null);
    setQuestionId(message.question_id);
    questionIdRef.current = message.question_id;
    setAnswerResult(null);

    const remainingSeconds =
      message.remaining_seconds ?? 30;

    startLocalTimer(remainingSeconds);

    console.log(
      "Восстановлен текущий вопрос:",
      message.question_id,
      "Осталось секунд:",
      remainingSeconds
    );
  } 

  if (message.type === "question_result") {
  console.log("Результат вопроса:", message);

  if (
    String(questionIdRef.current) ===
    String(message.question_id)
  ) {
    setAnswerResult({
      correct_answer: message.correct_answer,
      selected_answer: message.selected_answer,
      is_correct:
        message.selected_answer !== null &&
        String(message.correct_answer) ===
          String(message.selected_answer)
    });
  }
}


    if (message.type === "question_timeout") {
      setTimeLeft(0);

      console.log(
        "Время на вопрос истекло"
      );
    }

    if (message.type === "game_finished") {
      setGameFinished(true);
      setTimeLeft(0);
      setAnswerResult(null);

      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }

      console.log(
        "Игра завершена"
      );

      loadLeaderboard();
    }
  };

  socket.onerror = (error) => {
    if (isUnmounted) {
      return;
    }

    console.error(
      "WebSocket ошибка:",
      error
    );

    setWsStatus(
      "Ошибка подключения"
    );
  };

  socket.onclose = (event) => {
    if (isUnmounted) {
      return;
    }

    console.log(
      "WebSocket отключен",
      event.code,
      event.reason
    );

    setWsStatus("Отключено");
  };

  return () => {
    isUnmounted = true;

    if (
      socket.readyState === WebSocket.CONNECTING ||
      socket.readyState === WebSocket.OPEN
    ) {
      socket.close();
    }
    if (socketRef.current === socket) {
      socketRef.current = null;
    }

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
        {participants.map((participant) => {
          const isConnected = connectedPlayers.some(
            (connectedUserId) =>
              String(connectedUserId).toLowerCase() ===
              String(participant.user_id).toLowerCase()
          );

          return (
            <li key={participant.id}>
              {participant.user_id}
              {" — "}
              {isConnected
                ? "Подключён"
                : "Отключён"}
            </li>
          );
        })}
      </ul>

      {room.status === "waiting" && !gameStarted && !gameFinished && (
        <div>
          <p>
            Ожидание игроков...
          </p>

          <button onClick={handleReady}>
            Я готов
          </button>

          {isHost && (
            <button onClick={handleStartGame}>
              Начать игру
            </button>
          )}
        </div>
      )}
      {gameFinished && (
        <div>
          <h2>Игра завершена!</h2>

          <p>Все вопросы закончились.</p>

          <h3>Итоговая таблица</h3>

          {leaderboard.length === 0 ? (
            <p>Загрузка результатов...</p>
          ) : (
            <table
              border="1"
              cellPadding="8"
              style={{
                borderCollapse: "collapse",
                width: "100%",
                textAlign: "center",
              }}>
              <thead>
                <tr>
                  <th style={{ padding: "12px", minWidth: "80px" }}>
                    Место
                  </th>
                  <th style={{ padding: "12px", minWidth: "160px" }}>
                    Игрок
                  </th>
                  <th style={{ padding: "12px", minWidth: "100px" }}>
                    Баллы
                  </th>
                </tr>
              </thead>
              <tbody>
                {leaderboard.map((participant) => (
                  <tr key={participant.participant_id}>
                    <td style={{ padding: "12px" }}>
                      {participant.place}
                    </td>

                    <td style={{ padding: "12px" }}>
                      {participant.username ||
                        participant.name ||
                        participant.user_name ||
                        participant.user_id}
                    </td>

                    <td style={{ padding: "12px" }}>
                      {participant.score}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

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
          <button className={getAnswerClass(1)}
            onClick={() => handleAnswer(1)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_1}
          </button>
          <button className={getAnswerClass(2)}
            onClick={() => handleAnswer(2)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_2}
          </button>
          <button className={getAnswerClass(3)}
            onClick={() => handleAnswer(3)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_3}
          </button>
          <button className={getAnswerClass(4)}
            onClick={() => handleAnswer(4)}
            disabled={answerResult !== null || timeLeft === 0}>
            {question.answer_4}
          </button>
          
          {answerResult && (
            <div>
              {answerResult.selected_answer === null ? (
                <p>Время вышло. Ответ не выбран.</p>
              ) : (
                <p>Ответ принят.</p>
              )}
            </div>
          )}

          {answerResult && isHost && (
            <div>
              <button onClick={handleNextQuestion}>
                Следующий вопрос
              </button>
            </div>
          )}

        </div>
      )}
    </div>
  );
}

export default Room;