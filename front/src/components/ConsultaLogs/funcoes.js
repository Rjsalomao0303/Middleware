// Handix 
// Dev: Ricardo J. Salomão 06/05/2025 v1.3

const backendUrl = process.env.REACT_APP_BACKEND_URL;

export async function buscaLogs(filters, limit) {

    // Montando a URL com os parâmetros de filtro
    const queryParams = new URLSearchParams({
        dataInicio: filters.dataInicio || '',
        dataFim: filters.dataFim || '',
        dominio: filters.dominio || '',
        agenda: filters.agenda || '',
        numeroContato: filters.numeroContato || '',
        nomePaciente: filters.nomePaciente || '',
        limit: limit || 100
    });

    // Fazendo a requisição com os parâmetros na URL (método GET)
    const response = await fetch(`${backendUrl}/consultaLogs?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer M@t34200969#H@ndiX3420'
        }
    });

    const data = await response.json();

    console.log(data);

    // Verifique se a resposta é um erro (com base na estrutura retornada)
    if (data.status === "error") {
        throw new Error('Erro ao buscar logs! ' + data.message);
    }

    // Assegure-se de que estamos retornando um array
    return Array.isArray(data.data) ? data.data : []; // Retorna um array ou um array vazio
}