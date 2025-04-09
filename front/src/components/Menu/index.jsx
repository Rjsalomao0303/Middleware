import { useContext, useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import menu from '../../img/menu-bar.png';
import { AuthContext } from '../AuthContext'; // Importa o contexto de autenticação
import './styles.css';

const Menu = () => {

  const { isAuthenticated, logout } = useContext(AuthContext); // Usa o contexto de autenticação

  const [isOpen, setIsOpen] = useState(false);
  const menuRef = useRef(null);
  // const nivel_acesso = localStorage.getItem('nivel_acesso');

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  const closeMenu = () => {
    setIsOpen(false);
  };

  useEffect(() => {

    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        closeMenu();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [menuRef]);

  if (!isAuthenticated) return null; // Se não estiver autenticado, retorna null

  return (
    <>
      <button className="menu-toggle" onClick={toggleMenu}>
        <img id="img-menu-bar" src={menu} className="img-menu-bar" alt="Menu" />
      </button>

      <div ref={menuRef} className={`sidebar ${isOpen ? 'open' : ''}`}>
        <nav>
          <Link to="/parametrosCliente" onClick={closeMenu}>Parametros</Link>
          <Link to="/consultaLogs" onClick={closeMenu}>Logs</Link>
          <Link to="/" onClick={() => { logout(); closeMenu(); }}>Sair</Link>
        </nav>
      </div>
    </>
  );

}

export default Menu;