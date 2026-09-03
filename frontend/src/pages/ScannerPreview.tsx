import { useEffect, useRef, useState } from "react";
import { useMutation, useQuery } from "@tanstack/react-query";
import { Navigate } from "react-router-dom";
import { Html5Qrcode } from "html5-qrcode";
import BrandLockup from "@/components/BrandLockup";
import { ApiError, apiGet, apiPost } from "@/lib/api";
import { endSession } from "@/lib/session";
import type { ScanRequest, ScanResponse, ScannerContextResponse, SessionUser } from "@/lib/euphoria";

export default function ScannerPreview() {
  const [token, setToken] = useState("");
  const [cameraMessage, setCameraMessage] = useState("Camera is off. Open it and point directly at any EUPHORIA QR pass.");
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [torchOn, setTorchOn] = useState(false);
  const scanner = useRef<Html5Qrcode | null>(null);
  const cameraTrack = useRef<MediaStreamTrack | null>(null);
  const auth = useQuery({ queryKey: ["session"], queryFn: () => apiGet<SessionUser>("/auth/me"), retry: false });
  const context = useQuery({ queryKey: ["scanner-context"], queryFn: () => apiGet<ScannerContextResponse>("/scanner/context"), enabled: auth.data?.role === "scanner" });
  const scan = useMutation({ mutationFn: (payload: ScanRequest) => apiPost<ScanResponse>("/scanner/scan", payload) });

  const stopCamera = async () => {
    if (scanner.current?.isScanning) await scanner.current.stop();
    scanner.current?.clear();
    scanner.current = null;
    cameraTrack.current = null;
    setTorchOn(false);
  };
  useEffect(() => () => { void stopCamera(); }, []);

  const verify = (decodedToken = token) => {
    if (!decodedToken.trim()) return;
    scan.mutate({ token: decodedToken.trim() });
  };

  const startCamera = async () => {
    try {
      scan.reset();
      await stopCamera();
      const instance = new Html5Qrcode("qr-reader");
      scanner.current = instance;
      await instance.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 240, height: 240 } },
        async (decodedText) => {
          setToken(decodedText);
          setCameraMessage("QR detected. Event and today's entry are being verified…");
          await stopCamera();
          verify(decodedText);
        },
        () => undefined,
      );
      const video = document.querySelector("#qr-reader video") as HTMLVideoElement | null;
      cameraTrack.current = (video?.srcObject as MediaStream | null)?.getVideoTracks()[0] ?? null;
      setCameraMessage("Camera is live. Hold any EUPHORIA pass QR inside the frame.");
    } catch {
      setCameraMessage("Camera permission or device access failed. Upload the QR image or paste its secure token.");
    }
  };

  const scanImage = async (file: File) => {
    try {
      scan.reset();
      await stopCamera();
      const instance = new Html5Qrcode("qr-reader");
      scanner.current = instance;
      const decoded = await instance.scanFile(file, true);
      setToken(decoded);
      setCameraMessage("QR image decoded. Verifying today's entry…");
      instance.clear();
      scanner.current = null;
      verify(decoded);
    } catch {
      setCameraMessage("No readable QR was found. Try a clearer image or use the secure token.");
    }
  };

  const playTone = (ok: boolean) => {
    if (!soundEnabled) return;
    const audio = new AudioContext();
    const oscillator = audio.createOscillator();
    const gain = audio.createGain();
    oscillator.frequency.value = ok ? 880 : 220;
    gain.gain.value = 0.08;
    oscillator.connect(gain);
    gain.connect(audio.destination);
    oscillator.start();
    oscillator.stop(audio.currentTime + (ok ? 0.16 : 0.3));
  };
  useEffect(() => {
    if (!scan.data) return;
    playTone(scan.data.ok);
    navigator.vibrate?.(scan.data.ok ? [100] : [180, 80, 180]);
  }, [scan.data]);

  const toggleTorch = async () => {
    const track = cameraTrack.current;
    if (!track) { setCameraMessage("Open the camera before using the torch."); return; }
    const capabilities = track.getCapabilities() as MediaTrackCapabilities & { torch?: boolean };
    if (!capabilities.torch) { setCameraMessage("This camera does not expose torch control."); return; }
    const next = !torchOn;
    await track.applyConstraints({ advanced: [{ torch: next } as MediaTrackConstraintSet] });
    setTorchOn(next);
  };
  const openFullscreen = async () => { if (!document.fullscreenElement) await document.documentElement.requestFullscreen(); else await document.exitFullscreen(); };

  if (auth.isLoading) return <main className="ops-loading" data-testid="scanner-session-loading">Checking scanner session…</main>;
  if (auth.error instanceof ApiError && auth.error.status === 401) return <Navigate to="/scanner/login" replace />;
  if (auth.data?.role !== "scanner") return <Navigate to="/scanner/login" replace />;

  return <main className="scanner-shell">
    <header><BrandLockup variant="compact" /><div className="scanner-account"><span data-testid="scanner-user-name">{auth.data.name}</span><button onClick={() => endSession("/scanner/login")} data-testid="scanner-logout-button">Sign out ↗</button></div></header>
    <section>
      <div className="scanner-title-row"><div><p className="eyebrow accent" data-testid="scanner-mode-label">AUTO EVENT ENTRY / DATABASE LIVE</p><h1>Scan.<br /><em>That's it.</em></h1></div><div className="scanner-utility"><button onClick={() => setSoundEnabled(!soundEnabled)} data-testid="scanner-sound-button">Sound {soundEnabled ? "on" : "off"}</button><button onClick={toggleTorch} data-testid="scanner-torch-button">Torch {torchOn ? "on" : "off"}</button><button onClick={openFullscreen} data-testid="scanner-fullscreen-button">Fullscreen</button></div></div>
      <p data-testid="scanner-auto-instructions">{context.data?.instructions ?? "Scan any pass. Event and today's eligible event day are detected automatically."}</p>
      <div className="scanner-auto-status" data-testid="scanner-server-date"><span>SERVER DATE</span><strong>{context.data?.server_date ?? "Checking…"}</strong><small>No event, day or gate selection required</small></div>
      {context.data?.demo_mode && <p className="scanner-demo-note" data-testid="scanner-demo-mode">DEMO MODE · the next unused configured event day is selected automatically</p>}
      <div className="scanner-workspace">
        <div className="scanner-card scanner-card-auto">
          <div className="scanner-camera"><div id="qr-reader" data-testid="scanner-camera-view"></div><p data-testid="scanner-camera-message">{cameraMessage}</p><div className="scanner-camera-actions"><button className="button button-yellow" type="button" onClick={startCamera} data-testid="scanner-camera-button">Open camera & scan</button><label className="button button-ghost file-scan-button">Upload QR image<input type="file" accept="image/*" onChange={(event) => { const file = event.target.files?.[0]; if (file) void scanImage(file); }} data-testid="scanner-image-input" /></label></div></div>
          <label className="scanner-token-label">Manual secure token<input value={token} onChange={(event) => setToken(event.target.value)} placeholder="EUPHORIA-…" data-testid="scanner-token-input" /></label>
          <button className="button button-yellow full" disabled={!token || scan.isPending} onClick={() => verify()} data-testid="scanner-submit-button">{scan.isPending ? "Verifying…" : "Verify and record today's entry ↗"}</button>
        </div>
        <div className={`scanner-result ${scan.data ? `result-${scan.data.status}` : ""}`} data-testid="scanner-result" aria-live="polite">
          {!scan.data ? <><span className="scan-result-icon">⌁</span><strong>Waiting for a pass</strong><p>Open the camera and scan. Event and day routing happen automatically.</p></> : <><span className="scan-result-icon">{scan.data.ok ? "✓" : "!"}</span><p className="eyebrow" data-testid="scanner-result-status">{scan.data.status}</p><strong>{scan.data.ok ? "ENTRY ALLOWED" : scan.data.status === "duplicate" ? "ENTRY ALREADY RECORDED" : "ENTRY DENIED"}</strong><p data-testid="scanner-result-message">{scan.data.message}</p>{scan.data.participant && <dl data-testid="scanner-participant-details"><div><dt>Participant</dt><dd>{scan.data.participant.participant_name}</dd></div><div><dt>Registration</dt><dd>{scan.data.participant.registration_id}</dd></div><div><dt>Event</dt><dd>{scan.data.participant.event_name}</dd></div><div><dt>Event day</dt><dd>{scan.data.participant.event_day_label ?? "—"} · {scan.data.participant.event_day_date ?? "—"}</dd></div><div><dt>Institute</dt><dd>{scan.data.participant.college}</dd></div><div><dt>Mobile</dt><dd>{scan.data.participant.mobile}</dd></div><div><dt>Email</dt><dd>{scan.data.participant.email}</dd></div><div><dt>Payment / pass</dt><dd>{scan.data.participant.payment_status.toUpperCase()} / {scan.data.participant.qr_status.toUpperCase()}</dd></div>{scan.data.first_entry_at && <div><dt>First entry</dt><dd>{new Date(scan.data.first_entry_at).toLocaleString("en-IN")}</dd></div>}</dl>}</>}
        </div>
      </div>
    </section>
  </main>;
}