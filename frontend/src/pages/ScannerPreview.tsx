import { useEffect, useMemo, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { Html5Qrcode } from "html5-qrcode";
import BrandLockup from "@/components/BrandLockup";
import { ApiError, apiGet, apiPost } from "@/lib/api";
import { endSession } from "@/lib/session";
import type { ScanRequest, ScanResponse, ScannerContextResponse, SessionUser } from "@/lib/euphoria";

export default function ScannerPreview() {
  const [eventId, setEventId] = useState("");
  const [dayId, setDayId] = useState("");
  const [gate, setGate] = useState("");
  const [token, setToken] = useState("");
  const [cameraMessage, setCameraMessage] = useState("Camera is off. Manual token and QR image upload are available.");
  const scanner = useRef<Html5Qrcode | null>(null);
  const auth = useQuery({ queryKey: ["session"], queryFn: () => apiGet<SessionUser>("/auth/me"), retry: false });
  const context = useQuery({ queryKey: ["scanner-context"], queryFn: () => apiGet<ScannerContextResponse>("/scanner/context"), enabled: auth.data?.role === "scanner" });
  const selectedEvent = context.data?.events.find((event) => event.id === eventId);
  const days = useMemo(() => selectedEvent?.event_days ?? [], [selectedEvent]);
  const scan = useMutation({ mutationFn: (payload: ScanRequest) => apiPost<ScanResponse>("/scanner/scan", payload) });
  const stopCamera = async () => {
    if (scanner.current?.isScanning) await scanner.current.stop();
    scanner.current?.clear();
    scanner.current = null;
  };
  useEffect(() => () => { void stopCamera(); }, []);
  const verify = (decodedToken = token) => {
    if (!decodedToken.trim() || !eventId || !dayId || !gate) return;
    scan.mutate({ token: decodedToken.trim(), event_id: eventId, event_day_id: dayId, gate });
  };
  const startCamera = async () => {
    if (!eventId || !dayId || !gate) { setCameraMessage("Select event, event day and gate before opening the camera."); return; }
    try {
      await stopCamera();
      const instance = new Html5Qrcode("qr-reader");
      scanner.current = instance;
      await instance.start({ facingMode: "environment" }, { fps: 10, qrbox: { width: 240, height: 240 } }, async (decodedText) => { setToken(decodedText); setCameraMessage("QR detected. Verifying entry…"); await stopCamera(); verify(decodedText); }, () => undefined);
      setCameraMessage("Camera is live. Hold the pass QR inside the frame.");
    } catch {
      setCameraMessage("Camera permission or device access failed. Use QR image upload or paste the manual token.");
    }
  };
  const scanImage = async (file: File) => {
    try {
      await stopCamera();
      const instance = new Html5Qrcode("qr-reader"); scanner.current = instance;
      const decoded = await instance.scanFile(file, true); setToken(decoded); setCameraMessage("QR image decoded. Verifying entry…"); instance.clear(); scanner.current = null; verify(decoded);
    } catch { setCameraMessage("No readable QR was found in that image. Try a clearer image or use the token."); }
  };
  if (auth.isLoading) return <main className="ops-loading">Checking scanner session…</main>;
  if (auth.error instanceof ApiError && auth.error.status === 401) return <Navigate to="/scanner/login" replace />;
  if (auth.data?.role !== "scanner") return <Navigate to="/scanner/login" replace />;
  return <main className="scanner-shell"><header><BrandLockup variant="compact" /><div className="scanner-account"><span data-testid="scanner-user-name">{auth.data.name}</span><button onClick={() => endSession("/scanner/login")} data-testid="scanner-logout-button">Sign out ↗</button></div></header><section><p className="eyebrow accent">AUTHORIZED ENTRY / DATABASE LIVE</p><h1>Ready<br /><em>when you are.</em></h1><p>Select the assigned event, day and gate. Camera scans and manual tokens use the same secure server verification.</p>{context.data?.demo_mode && <p className="scanner-demo-note" data-testid="scanner-demo-mode">DEMO MODE · configured event days can be tested before their calendar date</p>}<div className="scanner-workspace"><div className="scanner-card"><label>Assigned event<select value={eventId} onChange={(e) => { setEventId(e.target.value); setDayId(""); scan.reset(); }} data-testid="scanner-event-select"><option value="">Select assigned event</option>{context.data?.events.map((event) => <option key={event.id} value={event.id} label={event.name} />)}</select></label><label>Event day<select value={dayId} onChange={(e) => { setDayId(e.target.value); scan.reset(); }} disabled={!eventId} data-testid="scanner-day-select"><option value="">Select day</option>{days.map((day) => <option key={day.id} value={day.id} label={`${day.label} · ${day.date}`} />)}</select></label><label>Gate<select value={gate} onChange={(e) => { setGate(e.target.value); scan.reset(); }} data-testid="scanner-gate-select"><option value="">Select gate</option>{context.data?.gates.map((item) => <option key={item} value={item} label={item} />)}</select></label><div className="scanner-camera"><div id="qr-reader" data-testid="scanner-camera-view"></div><p data-testid="scanner-camera-message">{cameraMessage}</p><div className="scanner-camera-actions"><button className="button button-yellow" type="button" onClick={startCamera} data-testid="scanner-camera-button">Open camera</button><label className="button button-ghost file-scan-button">Upload QR image<input type="file" accept="image/*" onChange={(e) => { const file = e.target.files?.[0]; if (file) void scanImage(file); }} data-testid="scanner-image-input" /></label></div></div><label className="scanner-token-label">Manual secure token<input value={token} onChange={(e) => setToken(e.target.value)} placeholder="EUPHORIA-…" data-testid="scanner-token-input" /></label><button className="button button-yellow full" disabled={!token || !eventId || !dayId || !gate || scan.isPending} onClick={() => verify()} data-testid="scanner-submit-button">{scan.isPending ? "Verifying…" : "Verify and record entry ↗"}</button></div><div className={`scanner-result ${scan.data ? `result-${scan.data.status}` : ""}`} data-testid="scanner-result" aria-live="polite">{!scan.data ? <><span className="scan-result-icon">⌁</span><strong>Waiting for a pass</strong><p>Choose the assignment, then scan the participant QR.</p></> : <><span className="scan-result-icon">{scan.data.ok ? "✓" : "!"}</span><p className="eyebrow">{scan.data.status}</p><strong>{scan.data.ok ? "ENTRY ALLOWED" : scan.data.status === "duplicate" ? "ENTRY ALREADY RECORDED" : "ENTRY DENIED"}</strong><p>{scan.data.message}</p>{scan.data.participant && <dl><div><dt>Participant</dt><dd>{scan.data.participant.participant_name}</dd></div><div><dt>Registration</dt><dd>{scan.data.participant.registration_id}</dd></div><div><dt>Event</dt><dd>{scan.data.participant.event_name}</dd></div><div><dt>Payment</dt><dd>{scan.data.participant.payment_status.toUpperCase()}</dd></div><div><dt>Pass</dt><dd>{scan.data.participant.qr_status.toUpperCase()}</dd></div>{scan.data.first_entry_at && <div><dt>First entry</dt><dd>{new Date(scan.data.first_entry_at).toLocaleString("en-IN")}</dd></div>}</dl>}</>}</div></div></section></main>;
}