import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <Link to="/">
            <span className="navbar-logo-brain">Brain</span>
            <span className="navbar-logo-plizz">Plizz</span>
          </Link>
        </div>

        <div className="navbar-links">
          <Link className="navbar-link" to="/">
            Главная
          </Link>

          <Link className="navbar-link" to="/login">
            Войти
          </Link>

          <Link className="navbar-link navbar-link-register" to="/register">
            Регистрация
          </Link>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;