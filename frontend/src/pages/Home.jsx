import { Link } from "react-router-dom";

function Home() {
  return (
    <main className="home-page">
      <div className="home-content">
        <div className="home-badge">
          🧠 МНОГОПОЛЬЗОВАТЕЛЬСКАЯ ВИКТОРИНА
        </div>

        <h1 className="home-title">
          Думай.
          <span> Играй.</span>
          <strong> Побеждай!</strong>
        </h1>

        <p className="home-description">
          Онлайн-игра, в которой можно соревноваться
          с другими игроками в интеллектуальной викторине.
        </p>

        <div className="home-actions">
          <Link
            className="home-button home-button-primary"
            to="/login"
          >
            Войти в игру
          </Link>

          <Link
            className="home-button home-button-secondary"
            to="/register"
          >
            Создать аккаунт
          </Link>
        </div>

        <div className="home-features">
          <div className="home-feature">
            <span className="home-feature-icon">👥</span>

            <div>
              <h3>Игра с друзьями</h3>
              <p>Создавай комнаты и приглашай игроков</p>
            </div>
          </div>

          <div className="home-feature">
            <span className="home-feature-icon">⚡</span>

            <div>
              <h3>В реальном времени</h3>
              <p>Вопросы, таймер и ответы синхронизированы</p>
            </div>
          </div>

          <div className="home-feature">
            <span className="home-feature-icon">🏆</span>

            <div>
              <h3>Соревнование</h3>
              <p>Получай очки и поднимайся в рейтинге</p>
            </div>
          </div>
        </div>
      </div>

      <div className="home-visual">
        <div className="home-glow home-glow-purple"></div>
        <div className="home-glow home-glow-orange"></div>

        <div className="home-brain-card">
          <div className="home-brain-icon">🧠</div>

          <div className="home-lightning">⚡</div>

          <div className="home-card-title">
            Brain<span>Plizz</span>
          </div>

          <p>Думай • Играй • Побеждай!</p>
        </div>

        <div className="home-floating-card home-floating-card-top">
          <span>?</span>
          <div>
            <strong>Тысячи вопросов</strong>
            <small>Разные категории</small>
          </div>
        </div>

        <div className="home-floating-card home-floating-card-bottom">
          <span>🏆</span>
          <div>
            <strong>Набирай очки</strong>
            <small>Попади в топ игроков</small>
          </div>
        </div>
      </div>
    </main>
  );
}

export default Home;