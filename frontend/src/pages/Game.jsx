import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { getMe, createRoom } from "../services/api";

function Game() {
  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [creatingRoom, setCreatingRoom] = useState(false);

  const [error, setError] = useState("");

  useEffect(() => {
    async function checkAuth() {
      const token = localStorage.getItem("access_token");

      if (!token) {
        navigate("/login");
        return;
      }

      try {
        const data = await getMe();

        setUser(data);
      } catch (error) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("user_id");
        navigate("/login");
      } finally {
        setLoading(false);
      }
    }

    checkAuth();
  }, [navigate]);

  async function handleCreateRoom() {
    setError("");
    setCreatingRoom(true);

    try {
      const room = await createRoom(4);

      console.log("Создана комната:", room);

      navigate(`/room/${room.id}`);

    } catch (error) {
      setError(error.message);

    } finally {
      setCreatingRoom(false);
    }
  }

  if (loading) {
    return <p>Проверка авторизации...</p>;
  }

  return (
    <div>
      <h1>BrainPlizz</h1>

      <h2>Игровая комната</h2>

      <p>
        Добро пожаловать, {user.username}!
      </p>

      <button
        onClick={handleCreateRoom}
        disabled={creatingRoom}
      >
        {creatingRoom
          ? "Создание..."
          : "Создать комнату"}
      </button>
      <button
      onClick={() => navigate("/join")}  
> 
      Присоединиться к комнате
      </button>

      {error && (
        <p>{error}</p>
      )}
    </div>
  );
}

export default Game;