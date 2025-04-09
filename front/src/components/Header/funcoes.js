import { toastr } from '../Utils';

export function btnConsultaCliente(navigate) {
  // toastr['info']('Botão consulta clientes!', 'Mensagem');
  navigate('/consultaClientes');
}

export function btnSair(logout, navigate) {
  logout();
  toastr['info']('Usuário deslogado!', 'Mensagem');
  navigate('/');
}