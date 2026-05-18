import { motion } from "framer-motion";
import { ArrowDown, CalendarClock, Github, Sparkles } from "lucide-react";

import { PipelineStepper } from "../components/PipelineStepper";
import { SchedulerWorkspace } from "../components/SchedulerWorkspace";
import { Button } from "../components/Ui";

export function App() {
  return (
    <div className="min-h-screen bg-paper text-ink">
      <nav className="sticky top-0 z-30 border-b border-ink/10 bg-paper/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6">
          <a href="#top" className="flex items-center gap-2 text-sm font-bold text-ink">
            <CalendarClock className="text-moss" size={22} />
            Language Based Scheduler
          </a>
          <div className="hidden items-center gap-5 text-sm font-semibold text-graphite md:flex">
            <a href="#scheduler">Scheduler</a>
            <a href="#pipeline">Pipeline</a>
            <a href="#tech">Tech</a>
          </div>
        </div>
      </nav>

      <main id="top">
        <section className="relative overflow-hidden border-b border-ink/10">
          <div className="mx-auto grid min-h-[calc(100vh-72px)] max-w-6xl items-center gap-8 px-4 py-12 sm:px-6 lg:grid-cols-[1fr_0.9fr]">
            <motion.div initial={{ opacity: 0, y: 22 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.55 }}>
              <div className="mb-5 inline-flex items-center gap-2 rounded-full bg-white px-3 py-1 text-xs font-bold text-moss shadow-line">
                <Sparkles size={14} />
                Whisper + spaCy + BERT + Google Calendar
              </div>
              <h1 className="max-w-3xl text-5xl font-black leading-[1.02] text-ink sm:text-6xl">
                Language Based Scheduler
              </h1>
              <p className="mt-5 max-w-xl text-lg leading-8 text-graphite">
                Turn natural language into editable calendar events with a production-style AI pipeline built from the original college NLP AOL prototype.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a href="#scheduler">
                  <Button>
                    Try Scheduler
                    <ArrowDown size={16} />
                  </Button>
                </a>
                <a href="#pipeline">
                  <Button variant="secondary">View Pipeline</Button>
                </a>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, scale: 0.96 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.55, delay: 0.1 }}
              className="rounded-lg border border-ink/10 bg-white p-5 shadow-soft"
            >
              <div className="mb-4 flex items-center justify-between">
                <p className="text-sm font-bold text-ink">AI Event Draft</p>
                <span className="rounded-full bg-mint px-3 py-1 text-xs font-bold text-moss">Preview first</span>
              </div>
              <div className="space-y-3">
                {[
                  ["Request", "Schedule a meeting with my lecturer tomorrow at 10 AM"],
                  ["Extraction", "Meeting with my lecturer · Tomorrow · 10:00"],
                  ["Classification", "education · 87% confidence"],
                  ["Calendar", "Waiting for user confirmation"],
                ].map(([label, value]) => (
                  <div key={label} className="rounded-lg bg-paper p-4 shadow-line">
                    <p className="text-xs font-bold uppercase text-moss">{label}</p>
                    <p className="mt-1 text-sm font-semibold text-ink">{value}</p>
                  </div>
                ))}
              </div>
            </motion.div>
          </div>
        </section>

        <SchedulerWorkspace />

        <section id="pipeline" className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
          <div className="mb-6">
            <p className="text-xs font-bold uppercase text-moss">AI pipeline</p>
            <h2 className="mt-2 text-3xl font-black text-ink">From speech to confirmed calendar event</h2>
          </div>
          <PipelineStepper />
        </section>

        <section id="tech" className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
          <div className="grid gap-4 md:grid-cols-4">
            {[
              ["Whisper", "Speech-to-text with the legacy base model family."],
              ["spaCy", "NER and rule-assisted extraction for date, time, and activity phrases."],
              ["BERT", "Fine-tuned bert-base-uncased activity classifier loaded from the legacy checkpoint."],
              ["Google Calendar", "OAuth-based event creation after explicit user confirmation."],
            ].map(([title, body]) => (
              <div key={title} className="rounded-lg bg-white p-5 shadow-line">
                <h3 className="font-bold text-ink">{title}</h3>
                <p className="mt-2 text-sm leading-6 text-graphite/75">{body}</p>
              </div>
            ))}
          </div>
        </section>
      </main>

      <footer className="border-t border-ink/10 px-4 py-8 text-center text-sm text-graphite">
        <span>Upgraded college NLP AOL project</span>
        <span className="mx-2">·</span>
        <Github className="inline" size={14} />
      </footer>
    </div>
  );
}
