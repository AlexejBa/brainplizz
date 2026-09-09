import { Link } from "react-router-dom";

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-logo">
        <Link to="/">BrainPlizz</Link>
      </div>

      <div className="navbar-links">
        <Link to="/">Главная</Link>
        <Link to="/login">Войти</Link>
        <Link to="/register">Регистрация</Link>
      </div>
    </nav>
  );
}

export default Navbar;