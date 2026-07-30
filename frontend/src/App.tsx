import { Box, Container, Typography } from "@mui/material";

export default function App() {
  return (
    <Container maxWidth="md">
      <Box sx={{ py: 8 }}>
        <Typography component="h1" variant="h3">
          CAM Manager
        </Typography>
        <Typography color="text.secondary" sx={{ mt: 2 }}>
          Hikvision device management
        </Typography>
      </Box>
    </Container>
  );
}
