function Home() {
  return (
    <main className="home-page">
      <h1>BrainPlizz</h1>

      <p>
        Онлайн-игра, в которой можно соревноваться
        с другими игроками в интеллектуальной викторине.
      </p>

      <div className="home-actions">
        <a href="/login">Войти в игру</a>
        <a href="/register">Создать аккаунт</a>
      </div>
    </main>
  );
}

export default Home;