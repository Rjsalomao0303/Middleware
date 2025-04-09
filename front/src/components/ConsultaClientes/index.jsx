import React, { useState, useEffect, useContext, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import GlobalStateContext from '../Context/GlobalStateContext';
import { buscaClientes } from './funcoes';
import { toastr } from '../Utils';

import fechar from '../../img/saida.png';
import './styles.css';

const ConsultaClientes = () => {
    const [clientes, setClientes] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    const [limit, setLimit] = useState(50);  // Inicialmente, vamos buscar 50 clientes
    const [isFetching, setIsFetching] = useState(false); // Estado para controle de carregamento

    const navigate = useNavigate();
    const { setState } = useContext(GlobalStateContext);
    const containerRef = useRef(null);

    useEffect(() => {
        const fetchClientes = async () => {
            setIsFetching(true);  // Inicia o estado de carregamento
            try {
                const data = await buscaClientes(limit);  // Busca os clientes com o limite definido
                setClientes(data || []);
            } catch (error) {
                console.error('Erro ao buscar clientes:', error);
                toastr.error('Erro ao buscar clientes! ' + error.message, 'Erro');
            } finally {
                setIsFetching(false);  // Finaliza o estado de carregamento
            }
        };

        fetchClientes();
    }, [limit]);  // Reexecuta a busca quando o limite mudar

    const handleSearchChange = (event) => {
        setSearchTerm(event.target.value);
    };

    const handleClienteClick = (cliente) => {
        navigate('/parametrosCliente', { state: cliente });
        setState('showConsultaCliente', false);
    };

    const handleClickOutside = useCallback((event) => {
        if (containerRef.current && !containerRef.current.contains(event.target)) {
            navigate('/parametrosCliente');
            setState('showConsultaCliente', false);
        }
    }, [navigate, setState]);

    useEffect(() => {
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [handleClickOutside]);

    const closeConsultaCliente = () => {
        navigate('/parametrosCliente');
        setState('showConsultaCliente', false);
    };

    const filteredClientes = Array.isArray(clientes) ? clientes.filter(cliente =>
        cliente.dominio_gesthor?.toLowerCase().includes(searchTerm.toLowerCase())
    ) : [];

    const handleLoadMore = () => {
        setLimit(prevLimit => prevLimit + 50);  // Carrega mais 50 clientes ao clicar
    };

    return (
        <div className='consulta-overlay'>
            <div className='consulta-container' ref={containerRef}>
                <button className='close-button' onClick={closeConsultaCliente}>
                    <img id="img-fechar" src={fechar} className="img-fechar" alt="Fecha Consulta" />
                </button>
                <input
                    type='text'
                    placeholder='Buscar cliente...'
                    value={searchTerm}
                    onChange={handleSearchChange}
                    className='consulta-input'
                />
                <div className='consulta-lista'>
                    {filteredClientes.length > 0 ? (
                        filteredClientes.map(cliente => (
                            <div
                                key={cliente.dominio_gesthor}
                                className='consulta-item'
                                onClick={() => handleClienteClick(cliente)}
                            >
                                <div className='consulta-item-linha'>
                                    <span>Dominio: {cliente.dominio_gesthor}</span>
                                </div>
                            </div>
                        ))
                    ) : (
                        <p>Nenhum cliente encontrado.</p>
                    )}
                    {!isFetching && filteredClientes.length >= 50 && (
                        <button onClick={handleLoadMore} className='load-more'>
                            Carregar mais
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ConsultaClientes;
