import { useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import { validarEmail } from '../Utils';
import { InputPassword } from '../Input-Password';
import { verificarLogin } from './funcoes';

import Logo from '../Logo';

import '../Label/styles.css';
import '../Input-Text/styles.css';
import '../Button/styles.css';
import './styles.css';

const Login = () => {
    const navigate = useNavigate();
    const { login } = useContext(AuthContext);

    const handleLogar = (event) => {
      event.preventDefault();
      verificarLogin(navigate, login);
    };

    return (
      <div className='container'>

        <Logo />
        
        <div className='corpo'>

          <input type='text' id='email' className='input-text' onBlur={() => validarEmail()} required></input>
          <label htmlFor='email' className='input-label'>Email</label>

          <InputPassword id='senha' className='input-text' required/>

          <div className='btnLogar'>
            <button className='button' onClick={handleLogar}>Logar</button>
          </div>

        </div>

      </div>
    );
}

export default Login;