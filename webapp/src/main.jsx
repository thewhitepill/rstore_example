import React from "react";
import { createRoot } from "react-dom/client";

import { createApiClient } from "./api-client";
import App from "./App";
import { createRequest } from "./request";

const apiClient = createApiClient(
  createRequest({ baseUrl: "http://localhost:3000" })
);

const root = createRoot(document.getElementById("app"));

root.render(
  <React.StrictMode>
    <App apiClient={apiClient} />
  </React.StrictMode>
);
