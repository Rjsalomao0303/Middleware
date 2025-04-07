import React, { useContext } from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Footer from './components/Footer';
import Menu from './components/Menu';
import Login from './components/Login';
import ParametrosCliente from './components/ParametrosCliente';
import ConsultaClientes from './components/ConsultaClientes';
import ConsultaLogs from './components/ConsultaLogs';
import { AuthProvider } from './components/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { GlobalStateProvider } from './components/Context/GlobalStateContext';

import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <GlobalStateProvider>
    <React.StrictMode>
      <AuthProvider>
        <Router>
          <Header />
          <Menu />
          <Routes>
            <Route path="/" element={<Login />} exact />

            {/* Rota para acesso à página de cadastro de parametros do cliente */}
            <Route path="/parametrosCliente" element={<ProtectedRoute element={<ParametrosCliente />} />} exact />

            {/* Rota para acesso à página de consulta de clientes com parametros */}
            <Route path="/consultaClientes" element={<ProtectedRoute element={<ConsultaClientes />} />} exact />

            {/* Rota para acesso à página de consulta de logs */}
            <Route path="/consultaLogs" element={<ProtectedRoute element={<ConsultaLogs />} />} exact />
            
          </Routes>
          <Footer />
        </Router>
      </AuthProvider>
    </React.StrictMode>
  </GlobalStateProvider>
);