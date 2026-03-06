import { Box, Drawer, List, ListItemButton, ListItemText, Toolbar, AppBar, Typography } from "@mui/material";
import { ReactNode } from "react";

const menu = ["Dashboard", "Credores", "Devedores", "Títulos", "Cobrança", "Acordos", "Recebimentos", "Relatórios", "Configurações"];

export function AppLayout({ children }: { children: ReactNode }) {
  return (
    <Box sx={{ display: "flex" }}>
      <AppBar position="fixed"><Toolbar><Typography>CRM Jurídico de Cobrança</Typography></Toolbar></AppBar>
      <Drawer variant="permanent" sx={{ width: 220, [`& .MuiDrawer-paper`]: { width: 220, marginTop: "64px" } }}>
        <List>{menu.map((m) => <ListItemButton key={m}><ListItemText primary={m} /></ListItemButton>)}</List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, marginTop: "64px", marginLeft: "220px" }}>{children}</Box>
    </Box>
  );
}
