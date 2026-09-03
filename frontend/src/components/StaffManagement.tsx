import { useMutation, useQuery } from "@tanstack/react-query";
import { apiGet, apiPost, apiPut } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import type { AdminStaffResponse, StaffRow } from "@/lib/euphoria";

export default function StaffManagement() {
  const staff = useQuery({ queryKey: ["admin-staff"], queryFn: () => apiGet<AdminStaffResponse>("/admin/staff") });
  const create = useMutation({
    mutationFn: (payload: { name: string; email: string; password: string; role: "scanner" }) => apiPost<StaffRow>("/admin/staff", payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-staff"] }),
  });
  const update = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: { name: string; role: "scanner"; is_active: boolean; password: null } }) => apiPut<StaffRow>(`/admin/staff/${id}`, payload),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["admin-staff"] }),
  });
  const scanners = staff.data?.data.filter((user) => user.role === "scanner") ?? [];

  return <section id="staff" className="ops-panel" data-testid="scanner-user-management">
    <div className="ops-panel-heading"><div><p className="eyebrow accent">SIMPLE SCANNER ACCESS</p><h2>Scanner users</h2><p className="ops-panel-copy" data-testid="scanner-access-rule">Every active scanner account can scan every event. Name the account after the event coordinator for easy management.</p></div><span>{scanners.length} accounts</span></div>
    <div className="ops-management-grid scanner-management-grid">
      <form className="ops-subpanel" data-testid="scanner-user-create-form" onSubmit={(event) => { event.preventDefault(); const form = event.currentTarget; const data = new FormData(form); create.mutate({ name: String(data.get("name")), email: String(data.get("email")), password: String(data.get("password")), role: "scanner" }, { onSuccess: () => form.reset() }); }}>
        <p className="eyebrow">CREATE SCANNER LOGIN</p>
        <label>Coordinator / scanner name<input name="name" required data-testid="scanner-user-name-input" /></label>
        <label>Login email<input name="email" type="email" required data-testid="scanner-user-email-input" /></label>
        <label>Temporary password<input name="password" type="password" minLength={12} required data-testid="scanner-user-password-input" /></label>
        <button className="button button-yellow" type="submit" disabled={create.isPending} data-testid="scanner-user-create-button">{create.isPending ? "Creating…" : "Create scanner login"}</button>
        {create.isSuccess && <p className="ops-success" data-testid="scanner-user-create-success">Scanner login created. It can scan every event automatically.</p>}
        {create.isError && <p className="form-error" data-testid="scanner-user-create-error">Could not create scanner. Check the unique email and 12-character password.</p>}
      </form>
      <div className="ops-subpanel" data-testid="scanner-user-list"><p className="eyebrow">ACTIVE ACCESS LIST</p>{scanners.map((user) => <div key={user.id} className="staff-row scanner-user-row" data-testid={`scanner-user-row-${user.id}`}><div><strong>{user.name}</strong><small>{user.email}</small></div><span className={`ops-status ${user.is_active ? "status-live" : "status-cancelled"}`}>{user.is_active ? "ACTIVE" : "DISABLED"}</span><button onClick={() => update.mutate({ id: user.id, payload: { name: user.name, role: "scanner", is_active: !user.is_active, password: null } })} data-testid={`scanner-user-toggle-${user.id}`}>{user.is_active ? "Disable" : "Enable"}</button></div>)}{!scanners.length && <p className="empty-copy" data-testid="scanner-user-empty">No scanner users yet.</p>}</div>
    </div>
  </section>;
}