import { useMutation } from "@tanstack/react-query";
import { Link, useNavigate } from "react-router-dom";
import BrandLockup from "@/components/BrandLockup";
import { apiPost } from "@/lib/api";
import { beginSession } from "@/lib/session";
import type { LoginRequest, SessionUser } from "@/lib/euphoria";

interface PortalLoginProps {
  portal: "admin" | "scanner";
}

export default function PortalLogin({ portal }: PortalLoginProps) {
  const navigate = useNavigate();
  const login = useMutation({
    mutationFn: (payload: LoginRequest) => apiPost<SessionUser>(`/auth/${portal}/login`, payload),
    onSuccess: () => {
      beginSession();
      navigate(`/${portal}`);
    },
  });
  return <main className="portal-login-shell">
    <section className="portal-login-brand"><Link to="/"><BrandLockup variant="compact" /></Link><p className="eyebrow accent">SECURE OPERATIONS</p><h1>{portal === "admin" ? "Build the\nprogramme." : "Control the\ngate."}</h1><p>{portal === "admin" ? "Create events, set pricing and monitor registrations from one connected dashboard." : "Validate paid QR passes and record one entry per configured event day."}</p></section>
    <form className="portal-login-card" data-testid={`${portal}-login-form`} onSubmit={(event) => { event.preventDefault(); const data = new FormData(event.currentTarget); login.mutate({ email: String(data.get("email")), password: String(data.get("password")) }); }}>
      <span className="eyebrow">{portal.toUpperCase()} LOGIN</span><h2>Authorized access</h2>
      <label>Email address<input name="email" type="email" required autoComplete="username" data-testid={`${portal}-email-input`} /></label>
      <label>Password<input name="password" type="password" required autoComplete="current-password" data-testid={`${portal}-password-input`} /></label>
      {login.isError && <p className="form-error" data-testid={`${portal}-login-error`}>Email or password is incorrect for this portal.</p>}
      <button className="button button-yellow full" type="submit" disabled={login.isPending} data-testid={`${portal}-login-submit`}>{login.isPending ? "Signing in…" : `Sign in to ${portal} ↗`}</button>
      <Link to="/" className="text-link">← Return to public site</Link>
    </form>
  </main>;
}