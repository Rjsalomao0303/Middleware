import React, { createContext, useState } from 'react';

const GlobalStateContext = createContext();

export const GlobalStateProvider = ({ children }) => {
  const [globalState, setGlobalState] = useState({
    token: null,
    // showBuscaCliente: false,
    // showLinkCadastro: false,
    // showConsultaCliente: false,
  });


  const setState = (key, value) => { setGlobalState((prevState) => ({ ...prevState, [key]: value })); };

  const resetState = () => {
    setGlobalState({
      // showBuscaCliente: false,
      // showLinkCadastro: false,
      // showConsultaCliente: false,
    });
  };

  return (
    <GlobalStateContext.Provider value={{ globalState, setState, resetState }}>
      {children}
    </GlobalStateContext.Provider>
  );
};

export default GlobalStateContext;
