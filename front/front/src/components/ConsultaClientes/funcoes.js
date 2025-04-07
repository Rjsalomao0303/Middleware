const backendUrl = process.env.REACT_APP_BACKEND_URL;

export async function buscaClientes() {
    const response = await fetch(`${backendUrl}/consultaClientes`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer M@t34200969#H@ndiX3420'
        }
    });

    const data = await response.json();

    // Verifique se a resposta é um erro (com base na estrutura retornada)
    if (data.status === "error") { // Verifique a propriedade correta
        throw new Error('Erro ao buscar clientes! ' + data.message);
    }

     // Assegure-se de que estamos retornando um array
     return Array.isArray(data.data) ? data.data : []; // Retorna um array ou um array vazio
}