export type Company = { id: number; name: string; nip: string | null; created_at: string };
export type Location = { id: number; company_id: number; name: string; address: string | null; city: string | null };
export type Recorder = {
  id: number; location_id: number; name: string; model: string | null; serial: string | null;
  firmware: string | null; ip: string; port: number; username: string; https: boolean;
  last_seen: string | null; status: string | null; hdd_status: string | null;
  hdd_total_bytes: number | null; hdd_free_bytes: number | null; temperature_celsius: number | null;
};
export type Camera = {
  id: number; recorder_id: number; channel: number; name: string; model: string | null;
  serial: string | null; ip: string | null; mac: string | null; firmware: string | null;
  online: boolean; last_snapshot: string | null; status: string | null;
};

const apiBase = import.meta.env.VITE_API_BASE_URL ?? "/api";

export async function api<T>(path: string, options: RequestInit = {}): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options.headers },
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Błąd API (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export const snapshotUrl = (recorderId: number, cameraId: number) =>
  `${apiBase}/recorders/${recorderId}/cameras/${cameraId}/snapshot?ts=${Date.now()}`;
