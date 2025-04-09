import { useContext, useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import GlobalStateContext from '../Context/GlobalStateContext';
import { salvar } from './funcoes';
import ConsultaClientes from '../ConsultaClientes';
import Logo from '../Logo';

import '../Label/styles.css';
import '../Input-Text/styles.css';
import '../Button/styles.css';
import '../Select/styles.css';
import './styles.css';

const Cliente = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useContext(AuthContext);
  const { setState, resetState, globalState } = useContext(GlobalStateContext);

  const [initialSetupDone, setInitialSetupDone] = useState(false);

  const cliente = location.state;

  const handleSalvar = (event) => {
    event.preventDefault();

    // Wait for async actions to complete
    setTimeout(() => {
      const data = {
        dominio_gesthor: document.getElementById('dominio_gesthor').value,
        cliente_id_gesthor: document.getElementById('cliente_id_gesthor').value,
        token_gesthor: document.getElementById('token_gesthor').value,
        hora_manha: document.getElementById('hora_manha').value,
        hora_tarde: document.getElementById('hora_tarde').value,
        hora_noite: document.getElementById('hora_noite').value,
        dominio_omniplus: document.getElementById('dominio_omniplus').value,
        token_omniplus: document.getElementById('token_omniplus').value,
        canal_omniplus: document.getElementById('canal_omniplus').value,
        consulta: document.getElementById('consulta').value,
        exame: document.getElementById('exame').value,
        retorno: document.getElementById('retorno').value,
        cirurgia: document.getElementById('cirurgia').value,
        dias_consulta: document.getElementById('dias_consulta').value,
        dias_exame: document.getElementById('dias_exame').value,
        dias_retorno: document.getElementById('dias_retorno').value,
        dias_cirurgia: document.getElementById('dias_cirurgia').value,
        ativo: document.getElementById('ativo').value
      };
      salvar(navigate, login, data);
    }, 1000);
  };

  useEffect(() => {
    if (!initialSetupDone) {
      // console.log("Initial setup running");
      setState('showBuscaClientes', true);
      setInitialSetupDone(true);
    }
  }, [initialSetupDone, setState, resetState]);

  return (
    <div className='container'>
      <Logo />
      <div className='corpo'>

        <div className='container-gesthor'>

          <h2 className='label-gesthor'>Parametros Gesthor</h2>
          
          <select id='ativo' className='select' defaultValue={cliente?.ativo || 'sim'} required>
            <option value='sim'>Sim</option>
            <option value='nao'>Não</option>
          </select>
          <label htmlFor='ativo' className='input-label'>Ativo</label>
          
          <input type='text' id='dominio_gesthor' className='input-text' defaultValue={cliente?.dominio_gesthor || ''} required></input>
          <label htmlFor='dominio_gesthor' className='input-label'>Dominio Gesthor:</label>

          <input type='text' id='cliente_id_gesthor' className='input-text' defaultValue={cliente?.cliente_id_gesthor || ''} required></input>
          <label htmlFor='cliente_id_gesthor' className='input-label'>Cliente ID Gesthor:</label>

          <input type='text' id='token_gesthor' className='input-text' defaultValue={cliente?.bearer_gesthor || ''} required></input>
          <label htmlFor='token_gesthor' className='input-label'>Token Gesthor:</label>


          <div className='container-gesthor-horarios'>

            <h2 className='label-gesthor-horarios'>Horários</h2>

            <input type='text' id='hora_manha' className='input-text' defaultValue={cliente?.hora_manha || ''} required></input>
            <label htmlFor='hora_manha' className='input-label'>Timer da manhã:</label>

            <input type='text' id='hora_tarde' className='input-text' defaultValue={cliente?.hora_tarde || ''} required></input>
            <label htmlFor='hora_tarde' className='input-label'>Timer da tarde:</label>

            <input type='text' id='hora_noite' className='input-text' defaultValue={cliente?.hora_noite || ''} required></input>
            <label htmlFor='hora_noite' className='input-label'>Timer da noite:</label>

          </div>

        </div>

        <div className='container-omniplus'>

          <h2 className='label-omniplus'>Parametros Omniplus</h2>

          <input type='text' id='dominio_omniplus' className='input-text' defaultValue={cliente?.dominio_omniplus || ''} required></input>
          <label htmlFor='dominio_omniplus' className='input-label'>Dominio Omniplus:</label>

          <input type='text' id='token_omniplus' className='input-text' defaultValue={cliente?.bearer_omniplus || ''} required></input>
          <label htmlFor='token_omniplus' className='input-label'>Token Omniplus:</label>

          <input type='text' id='canal_omniplus' className='input-text' defaultValue={cliente?.canal_omniplus || ''} required></input>
          <label htmlFor='canal_omniplus' className='input-label'>Canal Omniplus:</label>


          <div className='container-omniplus-templates'>

            <div className='container-omniplus-templates-tipos'>

              <input type='text' id='consulta' className='input-text' defaultValue={cliente?.template_consulta || ''} required></input>
              <label htmlFor='consulta' className='input-label'>Template consulta:</label>

              <input type='text' id='exame' className='input-text' defaultValue={cliente?.template_exame || ''} required></input>
              <label htmlFor='exame' className='input-label'>Template exame:</label>

              <input type='text' id='retorno' className='input-text' defaultValue={cliente?.template_retorno || ''} required></input>
              <label htmlFor='retorno' className='input-label'>Template retorno:</label>

              <input type='text' id='cirurgia' className='input-text' defaultValue={cliente?.template_cirurgia || ''} required></input>
              <label htmlFor='cirurgia' className='input-label'>Template cirurgia:</label>

            </div>

            <div className='container-omniplus-templates-dias'>

              <input type='text' id='dias_consulta' className='input-text' defaultValue={cliente?.dias_consulta || ''} required></input>
              <label htmlFor='dias_consulta' className='input-label'>Dias p/ consulta:</label>

              <input type='text' id='dias_exame' className='input-text' defaultValue={cliente?.dias_exame || ''} required></input>
              <label htmlFor='dias_exame' className='input-label'>Dias p/ exame:</label>

              <input type='text' id='dias_retorno' className='input-text' defaultValue={cliente?.dias_retorno || ''} required></input>
              <label htmlFor='dias_retorno' className='input-label'>Dias p/ retorno:</label>

              <input type='text' id='dias_cirurgia' className='input-text' defaultValue={cliente?.dias_cirurgia || ''} required></input>
              <label htmlFor='dias_cirurgia' className='input-label'>Dias p/ cirurgia:</label>

            </div>

          </div>

        </div>

        <div className='btnSalvar'>
          <button className='button' onClick={handleSalvar}>Salvar</button>
        </div>

      </div>
      {globalState.showConsultaClientes && <ConsultaClientes />}
    </div>
  );
}

export default Cliente;