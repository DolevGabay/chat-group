import React from 'react';
import { BrowserRouter, Route, Routes } from "react-router-dom";
import Connect from './Connect';
import Chat from './Chat';

function App() {
  return (
        <div>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<Connect />} />
              <Route path="/chat" element={<Chat />} />
            </Routes>
          </BrowserRouter>
        </div>
  );
}

export default App;
