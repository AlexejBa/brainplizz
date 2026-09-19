import {
  useCallback,
  useEffect,
  useRef,
  useState
} from "react";
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
  const [questionNumber, setQuestionNumber] = useState(null);
  const [totalQuestions, setTotalQuestions] = useState(null);
  const questionIdRef = useRef(null);
  const socketRef = useRef(null);
  const [answerResult, setAnswerResult] = useState(null);
  const [answerSubmitted, setAnswerSubmitted] = useState(false);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [timeLeft, setTimeLeft] = useState(null);
  const timerRef = useRef(null);

  const [currentParticipant, setCurrentParticipant] =
    useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [wsStatus, setWsStatus] = useState(
    currentUserId
      ? "Подключение..."
      : "Ошибка: пользователь не авторизован"
  );

  const isHost = room?.host_id === currentUserId;

  function getAnswerClass(answerNumber) {
    if (!answerResult) {
      return "";
    }

    const correctAnswer =
      Number(answerResult.correct_answer);

    const selectedAnswer =
      Number(answerResult.selected_answer);

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

  const loadLeaderboard = useCallback(
    async () => {
      try {
        const data = await getLeaderboard(roomId);

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
    },
    [roomId]
  );

  const loadRoom = useCallback(
    async () => {
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
        console.error(
          "Ошибка загрузки комнаты:",
          error
        );

        setError(
          error.message ||
          "Ошибка загрузки комнаты"
        );
      }
    },
    [roomId, loadLeaderboard]
  );

  const loadParticipants = useCallback(
    async () => {
      try {
        const data =
          await getRoomParticipants(roomId);

        const userId =
          localStorage.getItem("user_id");

        const currentUserParticipant =
          data.find(
            (participant) =>
              participant.user_id === userId
          );

        setCurrentParticipant(
          currentUserParticipant
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
    },
    [roomId]
  );

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
      setSelectedAnswer(selectedAnswer);

      const answeredQuestionId =
        question.id;

      await submitAnswer(
        currentParticipant.id,
        answeredQuestionId,
        selectedAnswer
      );

      if (
        String(questionIdRef.current) ===
        String(answeredQuestionId)
      ) {
        setAnswerSubmitted(true);
      }
    } catch (error) {
      console.error(
        "Ошибка отправки ответа:",
        error
      );

      setError(
        error?.message ||
        String(error) ||
        "Не удалось отправить ответ"
      );
    }
  }

  async function handleNextQuestion() {
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
        socketRef.current.readyState !==
          WebSocket.OPEN
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
      return;
    }

    async function initializeRoom() {
      await Promise.all([
        loadRoom(),
        loadParticipants()
      ]);
    }

    initializeRoom();
  }, [
    roomId,
    loadRoom,
    loadParticipants
  ]);

  useEffect(() => {
    if (!questionId) {
      return;
    }

    async function loadQuestion() {
      try {
        const data =
          await getQuestion(roomId);

        setQuestion(data);
      } catch (error) {
        console.error(
          "Ошибка загрузки вопроса:",
          error
        );

        setError(
          error.message ||
          "Ошибка загрузки вопроса"
        );
      }
    }

    loadQuestion();
  }, [questionId, roomId]);

  useEffect(() => {
    if (!roomId || !currentUserId) {
      return;
    }

    let isUnmounted = false;

    const socket = new WebSocket(
      `ws://127.0.0.1:8000/ws/rooms/${roomId}?user_id=${currentUserId}`
    );

    socketRef.current = socket;

    socket.onopen = () => {
      if (isUnmounted) {
        return;
      }

      setWsStatus("Подключено");
    };

    socket.onmessage = (event) => {
      if (isUnmounted) {
        return;
      }

      const message =
        JSON.parse(event.data);

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

      if (message.type === "ready_updated") {
        loadParticipants();
      }

      if (
        message.type ===
        "presence_updated"
      ) {
        setConnectedPlayers(
          message.connected_user_ids || []
        );
      }

      if (message.type === "game_started") {
        setGameStarted(true);
        setGameFinished(false);
        setQuestion(null);
        setQuestionId(
          message.question_id
        );

        questionIdRef.current =
          message.question_id;

        setQuestionNumber(
          message.question_number
        );

        setTotalQuestions(
          message.total_questions
        );

        setAnswerResult(null);
        setAnswerSubmitted(false);
        setSelectedAnswer(null);
        setTimeLeft(null);
      }

      if (message.type === "next_question") {
        setQuestion(null);
        setQuestionId(
          message.question_id
        );

        questionIdRef.current =
          message.question_id;

        setQuestionNumber(
          message.question_number
        );

        setTotalQuestions(
          message.total_questions
        );

        setAnswerResult(null);
        setAnswerSubmitted(false);
        setSelectedAnswer(null);
        setTimeLeft(null);
      }

      if (
        message.type ===
        "current_question"
      ) {
        setGameStarted(true);
        setGameFinished(false);
        setQuestion(null);
        setQuestionId(
          message.question_id
        );

        questionIdRef.current =
          message.question_id;

        setQuestionNumber(
          message.question_number
        );

        setTotalQuestions(
          message.total_questions
        );

        setAnswerSubmitted(
          message.selected_answer !== null &&
          message.selected_answer !== undefined
        );

        setSelectedAnswer(
          message.selected_answer ?? null
        );

        if (message.question_finished) {
          setAnswerResult({
            correct_answer:
              message.correct_answer,
            selected_answer:
              message.selected_answer,
            is_correct:
              message.selected_answer !== null &&
              String(
                message.correct_answer
              ) ===
                String(
                  message.selected_answer
                )
          });
        } else {
          setAnswerResult(null);
        }

        const remainingSeconds =
          message.remaining_seconds ?? 30;

        setTimeLeft(
          remainingSeconds
        );
      }

      if (
        message.type ===
        "timer_update"
      ) {
        if (
          String(questionIdRef.current) ===
          String(message.question_id)
        ) {
          setTimeLeft(
            Math.max(
              0,
              Number(
                message.remaining_seconds
              )
            )
          );
        }
      }

      if (
        message.type ===
        "question_result"
      ) {
        if (
          String(questionIdRef.current) ===
          String(message.question_id)
        ) {
          if (timerRef.current) {
            clearInterval(
              timerRef.current
            );

            timerRef.current = null;
          }

          setAnswerResult({
            correct_answer:
              message.correct_answer,
            selected_answer:
              message.selected_answer,
            is_correct:
              message.selected_answer !== null &&
              String(
                message.correct_answer
              ) ===
                String(
                  message.selected_answer
                )
          });
        }
      }

      if (
        message.type ===
        "question_timeout"
      ) {
        setTimeLeft(0);
      }

      if (
        message.type ===
        "game_finished"
      ) {
        setGameFinished(true);
        setTimeLeft(0);
        setAnswerResult(null);

        if (timerRef.current) {
          clearInterval(
            timerRef.current
          );

          timerRef.current = null;
        }

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

    socket.onclose = () => {
      if (isUnmounted) {
        return;
      }

      setWsStatus("Отключено");
    };

    return () => {
      isUnmounted = true;

      if (
        socket.readyState ===
          WebSocket.CONNECTING ||
        socket.readyState ===
          WebSocket.OPEN
      ) {
        socket.close();
      }

      if (
        socketRef.current === socket
      ) {
        socketRef.current = null;
      }

      if (timerRef.current) {
        clearInterval(
          timerRef.current
        );

        timerRef.current = null;
      }
    };
  }, [
    roomId,
    currentUserId,
    loadParticipants,
    loadLeaderboard
  ]);

  if (loading) {
    return (
      <div>
        <h1>BrainPlizz</h1>
        <p>Загрузка комнаты...</p>
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
    <main className="room-page">
      <div className="room-container">

        <section className="room-header">
          <div>
            <div className="room-badge">
              🎮 ИГРОВАЯ КОМНАТА
            </div>
            <h1 className="room-title">
              Комната ({room.code})
            </h1>
          </div>

          <div
            className={`room-connection-status ${
              wsStatus === "Подключено"
                ? "room-connection-online"
                : ""
            }`}
          >
            <span className="room-status-dot"></span>
            {wsStatus}
          </div>
        </section>

        {error && (
          <div className="room-error">
            <span>⚠</span>
            <p>{error}</p>
          </div>
        )}

        {!gameStarted && !gameFinished && (
          <section className="room-layout">

            <div className="room-main-card">

              <div className="room-code-section">
                <p className="room-label">
                  КОД КОМНАТЫ
                </p>

                <div className="room-code">
                  {room.code}
                </div>

                <p className="room-code-hint">
                  Передайте этот код игрокам,
                  чтобы они могли присоединиться
                </p>
              </div>

              <div className="room-divider"></div>

              <div className="room-players-header">
                <div>
                  <h2>Игроки</h2>
                </div>

                <div className="room-player-count">
                  {participants.length}
                  <span>
                    / {room.max_players}
                  </span>
                </div>
              </div>

              <div className="room-players-list">
                {participants.map(
                  (participant, index) => {
                    const isConnected =
                      connectedPlayers.some(
                        (connectedUserId) =>
                          String(
                            connectedUserId
                          ).toLowerCase() ===
                          String(
                            participant.user_id
                          ).toLowerCase()
                      );

                    const isCurrentUser =
                      String(
                        participant.user_id
                      ).toLowerCase() ===
                      String(
                        currentUserId
                      ).toLowerCase();

                    const isParticipantHost =
                      String(
                        participant.user_id
                      ).toLowerCase() ===
                      String(
                        room.host_id
                      ).toLowerCase();

                    return (
                      <div
                        className="room-player"
                        key={participant.id}
                      >
                        <div className="room-player-number">
                          {index + 1}
                        </div>

                        <div className="room-player-avatar">
                          {participant.username
                            ?.slice(0, 1)
                            .toUpperCase()}
                        </div>

                        <div className="room-player-info">
                          <div className="room-player-name">
                            {participant.username}

                            {isCurrentUser && (
                              <span className="room-player-you">
                                Вы
                              </span>
                            )}

                            {isParticipantHost && (
                              <span className="room-player-host">
                                👑
                              </span>
                            )}
                          </div>

                          <div className="room-player-status">
                            <span
                              className={`room-status-dot ${
                                participant.is_ready
                                  ? "room-status-dot-online"
                                  : "room-status-dot-offline"
                              }`}
                            ></span>

                            {participant.is_ready
                              ? "Готов"
                              : "Не готов"}
                          </div>

                          <div className="room-player-status">
                            <span
                              className={`room-status-dot ${
                                isConnected
                                  ? "room-status-dot-online"
                                  : "room-status-dot-offline"
                              }`}
                            ></span>

                            {isConnected
                              ? "Подключён"
                              : "Отключён"}
                          </div>
                        </div>
                      </div>
                    );
                  }
                )}
              </div>

              {room.status === "waiting" &&
                !gameStarted &&
                !gameFinished && (
                  <div className="room-waiting">

                    <div className="room-waiting-icon">
                      ⏳
                    </div>

                    <div className="room-waiting-text">
                      <h3>
                        Ожидание игроков
                      </h3>

                      <p>
                        Когда все будут готовы,
                        ведущий сможет начать игру.
                      </p>
                    </div>
                  </div>
                )}

              {room.status === "waiting" &&
                !gameStarted &&
                !gameFinished && (
                  <div className="room-actions">

                    <button
                      className="room-button room-button-secondary"
                      onClick={handleReady}
                    >
                      {currentParticipant?.is_ready
                        ? "Я не готов"
                        : "✓ Я готов"}
                    </button>

                    {isHost && (
                      <button
                        className="room-button room-button-primary"
                        onClick={handleStartGame}
                      >
                        Начать игру
                        <span>→</span>
                      </button>
                    )}
                  </div>
                )}

            </div>

            <aside className="room-side-card">

              <div className="room-side-glow"></div>

              <div className="room-side-icon">
                🧠
              </div>

              <h2>
                Готовы сыграть?
              </h2>

              <p>
                Соберите команду, выберите
                ответы и узнайте, кто окажется
                самым быстрым и внимательным.
              </p>

              <div className="room-side-features">
                <div>
                  <span>⚡</span>
                  <p>В реальном времени</p>
                </div>

                <div>
                  <span>⏱</span>
                  <p>30 секунд на вопрос</p>
                </div>

                <div>
                  <span>🏆</span>
                  <p>Итоговый рейтинг</p>
                </div>
              </div>

            </aside>

          </section>
        )}

        {gameFinished && (
          <section className="game-finished-card">
            <div className="game-finished-icon">
              🏆
            </div>

            <h2>Игра завершена!</h2>

            <p>
              Все вопросы закончились.
            </p>

            <h3>Итоговая таблица</h3>

            {leaderboard.length === 0 ? (
              <p>Загрузка результатов...</p>
            ) : (
              <table className="leaderboard-table">
                <thead>
                  <tr>
                    <th>Место</th>
                    <th>Игрок</th>
                    <th>Баллы</th>
                  </tr>
                </thead>

                <tbody>
                  {leaderboard.map(
                    (participant) => (
                      <tr
                        key={
                          participant.participant_id
                        }
                      >
                        <td>
                          {participant.place}
                        </td>

                        <td>
                          {participant.username ||
                            participant.name ||
                            participant.user_name ||
                            participant.user_id}
                        </td>

                        <td>
                          {participant.score}
                        </td>
                      </tr>
                    )
                  )}
                </tbody>
              </table>
            )}

            <p className="game-finished-thanks">
              Спасибо за участие!
            </p>
          </section>
        )}

        {gameStarted &&
          question &&
          !gameFinished && (
            <section className="game-question-card">

              <div className="game-question-header">
                <div>
                  <div className="game-question-label">
                    ВОПРОС {questionNumber}/{totalQuestions}
                  </div>
                </div>

                <div
                  className={`game-timer ${
                    timeLeft !== null &&
                    timeLeft <= 5
                      ? "game-timer-critical"
                      : timeLeft !== null &&
                          timeLeft <= 15
                        ? "game-timer-warning"
                        : ""
                  }`}
                >
                  <span className="game-timer-icon">
                    ⏱
                  </span>

                  <div>
                    <strong>
                      {timeLeft ?? 0}
                    </strong>

                    <small>
                      секунд
                    </small>
                  </div>
                </div>
              </div>

              <div className="game-question-progress">
                <div
                  className={`game-question-progress-bar ${
                    timeLeft !== null &&
                    timeLeft <= 5
                      ? "progress-critical"
                      : timeLeft !== null &&
                          timeLeft <= 15
                        ? "progress-warning"
                        : ""
                  }`}
                  style={{
                    width: `${Math.max(
                      0,
                      Math.min(
                        100,
                        ((timeLeft ?? 0) /
                          30) *
                          100
                      )
                    )}%`,
                  }}
                ></div>
              </div>

              <h1 className="game-question-text">
                {question.text}
              </h1>

              <div className="game-answers">

                <button
                  className={`game-answer ${
                    selectedAnswer === 1
                      ? "answer-selected"
                      : ""
                  } ${getAnswerClass(1)}`}
                  onClick={() =>
                    handleAnswer(1)
                  }
                  disabled={
                    answerSubmitted ||
                    answerResult !== null ||
                    timeLeft === 0
                  }
                >
                  <span className="game-answer-letter">
                    A
                  </span>

                  <span className="game-answer-text">
                    {question.answer_1}
                  </span>
                </button>

                <button
                  className={`game-answer ${
                    selectedAnswer === 2
                      ? "answer-selected"
                      : ""
                  } ${getAnswerClass(2)}`}
                  onClick={() =>
                    handleAnswer(2)
                  }
                  disabled={
                    answerSubmitted ||
                    answerResult !== null ||
                    timeLeft === 0
                  }
                >
                  <span className="game-answer-letter">
                    B
                  </span>

                  <span className="game-answer-text">
                    {question.answer_2}
                  </span>
                </button>

                <button
                  className={`game-answer ${
                    selectedAnswer === 3
                      ? "answer-selected"
                      : ""
                  } ${getAnswerClass(3)}`}
                  onClick={() =>
                    handleAnswer(3)
                  }
                  disabled={
                    answerSubmitted ||
                    answerResult !== null ||
                    timeLeft === 0
                  }
                >
                  <span className="game-answer-letter">
                    C
                  </span>

                  <span className="game-answer-text">
                    {question.answer_3}
                  </span>
                </button>

                <button
                  className={`game-answer ${
                    selectedAnswer === 4
                      ? "answer-selected"
                      : ""
                  } ${getAnswerClass(4)}`}
                  onClick={() =>
                    handleAnswer(4)
                  }
                  disabled={
                    answerSubmitted ||
                    answerResult !== null ||
                    timeLeft === 0
                  }
                >
                  <span className="game-answer-letter">
                    D
                  </span>

                  <span className="game-answer-text">
                    {question.answer_4}
                  </span>
                </button>

              </div>

              {answerSubmitted &&
                !answerResult && (
                  <div className="game-answer-result">
                    <span className="game-result-icon">
                      ✓
                    </span>

                    <div>
                      <strong>
                        Ответ принят
                      </strong>

                      <p>
                        Ждём остальных игроков...
                      </p>
                    </div>
                  </div>
                )}

              {answerResult && (
                <div
                  className={`game-answer-result ${
                    answerResult.selected_answer ===
                    null
                      ? "result-timeout"
                      : answerResult.is_correct
                        ? "result-correct"
                        : "result-wrong"
                  }`}
                >
                  {answerResult.selected_answer ===
                  null ? (
                    <>
                      <span className="game-result-icon">
                        ⏰
                      </span>

                      <div>
                        <strong>
                          Время вышло
                        </strong>

                        <p>
                          Ответ не был выбран.
                        </p>
                      </div>
                    </>
                  ) : (
                    <>
                      <span className="game-result-icon">
                        ✓
                      </span>

                      <div>
                        <strong>
                          Ответ принят
                        </strong>

                        <p>
                          Результат вопроса показан на экране.
                        </p>
                      </div>
                    </>
                  )}
                </div>
              )}

              {answerResult &&
                isHost && (
                  <div className="game-next-question">

                    <p>
                      Вопрос завершён. Ведущий может
                      перейти дальше.
                    </p>

                    <button
                      className="room-button room-button-primary"
                      onClick={
                        handleNextQuestion
                      }
                    >
                      {questionNumber ===
                      totalQuestions
                        ? "Закончить игру"
                        : "Следующий вопрос"}
                      <span>→</span>
                    </button>

                  </div>
                )}

            </section>
          )}
      </div>
    </main>
  );
}

export default Room;