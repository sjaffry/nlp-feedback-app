import React from 'react';
import ReactDOM from 'react-dom/client';
import 'semantic-ui-css/semantic.min.css'
import './index.css';
import App from './App';
import TextInput from './TextInput';
import { Amplify } from 'aws-amplify';
import config from './aws-exports';
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";

document.title = 'Feedback app';

Amplify.configure(config);

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Router>
      <Routes>
        <Route path="/TextInput" element={<TextInput />} />
        <Route path="/" element={<App />} />
      </Routes>
    </Router>
  </React.StrictMode>
);
