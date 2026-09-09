import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { joinRoom } from "../services/api";

function JoinRoom() {
  const navigate = useNavigate();

  const [code, setCode] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setError("");
    setLoading(true);

    try {
      const participant = await joinRoom(code);

      console.log("Участник добавлен:", participant);

      navigate(`/room/${participant.room_id}`);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h1>BrainPlizz</h1>

      <h2>Присоединиться к комнате</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Код комнаты"
          value={code}
          onChange={(event) =>
            setCode(event.target.value.toUpperCase())
          }
          maxLength={6}
          required
        />

        {error && (
          <p>{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
        >
          {loading
            ? "Подключение..."
            : "Присоединиться"}
        </button>
      </form>
    </div>
  );
}

export default JoinRoom;