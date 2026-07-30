import AddIcon from "@mui/icons-material/Add";
import CamerasIcon from "@mui/icons-material/Videocam";
import CompaniesIcon from "@mui/icons-material/Business";
import DashboardIcon from "@mui/icons-material/Dashboard";
import LocationsIcon from "@mui/icons-material/LocationOn";
import RecordersIcon from "@mui/icons-material/Dns";
import RefreshIcon from "@mui/icons-material/Refresh";
import SyncIcon from "@mui/icons-material/Sync";
import DeleteIcon from "@mui/icons-material/Delete";
import {
  Alert, AppBar, Box, Button, Chip, CircularProgress, Dialog, DialogActions, DialogContent,
  DialogTitle, Drawer, IconButton, List, ListItemButton, ListItemIcon, ListItemText, MenuItem,
  Paper, Snackbar, Stack, Table, TableBody, TableCell, TableHead, TableRow, TextField, Toolbar,
  Typography,
} from "@mui/material";
import { FormEvent, ReactNode, useCallback, useEffect, useMemo, useState } from "react";

import { api, Camera, Company, Location, Recorder, snapshotUrl } from "./api";

type View = "dashboard" | "companies" | "locations" | "recorders" | "cameras";
const drawerWidth = 244;

const statusChip = (value: string | null | boolean) => {
  const online = value === "online" || value === true;
  const label = online ? "online" : value === false || value === "offline" ? "offline" : value || "nieznany";
  return <Chip size="small" color={online ? "success" : "default"} label={label} />;
};
const bytes = (value: number | null) => value === null ? "—" : `${(value / 1024 ** 3).toFixed(1)} GB`;

export default function App() {
  const [view, setView] = useState<View>("dashboard");
  const [companies, setCompanies] = useState<Company[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [recorders, setRecorders] = useState<Recorder[]>([]);
  const [cameras, setCameras] = useState<Camera[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dialog, setDialog] = useState<"company" | "location" | "recorder" | null>(null);
  const [snapshot, setSnapshot] = useState<Camera | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Recorder | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [companyData, locationData, recorderData, cameraData] = await Promise.all([
        api<Company[]>("/companies"), api<Location[]>("/locations"), api<Recorder[]>("/recorders"), api<Camera[]>("/cameras"),
      ]);
      setCompanies(companyData); setLocations(locationData); setRecorders(recorderData); setCameras(cameraData);
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Nie udało się pobrać danych."); }
    finally { setLoading(false); }
  }, []);
  useEffect(() => { void load(); }, [load]);

  const action = async (path: string, success: string) => {
    try { await api(path, { method: "POST" }); await load(); setError(success); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Operacja nie powiodła się."); }
  };
  const deleteRecorder = async () => {
    if (!deleteTarget) return;
    try { await api(`/recorders/${deleteTarget.id}`, { method: "DELETE" }); setDeleteTarget(null); await load(); setError("Rejestrator i przypisane kamery zostały usunięte."); }
    catch (cause) { setError(cause instanceof Error ? cause.message : "Nie udało się usunąć rejestratora."); }
  };
  const names = useMemo(() => ({
    company: new Map(companies.map((item) => [item.id, item.name])),
    location: new Map(locations.map((item) => [item.id, item.name])),
    recorder: new Map(recorders.map((item) => [item.id, item.name])),
  }), [companies, locations, recorders]);

  const menu: Array<[View, string, ReactNode]> = [
    ["dashboard", "Pulpit", <DashboardIcon />], ["companies", "Firmy", <CompaniesIcon />],
    ["locations", "Lokalizacje", <LocationsIcon />], ["recorders", "Rejestratory", <RecordersIcon />],
    ["cameras", "Kamery", <CamerasIcon />],
  ];
  const title = menu.find(([key]) => key === view)?.[1] ?? "CAM Manager";

  return <Box sx={{ display: "flex", minHeight: "100vh" }}>
    <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
      <Toolbar><Typography variant="h6" sx={{ fontWeight: 700, letterSpacing: 0.4 }}>CAM Manager</Typography><Box sx={{ flexGrow: 1 }} /><Button color="inherit" startIcon={<RefreshIcon />} onClick={() => void load()}>Odśwież</Button></Toolbar>
    </AppBar>
    <Drawer variant="permanent" sx={{ width: drawerWidth, flexShrink: 0, "& .MuiDrawer-paper": { width: drawerWidth, boxSizing: "border-box" } }}>
      <Toolbar /><List>{menu.map(([key, label, icon]) => <ListItemButton key={key} selected={view === key} onClick={() => setView(key)}><ListItemIcon>{icon}</ListItemIcon><ListItemText primary={label} /></ListItemButton>)}</List>
    </Drawer>
    <Box component="main" sx={{ flexGrow: 1, p: 3, bgcolor: "background.default" }}><Toolbar />
      <Stack direction="row" alignItems="center" justifyContent="space-between" sx={{ mb: 3 }}><Typography variant="h4">{title}</Typography>
        {view !== "dashboard" && view !== "cameras" && <Button variant="contained" startIcon={<AddIcon />} onClick={() => setDialog(view.slice(0, -1) as "company" | "location" | "recorder")}>Dodaj</Button>}
      </Stack>
      {loading ? <Box sx={{ textAlign: "center", py: 10 }}><CircularProgress /></Box> : <Content view={view} companies={companies} locations={locations} recorders={recorders} cameras={cameras} names={names} onRefresh={(id) => void action(`/recorders/${id}/refresh`, "Dane rejestratora odświeżone.")} onSync={(id) => void action(`/recorders/${id}/sync`, "Kamery zostały zsynchronizowane.")} onSnapshot={setSnapshot} onDelete={setDeleteTarget} />}
    </Box>
    <CreateDialog kind={dialog} companies={companies} locations={locations} onClose={() => setDialog(null)} onCreated={() => { setDialog(null); void load(); }} onError={setError} />
    <Dialog open={snapshot !== null} onClose={() => setSnapshot(null)} maxWidth="md" fullWidth><DialogTitle>Snapshot: {snapshot?.name}</DialogTitle><DialogContent>{snapshot && <Box component="img" src={snapshotUrl(snapshot.recorder_id, snapshot.id)} alt={`Snapshot ${snapshot.name}`} sx={{ display: "block", width: "100%" }} />}</DialogContent></Dialog>
    <Dialog open={deleteTarget !== null} onClose={() => setDeleteTarget(null)}><DialogTitle>Usunąć rejestrator?</DialogTitle><DialogContent><Typography>Usunięty zostanie „{deleteTarget?.name}” oraz wszystkie przypisane do niego kamery. Tej operacji nie można cofnąć.</Typography></DialogContent><DialogActions><Button onClick={() => setDeleteTarget(null)}>Anuluj</Button><Button color="error" variant="contained" onClick={() => void deleteRecorder()}>Usuń</Button></DialogActions></Dialog>
    <Snackbar open={error !== null} autoHideDuration={5000} onClose={() => setError(null)}><Alert severity={error?.includes("odświeżone") || error?.includes("zsynchronizowane") ? "success" : "error"} onClose={() => setError(null)}>{error}</Alert></Snackbar>
  </Box>;
}

function Content({ view, companies, locations, recorders, cameras, names, onRefresh, onSync, onSnapshot, onDelete }: { view: View; companies: Company[]; locations: Location[]; recorders: Recorder[]; cameras: Camera[]; names: { company: Map<number, string>; location: Map<number, string>; recorder: Map<number, string> }; onRefresh: (id: number) => void; onSync: (id: number) => void; onSnapshot: (camera: Camera) => void; onDelete: (recorder: Recorder) => void }) {
  if (view === "dashboard") return <Stack direction={{ xs: "column", md: "row" }} spacing={2}>{[["Firmy", companies.length], ["Lokalizacje", locations.length], ["Rejestratory online", recorders.filter((item) => item.status === "online").length], ["Kamery online", cameras.filter((item) => item.online).length]].map(([label, amount]) => <Paper key={String(label)} sx={{ p: 3, flex: 1 }}><Typography color="text.secondary">{label}</Typography><Typography variant="h3">{amount}</Typography></Paper>)}</Stack>;
  if (view === "companies") return <DataTable heads={["Nazwa", "NIP", "Utworzono"]} rows={companies.map((item) => [item.name, item.nip || "—", new Date(item.created_at).toLocaleString("pl-PL")])} />;
  if (view === "locations") return <DataTable heads={["Nazwa", "Firma", "Adres", "Miasto"]} rows={locations.map((item) => [item.name, names.company.get(item.company_id) || item.company_id, item.address || "—", item.city || "—"])} />;
  if (view === "recorders") return <DataTable heads={["Nazwa", "Lokalizacja", "Adres", "Status", "HDD", "Temperatura", "Akcje"]} rows={recorders.map((item) => [item.name, names.location.get(item.location_id) || item.location_id, `${item.ip}:${item.port}`, statusChip(item.status), `${bytes(item.hdd_free_bytes)} / ${bytes(item.hdd_total_bytes)}`, item.temperature_celsius === null ? "—" : `${item.temperature_celsius} °C`, <Stack key={item.id} direction="row"><IconButton title="Odśwież" onClick={() => onRefresh(item.id)}><RefreshIcon /></IconButton><IconButton title="Synchronizuj kamery" onClick={() => onSync(item.id)}><SyncIcon /></IconButton><IconButton title="Usuń rejestrator" color="error" onClick={() => onDelete(item)}><DeleteIcon /></IconButton></Stack>])} />;
  return <DataTable heads={["Kanał", "Nazwa", "Rejestrator", "Adres IP", "Model", "Status", "Snapshot"]} rows={cameras.map((item) => [item.channel, item.name, names.recorder.get(item.recorder_id) || item.recorder_id, item.ip || "—", item.model || "—", statusChip(item.online), <Button key={item.id} size="small" onClick={() => onSnapshot(item)}>Podgląd</Button>])} />;
}

function DataTable({ heads, rows }: { heads: string[]; rows: ReactNode[][] }) { return <Paper sx={{ overflowX: "auto" }}><Table><TableHead><TableRow>{heads.map((head) => <TableCell key={head}>{head}</TableCell>)}</TableRow></TableHead><TableBody>{rows.map((row, index) => <TableRow key={index}>{row.map((cell, cellIndex) => <TableCell key={cellIndex}>{cell}</TableCell>)}</TableRow>)}</TableBody></Table></Paper>; }

function CreateDialog({ kind, companies, locations, onClose, onCreated, onError }: { kind: "company" | "location" | "recorder" | null; companies: Company[]; locations: Location[]; onClose: () => void; onCreated: () => void; onError: (message: string) => void }) {
  const [form, setForm] = useState<Record<string, string>>({});
  useEffect(() => setForm({}), [kind]);
  if (!kind) return null;
  const submit = async (event: FormEvent) => { event.preventDefault(); const body: Record<string, unknown> = { ...form }; if (kind === "location") body.company_id = Number(form.company_id); if (kind === "recorder") { body.location_id = Number(form.location_id); body.port = Number(form.port || 443); body.https = form.https !== "false"; } try { await api(`/${kind}s`, { method: "POST", body: JSON.stringify(body) }); onCreated(); } catch (cause) { onError(cause instanceof Error ? cause.message : "Nie udało się zapisać danych."); } };
  const field = (name: string, label: string, type = "text") => <TextField required={name === "name" || name === "ip" || name === "username" || name === "password"} type={type} label={label} value={form[name] || ""} onChange={(event) => setForm({ ...form, [name]: event.target.value })} fullWidth />;
  return <Dialog open onClose={onClose} fullWidth maxWidth="sm" PaperProps={{ component: "form", onSubmit: submit }}><DialogTitle>Dodaj: {kind === "company" ? "firma" : kind === "location" ? "lokalizacja" : "rejestrator"}</DialogTitle><DialogContent><Stack spacing={2} sx={{ pt: 1 }}>
    {kind === "company" && <>{field("name", "Nazwa firmy")}{field("nip", "NIP")}</>}
    {kind === "location" && <><TextField select required label="Firma" value={form.company_id || ""} onChange={(event) => setForm({ ...form, company_id: event.target.value })}>{companies.map((item) => <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>)}</TextField>{field("name", "Nazwa lokalizacji")}{field("address", "Adres")}{field("city", "Miasto")}</>}
    {kind === "recorder" && <><TextField select required label="Lokalizacja" value={form.location_id || ""} onChange={(event) => setForm({ ...form, location_id: event.target.value })}>{locations.map((item) => <MenuItem key={item.id} value={item.id}>{item.name}</MenuItem>)}</TextField>{field("name", "Nazwa")}{field("ip", "Adres IP")}{field("port", "Port", "number")}{field("username", "Użytkownik")}{field("password", "Hasło", "password")}<TextField select label="Protokół" value={form.https ?? "true"} onChange={(event) => setForm({ ...form, https: event.target.value })}><MenuItem value="true">HTTPS</MenuItem><MenuItem value="false">HTTP</MenuItem></TextField></>}
  </Stack></DialogContent><DialogActions><Button onClick={onClose}>Anuluj</Button><Button type="submit" variant="contained">Zapisz</Button></DialogActions></Dialog>;
}
