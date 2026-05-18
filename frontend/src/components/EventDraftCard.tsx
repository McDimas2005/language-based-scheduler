import { CalendarCheck, ExternalLink, ShieldAlert } from "lucide-react";
import type { AuthStatus, CalendarCreateResponse, EditableDraft, EventDraft } from "../types/api";
import { recomputeDatetimes } from "../lib/datetime";
import { Button, StatusPill } from "./Ui";

export function EventDraftCard({
  draft,
  editable,
  auth,
  result,
  onChange,
  onCreate,
  onConnect,
}: {
  draft: EventDraft;
  editable: EditableDraft;
  auth: AuthStatus | null;
  result: CalendarCreateResponse | null;
  onChange: (draft: EditableDraft) => void;
  onCreate: () => void;
  onConnect: () => void;
}) {
  const requiredMissing = !editable.title || !editable.start_datetime || !editable.end_datetime;

  function update<K extends keyof EditableDraft>(key: K, value: EditableDraft[K]) {
    const next = recomputeDatetimes({ ...editable, [key]: value });
    onChange(next);
  }

  return (
    <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft">
      <div className="mb-5 flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase text-moss">Event draft</p>
          <h3 className="mt-1 text-xl font-bold text-ink">{editable.title || "Untitled event"}</h3>
        </div>
        <div className="flex flex-wrap gap-2">
          {editable.category && <StatusPill ok label={`${editable.category} ${Math.round(draft.category_confidence * 100)}%`} />}
          <StatusPill ok={!draft.missing_fields.length} label={draft.missing_fields.length ? "Needs edits" : "Ready to confirm"} />
        </div>
      </div>

      {draft.transcript && (
        <div className="mb-4 rounded-lg bg-paper p-3 text-sm text-graphite">
          <span className="font-semibold text-ink">Transcript:</span> {draft.transcript}
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        <Field label="Title" value={editable.title} onChange={(value) => update("title", value)} />
        <Field label="Category" value={editable.category} onChange={(value) => update("category", value)} />
        <Field label="Date" type="date" value={editable.date} onChange={(value) => update("date", value)} />
        <Field label="Time" type="time" value={editable.time} onChange={(value) => update("time", value)} />
        <Field
          label="Duration"
          type="number"
          value={String(editable.duration_minutes)}
          onChange={(value) => update("duration_minutes", Math.max(15, Number(value) || 60))}
        />
        <Field label="Timezone" value={editable.timezone} onChange={(value) => update("timezone", value)} />
      </div>

      <label className="mt-4 block">
        <span className="mb-2 block text-xs font-semibold uppercase text-graphite">Description</span>
        <textarea
          value={editable.description}
          onChange={(event) => update("description", event.target.value)}
          className="min-h-24 w-full resize-none rounded-lg border border-ink/10 bg-paper p-3 text-sm text-ink outline-none focus:border-moss focus:ring-4 focus:ring-mint"
        />
      </label>

      {(draft.warnings.length > 0 || draft.missing_fields.length > 0) && (
        <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-900">
          <p className="mb-2 flex items-center gap-2 font-semibold">
            <ShieldAlert size={16} />
            Confirm before saving
          </p>
          {[...draft.missing_fields.map((field) => `Missing field: ${field}`), ...draft.warnings].map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </div>
      )}

      <div className="mt-5 flex flex-wrap items-center gap-3">
        {!auth?.connected ? (
          <Button variant="secondary" onClick={onConnect}>
            <CalendarCheck size={16} />
            Connect Google Calendar
          </Button>
        ) : (
          <Button disabled={requiredMissing} onClick={onCreate}>
            <CalendarCheck size={16} />
            Create event
          </Button>
        )}
        {result?.html_link && (
          <a
            className="inline-flex items-center gap-2 rounded-lg bg-mint px-4 py-2 text-sm font-semibold text-moss"
            href={result.html_link}
            target="_blank"
            rel="noreferrer"
          >
            View in Calendar
            <ExternalLink size={16} />
          </a>
        )}
      </div>
    </div>
  );
}

function Field({
  label,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  type?: string;
}) {
  return (
    <label className="block">
      <span className="mb-2 block text-xs font-semibold uppercase text-graphite">{label}</span>
      <input
        type={type}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        className="h-11 w-full rounded-lg border border-ink/10 bg-paper px-3 text-sm text-ink outline-none focus:border-moss focus:ring-4 focus:ring-mint"
      />
    </label>
  );
}
