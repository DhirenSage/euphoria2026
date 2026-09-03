import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiPostForm } from "@/lib/api";
import { queryClient } from "@/lib/queryClient";
import type { BulkPassImportResponse } from "@/lib/euphoria";

export default function BulkPassGenerator() {
  const [file, setFile] = useState<File | null>(null);
  const upload = useMutation({
    mutationFn: (selected: File) => { const body = new FormData(); body.append("file", selected); return apiPostForm<BulkPassImportResponse>("/admin/bulk-passes/import", body); },
    onSuccess: () => { queryClient.invalidateQueries({ queryKey: ["admin-registrations"] }); queryClient.invalidateQueries({ queryKey: ["admin-dashboard"] }); },
  });

  return <section id="bulk-passes" className="ops-panel" data-testid="bulk-pass-generator">
    <div className="ops-panel-heading"><div><p className="eyebrow accent">MANUAL PASS GENERATOR</p><h2>Bulk complimentary passes</h2><p className="ops-panel-copy">Upload CSV or Excel. Every valid row becomes a confirmed complimentary registration with active QR and scheduled pass email.</p></div><a className="button button-ghost" href="/api/admin/bulk-passes/template.csv" data-testid="bulk-pass-template-download">Download template ↓</a></div>
    <div className="bulk-pass-layout"><div className="ops-subpanel"><p className="eyebrow">REQUIRED COLUMNS</p><code data-testid="bulk-pass-columns">participant_name · mobile · institute_name · email · event_name</code><p>Optional: event_slug, city, participant_affiliation. Event name must match Admin exactly; event_slug is safer when names repeat.</p></div><form className="ops-subpanel" data-testid="bulk-pass-upload-form" onSubmit={(event) => { event.preventDefault(); if (file) upload.mutate(file); }}><label>Participant list (.csv or .xlsx)<input type="file" accept=".csv,.xlsx" required onChange={(event) => setFile(event.target.files?.[0] ?? null)} data-testid="bulk-pass-file-input" /></label><button className="button button-yellow" type="submit" disabled={!file || upload.isPending} data-testid="bulk-pass-upload-button">{upload.isPending ? "Generating passes…" : "Generate & email passes"}</button>{upload.isError && <p className="form-error" data-testid="bulk-pass-upload-error">Import failed. Check the file format, required columns, row values, and event names.</p>}</form></div>
    {upload.data && <div className="bulk-import-result" data-testid="bulk-pass-import-result"><div><span>ROWS</span><strong>{upload.data.total_rows}</strong></div><div><span>CREATED</span><strong>{upload.data.created}</strong></div><div><span>SKIPPED</span><strong>{upload.data.skipped}</strong></div><div><span>EMAILS SCHEDULED</span><strong>{upload.data.emails_scheduled}</strong></div>{upload.data.errors.length > 0 && <ul data-testid="bulk-pass-errors">{upload.data.errors.slice(0, 20).map((error) => <li key={`${error.row}-${error.message}`}>Row {error.row}: {error.message}</li>)}</ul>}</div>}
  </section>;
}