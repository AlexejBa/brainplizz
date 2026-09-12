import { Link } from "react-router-dom";

function Home() {
  return (
    <main className="home-page">
      <h1>BrainPlizz</h1>

      <p>
        Онлайн-игра, в которой можно соревноваться
        с другими игроками в интеллектуальной викторине.
      </p>

      <div className="home-actions">
        <Link to="/login">Войти в игру</Link>

        <Link to="/register">Создать аккаунт</Link>
      </div>
    </main>
  );
}

export default Home;