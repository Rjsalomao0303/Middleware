import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { buscaLogs } from './funcoes';  // Função para buscar os logs
import { toastr } from '../Utils';
import Logo from '../Logo';
import './styles.css';

const ConsultaLogs = () => {
    const [logs, setLogs] = useState([]);
    const [filters, setFilters] = useState({
        dataInicio: '',
        dataFim: '',
        dominio: '',
        numeroContato: '',
        nomePaciente: ''
    });
    const [limit, setLimit] = useState(100);
    const [isFetching, setIsFetching] = useState(false);
    const navigate = useNavigate();
    const containerRef = useRef(null);

    useEffect(() => {
        const fetchLogs = async () => {
            setIsFetching(true);
            try {
                const data = await buscaLogs(filters, limit);
                setLogs(data || []);
            } catch (error) {
                console.error('Erro ao buscar logs:', error);
                toastr.error('Erro ao buscar logs! ' + error.message, 'Erro');
            } finally {
                setIsFetching(false);
            }
        };

        fetchLogs();
    }, [filters, limit]);

    const handleFilterChange = (event) => {
        const { name, value } = event.target;
        setFilters(prevFilters => ({
            ...prevFilters,
            [name]: value
        }));
    };

    const handleLoadMore = () => {
        setLimit(prevLimit => prevLimit + 100);
    };

    return (
        <div className='container'>

            <Logo />

            <div className='corpo-consulta'>

                <div className='container-logs'>

                    {/* Cabeçalho dos Filtros */} 
                    <h2 className='label-filtros'>Filtros de Consulta</h2>

                    <div className='filtro-header'>
                        <input
                            type='date'
                            name='dataInicio'
                            value={filters.dataInicio}
                            onChange={handleFilterChange}
                            className='consulta-input'
                        />
                        <input
                            type='date'
                            name='dataFim'
                            value={filters.dataFim}
                            onChange={handleFilterChange}
                            className='consulta-input'
                        />
                        <input
                            type='text'
                            name='dominio'
                            value={filters.dominio}
                            onChange={handleFilterChange}
                            className='consulta-input'
                            placeholder='Dominio'
                        />
                        <input
                            type='text'
                            name='numeroContato'
                            value={filters.numeroContato}
                            onChange={handleFilterChange}
                            className='consulta-input'
                            placeholder='Número de Contato'
                        />
                        <input
                            type='text'
                            name='nomePaciente'
                            value={filters.nomePaciente}
                            onChange={handleFilterChange}
                            className='consulta-input'
                            placeholder='Nome do Paciente'
                        />
                    </div>
                    
                    {/* Cabeçalho da Consulta */}
                    <h2 className='label-resultados'>Resultado da Consulta</h2>
                    <div className='consulta-header'>
                        <div className='consulta-header-linha'>
                            <span>Paciente</span>
                            <span>Telefone</span>
                            <span>Agendamento</span>
                        </div>
                        <div className='consulta-header-linha'>
                            <span>Tipo</span>
                            <span>Data</span>
                            <span>Confirmado</span>
                            <span>Motivo</span>
                        </div>
                    </div>
                    
                    {/* Lista de Logs */}
                    <div className='consulta-lista'>
                        {logs.length > 0 ? (
                            logs.map(log => (
                                <div key={log.time} className='consulta-item'>
                                    <div className='consulta-item-linha'>
                                        <span>{log.codigo_paciente}-{log.nome_paciente}</span>
                                        <span>{log.numero_contato}</span>
                                        <span>{log.codigo_agendamento}</span>
                                    </div>

                                    {/* time, dominio_omniplus, numero_contato, codigo_paciente, nome_paciente, tipo_agendamento, codigo_agendamento, status, confirmacao */}

                                    <div className='consulta-item-linha'>
                                        <span>{log.tipo_agendamento}</span>
                                        <span>{new Date(log.time).toLocaleString()}</span>
                                        <span>{log.confirmacao}</span>
                                        <span>{log.status}</span>
                                    </div>

                                </div>
                            ))
                        ) : (
                            <p>Nenhum log encontrado.</p>
                        )}
                        {/* {!isFetching && logs.length >= limit && (
                            <button onClick={handleLoadMore} className='load-more'>
                                Carregar mais
                            </button>
                        )} */}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ConsultaLogs;
