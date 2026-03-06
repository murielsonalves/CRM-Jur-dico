import { Grid, Typography } from "@mui/material";
import { DashboardCard } from "../components/DashboardCard";

export function DashboardPage() {
  return (
    <>
      <Typography variant="h4" gutterBottom>Dashboard Financeiro</Typography>
      <Grid container spacing={2}>
        <Grid item xs={3}><DashboardCard label="Carteira Total" value="R$ 4.250.000,00" /></Grid>
        <Grid item xs={3}><DashboardCard label="Valor Recuperado" value="R$ 1.730.000,00" /></Grid>
        <Grid item xs={3}><DashboardCard label="Em Aberto" value="R$ 2.520.000,00" /></Grid>
        <Grid item xs={3}><DashboardCard label="Taxa de Recuperação" value="40,7%" /></Grid>
      </Grid>
    </>
  );
}
