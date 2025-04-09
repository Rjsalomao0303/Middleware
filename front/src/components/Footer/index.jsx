import './styles.css';

const Footer = () => {
   
    const anoAtual = new Date().getFullYear(); // Obtém o ano atual

    return (
        <footer className="container-footer">
            <a href="http://www.handix.com.br" target="_blank" style={{ color: 'white' }} rel="noreferrer">
                Handix Copyright © 2024 - Todos os direitos reservados {anoAtual} v1.2
            </a>
        </footer>
    );
}

export default Footer;