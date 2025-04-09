import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { buscaLogs } from './funcoes'; // Função para buscar os logs
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

  const formatDataForCSV = () => {
    if (!logs || logs.length === 0) {
      return "";
    }

    const headers = Object.keys(logs[0]).join(',');
    const rows = logs.map(log => Object.values(log).join(',')).join('\n');

    return `${headers}\n${rows}`;
  };

  const downloadCSV = () => {
    const csvData = formatDataForCSV();
    if (!csvData) {
      toastr.warning("Nenhum dado para exportar.", "Aviso");
      return;
    }

    const filename = 'logs_consulta.csv';
    const blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });

    if (navigator.msSaveBlob) { // IE e Edge
      navigator.msSaveBlob(blob, filename);
    } else {
      const link = document.createElement("a");
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
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

          {/* Cabeçalho da Consulta e Botão de Exportação */}
          <div className='resultados-header'>
            <h2 className='label-resultados'>Resultado da Consulta</h2>
            <button onClick={downloadCSV} className='button'>Exportar CSV</button>
          </div>

          {/* Lista de Logs */}
          <div className='consulta-lista'>
            {logs.length > 0 ? (
              <table>
                <thead>
                  <tr>
                    <th style={{ width: '30%', textAlign: 'left' }}>Paciente</th>
                    <th style={{ width: '15%', textAlign: 'center' }}>Telefone</th>
                    <th style={{ width: '10%', textAlign: 'center' }}>Agendamento</th>
                    <th style={{ width: '10%', textAlign: 'left' }}>Tipo</th>
                    <th style={{ width: '15%', textAlign: 'center' }}>Data/Hora</th>
                    <th style={{ width: '10%', textAlign: 'center' }}>Confirmado</th>
                    <th style={{ width: '10%', textAlign: 'left' }}>Motivo</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map(log => (
                    <tr key={log.time}>
                      <td style={{ textAlign: 'left' }}>{log.codigo_paciente}-{log.nome_paciente}</td>
                      <td style={{ textAlign: 'center' }}>{log.numero_contato_formatado}</td>
                      <td style={{ textAlign: 'center' }}>{log.codigo_agendamento}</td>
                      <td style={{ textAlign: 'left' }}>{log.tipo_agendamento}-{log.descricao_tipo_agendamento}</td>
                      <td style={{ textAlign: 'center' }}>{log.time_formatado}</td>
                      <td style={{ textAlign: 'center' }}>{log.status}-{log.confirmacao}</td>
                      <td style={{ textAlign: 'left' }}>{log.descricao_status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p>Nenhum log encontrado.</p>
            )}
          </div>

          {logs.length > 0 && !isFetching && (
            <div className='load-more'>
              <button onClick={handleLoadMore} className='button'>Carregar Mais</button>
            </div>
          )}

          {isFetching && <p>Carregando logs...</p>}
        </div>
      </div>
    </div>
  );
};

export default ConsultaLogs;