import toastr from 'toastr';

import 'toastr/build/toastr.css'; // Importa os estilos padrão do Toastr

import './styles.css';

// Configuração global do Toastr
toastr.options = {
    closeButton: true,
    progressBar: true,
    positionClass: 'toast-custom-top-right', // Posição dos Toasts (top-right, top-left, bottom-right, bottom-left)
    preventDuplicates: true,
    showDuration: 300,
    hideDuration: 1000,
    timeOut: 1500, // Tempo de exibição de cada Toast (em milissegundos)
    extendedTimeOut: 1000, // Tempo de exibição extra para mensagens com progressBar (em milissegundos)
}; 


// Aplicar a máscara de telefone usando a biblioteca inputmask
function formatarTelefone(input) {
    // Remove todos os caracteres não numéricos
    var numTelefone = input.value.replace(/\D/g, '');

    // Verifica o comprimento do número de telefone para determinar a formatação
    if (numTelefone.length <= 10) {
        input.value = '(' + numTelefone.substring(0, 2) + ') ' + numTelefone.substring(2, 6) + '-' + numTelefone.substring(6, 10);
    } else if (numTelefone.length > 10) {
        input.value = '(' + numTelefone.substring(0, 2) + ') ' + numTelefone.substring(2, 7) + '-' + numTelefone.substring(7, 11);
    }
}

function apenasNumeros(event) {
    var charCode = (event.which) ? event.which : event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        event.preventDefault();
    }
    return true;
}

function formatarNumero(input) {
    // Remove todos os caracteres não numéricos
    var valorNumerico = input.value.replace(/\D/g, '');

    // Formata o valor com ponto para separar milhares e vírgula para separar decimais
    var valorFormatado = (parseFloat(valorNumerico) / 100).toLocaleString('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });

    // Atualiza o valor do campo com o valor formatado
    input.value = valorFormatado;
}

function formatarNumeroInteiro(input) {
    // Remove todos os caracteres não numéricos
    var valorFormatado = input.value.replace(/\D/g, '');

    // Atualiza o valor do campo
    input.value = valorFormatado;
}

function validarEmail() {
    var emailInput = document.getElementById('email');
    var email = emailInput.value;

    // Expressão regular para verificar se o e-mail tem um formato válido
    var regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (!regex.test(email)) {
        toastr['warning']('E-mail inválido!', 'Aviso');
        emailInput.value = "";
    }
}

function formataDate(isoDateString) {
    if (!isoDateString){
        return;
    }
    const date = new Date(isoDateString);
    
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-based
    const year = date.getFullYear();
    
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    const seconds = String(date.getSeconds()).padStart(2, '0');

    return `${day}/${month}/${year} ${hours}:${minutes}:${seconds}`;
}

function formataValor(value) {
    if (!value){
        return;
    }
    return value.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' });
}

function formataValorReal(value) {
    if (!value) {
        return;
    }
    return new Intl.NumberFormat('pt-BR', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(value);
}

export {toastr, formatarTelefone, apenasNumeros, formatarNumero, formatarNumeroInteiro, validarEmail, formataDate, formataValor, formataValorReal}