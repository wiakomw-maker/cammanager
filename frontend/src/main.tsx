import { CssBaseline, ThemeProvider, createTheme } from "@mui/material";
import { createRoot } from "react-dom/client";

import App from "./App";

const theme = createTheme({ palette: { mode: "dark" } });

createRoot(document.getElementById("root")!).render(
  <ThemeProvider theme={theme}>
    <CssBaseline />
    <App />
  </ThemeProvider>,
);
