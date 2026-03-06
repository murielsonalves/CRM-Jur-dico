import { Card, CardContent, Typography } from "@mui/material";

type Props = { label: string; value: string };

export function DashboardCard({ label, value }: Props) {
  return (
    <Card>
      <CardContent>
        <Typography variant="body2">{label}</Typography>
        <Typography variant="h5">{value}</Typography>
      </CardContent>
    </Card>
  );
}
