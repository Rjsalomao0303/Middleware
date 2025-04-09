import { useContext } from 'react';
import GlobalStateContext from '../Context/GlobalStateContext';
import { useNavigate } from 'react-router-dom';
import { btnConsultaCliente, btnSair } from './funcoes';
import { AuthContext } from '../AuthContext';

import './styles.css';

import linkConsultaClientes from '../../img/cadastro.png';
import sair from '../../img/saida.png';

const Header = () => {

  const { isAuthenticated, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const { globalState, setState } = useContext(GlobalStateContext);

  const eventConsultaClientes = (event) => {
    event.preventDefault();
    setState('showConsultaCliente', true);
    btnConsultaCliente(navigate);
  };

  const eventSair = (event) => {
    event.preventDefault();
    btnSair(logout, navigate);
  };

  const showConsultaCliente = globalState.showConsultaCliente || true;

  if (!isAuthenticated) return null;

  return (
    <div className="principal-header">

      <div className="container-buscas">

        <button className="link-cadastro" onClick={eventConsultaClientes} style={{ display: showConsultaCliente ? 'block' : 'none' }}>
          <img id="img-link-cadastro" src={linkConsultaClientes} className="img-link-cadastro" alt="Consulta Cliente" />
        </button>

      </div>

      <button className="saida-bar" onClick={eventSair}>
        <img id="img-saida-bar" src={sair} className="img-saida-bar" alt="Sair" />
      </button>

    </div>
  );

}

export default Header;