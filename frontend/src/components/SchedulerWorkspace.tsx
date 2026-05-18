import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AudioLines, Keyboard, Mic2 } from "lucide-react";

import { api } from "../lib/api";
import { recomputeDatetimes, toEditableDraft } from "../lib/datetime";
import type { AuthStatus, CalendarCreateResponse, EditableDraft, EventDraft, HealthResponse } from "../types/api";
import { AudioUploader, TextSchedulerInput, VoiceRecorder } from "./InputPanels";
import { EventDraftCard } from "./EventDraftCard";
import { ErrorAlert, LoadingOverlay, StatusPill } from "./Ui";

type Tab = "voice" | "upload" | "text";

const tabs: { id: Tab; label: string; icon: typeof Mic2 }[] = [
  { id: "voice", label: "Voice Record", icon: Mic2 },
  { id: "upload", label: "Upload Audio", icon: AudioLines },
  { id: "text", label: "Type Text", icon: Keyboard },
];

export function SchedulerWorkspace() {
  const [activeTab, setActiveTab] = useState<Tab>("text");
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [auth, setAuth] = useState<AuthStatus | null>(null);
  const [draft, setDraft] = useState<EventDraft | null>(null);
  const [editable, setEditable] = useState<EditableDraft | null>(null);
  const [calendarResult, setCalendarResult] = useState<CalendarCreateResponse | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void refreshStatus();
  }, []);

  async function refreshStatus() {
    try {
      const [healthResponse, authResponse] = await Promise.all([api.health(), api.authStatus()]);
      setHealth(healthResponse);
      setAuth(authResponse);
    } catch {
      setError("Backend is offline or unreachable. Start FastAPI at http://localhost:8000.");
    }
  }

  async function runText(text: string) {
    await run("Analyzing language request", () => api.analyzeText(text));
  }

  async function runAudio(file: File | Blob) {
    await run("Transcribing and analyzing audio", () => api.scheduleFromAudio(file, file instanceof File ? file.name : "recording.webm"));
  }

  async function run(label: string, action: () => Promise<EventDraft>) {
    setLoading(label);
    setError(null);
    setCalendarResult(null);
    try {
      const response = await action();
      setDraft(response);
      setEditable(recomputeDatetimes(toEditableDraft(response)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Request failed.");
    } finally {
      setLoading(null);
    }
  }

  async function connectGoogle() {
    setLoading("Opening Google OAuth");
    setError(null);
    try {
      const response = await api.startGoogleAuth();
      window.location.href = response.authorization_url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Google OAuth could not start.");
      setLoading(null);
    }
  }

  async function createEvent() {
    if (!editable) return;
    setLoading("Creating Google Calendar event");
    setError(null);
    try {
      const result = await api.createEvent(editable);
      setCalendarResult(result);
      await refreshStatus();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not create the event.");
    } finally {
      setLoading(null);
    }
  }

  return (
    <section id="scheduler" className="relative mx-auto max-w-6xl px-4 py-10 sm:px-6">
      {loading && <LoadingOverlay label={loading} />}
      <div className="mb-6 flex flex-wrap gap-2">
        {health && (
          <>
            <StatusPill ok={health.models.spacy_available} label="spaCy" />
            <StatusPill ok={health.models.bert_available} label="BERT" />
            <StatusPill ok={health.models.whisper_available} label="Whisper" />
          </>
        )}
        {auth && <StatusPill ok={auth.connected} label={auth.connected ? "Calendar connected" : "Calendar not connected"} />}
      </div>

      {error && <div className="mb-5"><ErrorAlert message={error} /></div>}

      <div className="grid gap-6 lg:grid-cols-[0.95fr_1.05fr]">
        <motion.div
          initial={{ opacity: 0, x: -18 }}
          whileInView={{ opacity: 1, x: 0 }}
          viewport={{ once: true }}
          className="rounded-lg border border-ink/10 bg-paper/80 p-5 shadow-soft"
        >
          <div className="mb-5 flex rounded-lg bg-white p-1 shadow-line">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const selected = activeTab === tab.id;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex min-h-11 flex-1 items-center justify-center gap-2 rounded-md px-2 text-sm font-semibold transition ${
                    selected ? "bg-ink text-white" : "text-graphite hover:bg-mint"
                  }`}
                >
                  <Icon size={16} />
                  <span className="hidden sm:inline">{tab.label}</span>
                </button>
              );
            })}
          </div>

          {activeTab === "voice" && <VoiceRecorder disabled={Boolean(loading)} onAnalyze={runAudio} />}
          {activeTab === "upload" && <AudioUploader disabled={Boolean(loading)} onAnalyze={runAudio} />}
          {activeTab === "text" && <TextSchedulerInput disabled={Boolean(loading)} onAnalyze={runText} />}
        </motion.div>

        <motion.div initial={{ opacity: 0, x: 18 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }}>
          {draft && editable ? (
            <EventDraftCard
              draft={draft}
              editable={editable}
              auth={auth}
              result={calendarResult}
              onChange={setEditable}
              onCreate={createEvent}
              onConnect={connectGoogle}
            />
          ) : (
            <div className="grid min-h-[420px] place-items-center rounded-lg border border-ink/10 bg-white p-8 text-center shadow-soft">
              <div>
                <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-lg bg-mint text-moss">
                  <Keyboard size={26} />
                </div>
                <h3 className="text-xl font-bold text-ink">Draft preview appears here</h3>
                <p className="mt-2 max-w-sm text-sm text-graphite/75">
                  Analyze voice, uploaded audio, or typed text to review the extracted calendar event before saving it.
                </p>
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {health?.models.warnings.length ? (
        <div className="mt-5 rounded-lg bg-white p-4 text-sm text-graphite shadow-line">
          {health.models.warnings.map((warning) => (
            <p key={warning}>{warning}</p>
          ))}
        </div>
      ) : null}
    </section>
  );
}

