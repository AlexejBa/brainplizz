import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { login, getMe } from "../services/api";

function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    console.log("HANDLE SUBMIT ЗАПУСТИЛСЯ");

    setError("");
    setLoading(true);

    try {
      const data = await login(email, password);
      console.log("LOGIN УСПЕШНО ЗАВЕРШИЛСЯ", data);
      localStorage.setItem(
        "access_token",
        data.access_token
      );

      console.log("ТОКЕН СОХРАНЕН");

      const user = await getMe();
      console.log("GET ME УСПЕШНО ЗАВЕРШИЛСЯ", user);
      localStorage.setItem(
        "user_id",
        user.id
      );

      alert("Вы успешно вошли!")

      navigate("/game");

    } catch (error) {
      setError(error.message);

    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-page">

      <h1>BrainPlizz</h1>

      <h2>Вход</h2>

      <form onSubmit={handleSubmit}>

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(event) =>
            setEmail(event.target.value)
          }
          required
        />

        <input
          type="password"
          placeholder="Пароль"
          value={password}
          onChange={(event) =>
            setPassword(event.target.value)
          }
          required
        />

        {error && (
          <p>{error}</p>
        )}

        <button
          type="submit"
          disabled={loading}
        >
          {loading ? "Вход..." : "Войти"}
        </button>

      </form>

    </div>
  );
}

export default Login;