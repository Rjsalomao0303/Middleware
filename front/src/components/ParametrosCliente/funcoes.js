import { toastr } from '../Utils';

const backendUrl = process.env.REACT_APP_BACKEND_URL;

export function salvar(navigate, login, data) {

    // dominio_gesthor
    if (!data.dominio_gesthor) {
        toastr.warning('Necessário informar o dominio do Gesthor!', 'Aviso');
        return;
    }

    // cliente_id_gesthor
    if (!data.cliente_id_gesthor) {
        toastr.warning('Necessário informar o cliente id do Gesthor!', 'Aviso');
        return;
    }

    // token_gesthor
    if (!data.token_gesthor) {
        toastr.warning('Necessário informar o token do Gesthor!', 'Aviso');
        return;
    }

    // hora_manha
    if (!data.hora_manha) {
        toastr.warning('Necessário informar o timer da manhã!', 'Aviso');
        return;
    }

    // hora_tarde
    if (!data.hora_tarde) {
        toastr.warning('Necessário informar o timer da tarde!', 'Aviso');
        return;
    }

    // hora_noite
    if (!data.hora_noite) {
        toastr.warning('Necessário informar o timer da noite!', 'Aviso');
        return;
    }

    // dominio_omniplus
    if (!data.dominio_omniplus) {
        toastr.warning('Necessário informar o dominio do Omniplus!', 'Aviso');
        return;
    }

    // token_omniplus
    if (!data.token_omniplus) {
        toastr.warning('Necessário informar o token do Omniplus!', 'Aviso');
        return;
    }

    // canal_omniplus
    if (!data.canal_omniplus) {
        toastr.warning('Necessário informar o canal do Omniplus!', 'Aviso');
        return;
    }

    // consulta
    if (!data.consulta) {
        toastr.warning('Necessário informar o consulta!', 'Aviso');
        return;
    }

    // exame
    if (!data.exame) {
        toastr.warning('Necessário informar o exame!', 'Aviso');
        return;
    }

    // retorno
    if (!data.retorno) {
        toastr.warning('Necessário informar o retorno!', 'Aviso');
        return;
    }

    // cirurgia
    if (!data.cirurgia) {
        toastr.warning('Necessário informar o cirurgia!', 'Aviso');
        return;
    }

    // dias_consulta
    if (!data.dias_consulta) {
        toastr.warning('Necessário informar o dias_consulta!', 'Aviso');
        return;
    }

    // dias_exame
    if (!data.dias_exame) {
        toastr.warning('Necessário informar o dias_exame!', 'Aviso');
        return;
    }

    // dias_retorno
    if (!data.dias_retorno) {
        toastr.warning('Necessário informar o dias_retorno!', 'Aviso');
        return;
    }

    // dias_cirurgia
    if (!data.dias_cirurgia) {
        toastr.warning('Necessário informar o dias_cirurgia!', 'Aviso');
        return;
    }

    // Faz a solicitação HTTP para a rota de login
    fetch(`${backendUrl}/parametros`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer M@t34200969#H@ndiX3420'
        },
        body: JSON.stringify(data),
    })
        .then(async response => {
            // Verifica se a resposta foi bem-sucedida (código HTTP 2xx)
            if (response.ok) {
                const data = await response.json();
                if (data.status === 'success' && data.code === 200) {
                    // Se a resposta for bem-sucedida, exibe uma mensagem de sucesso
                    toastr['success']('Registro salvo!', 'Mensagem');
                    navigate('/parametrosCliente');
                } else {
                    // Se a resposta indicar erro de login
                    toastr['warning']('Não foi possivel gravar o registro!', 'Aviso');
                }
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