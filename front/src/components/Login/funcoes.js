import { toastr } from '../Utils';

const backendUrl = process.env.REACT_APP_BACKEND_URL;

export function verificarLogin(navigate, login) {
  const email = document.getElementById('email').value.toLowerCase();
  const password = document.getElementById('senha').value;

  if (email === '') {
    toastr['warning']('Informe o campo E-mail!', 'Aviso');
    return false;
  }

  if (password === '') {
    toastr['warning']('Informe o campo Senha!', 'Aviso');
    return false;
  }

  // Faz a solicitação HTTP para a rota de login
  fetch(`${backendUrl}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer M@t34200969#H@ndiX3420'
    },
    body: JSON.stringify({
      email: email,
      password: password
    }), // Envia as credenciais do usuário no corpo da solicitação
  })
  .then(async response => {
    // Verifica se a resposta foi bem-sucedida (código HTTP 2xx)
    if (response.ok) {
      const data = await response.json();
      if (data.status === 'success' && data.code === 200) {
        // Se a resposta for bem-sucedida, exibe uma mensagem de sucesso
        toastr['success']('Seja bem vindo ' + data.data.nome + '!', 'Mensagem');
        // Armazena os dados no localStorage
        localStorage.setItem('userId', data.data.id);
        localStorage.setItem('userName', data.data.nome);
        localStorage.setItem('nivel_acesso', data.data.nivel);
        login();
        navigate('/parametrosCliente');
      } else {
        // Se a resposta indicar erro de login
        toastr['warning']('Credenciais inválidas!', 'Aviso');
      }
    } else if (response.status === 404) {
      // Tratar especificamente o erro 404 como "credenciais inválidas"
      toastr['warning']('Nenhum registro encontrado! Verifique suas credenciais.', 'Aviso');
    } else {
      // Se a resposta não for bem-sucedida, trata o erro adequadamente
      console.log('Erro de servidor:', response.status, response.statusText);
      toastr['error']('Erro de servidor! ' + response.status + ' ' + response.statusText, 'Erro');
    }
  })
  .catch(error => {
    // Verifica se houve um erro de rede
    console.log('Erro de rede:', error.message);
    toastr['error']('Erro de rede! ' + error.message, 'Erro');
  });
}
