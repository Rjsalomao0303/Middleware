import React, { useState } from 'react';
import visivelImg from '../../img/visivel.png';
import invisivelImg from '../../img/invisivel.png';

import './styles.css';


export function InputPassword() {
  const [showPassword, setShowPassword] = useState(false);

  const togglePasswordVisibility = (event) => {
    event.preventDefault();
    setShowPassword(!showPassword);
  };

  return (
    <form>
      <div className='input-password-container'>
        <input type={showPassword ? 'text' : 'password'} id='senha' className='input-text' autoComplete='new-password'/>
        <label htmlFor='senha' className='input-label-senha'>Senha</label>
        <button className='btnVisible' onClick={togglePasswordVisibility}>
          <img className='visivelImg' src={showPassword ? invisivelImg : visivelImg} alt={showPassword ? 'Ocultar Senha' : 'Mostrar Senha'} />
        </button>
      </div>
    </form>
  );
}
