// Shourya/src/main.tsx - React 18 DOM entry point mounting the QuantSim ShadCN UI App.
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
