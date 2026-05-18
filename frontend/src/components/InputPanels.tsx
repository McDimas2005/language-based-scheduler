import { ChangeEvent, useState } from "react";
import { FileAudio, Mic, Send, Square, Upload } from "lucide-react";

import { useRecorder } from "../hooks/useRecorder";
import { Button, ErrorAlert } from "./Ui";

const examples = [
  "Schedule a meeting with my lecturer tomorrow at 10 AM",
  "Add gym session next Monday at 7 PM",
  "Book dentist appointment on Friday morning",
  "Create lunch with friends tomorrow at 12",
];

export function TextSchedulerInput({
  onAnalyze,
  disabled,
}: {
  onAnalyze: (text: string) => void;
  disabled?: boolean;
}) {
  const [text, setText] = useState(examples[0]);
  return (
    <div className="space-y-4">
      <textarea
        value={text}
        onChange={(event) => setText(event.target.value)}
        className="min-h-36 w-full resize-none rounded-lg border border-ink/10 bg-white p-4 text-sm text-ink outline-none transition focus:border-moss focus:ring-4 focus:ring-mint"
      />
      <div className="flex flex-wrap gap-2">
        {examples.map((example) => (
          <button
            key={example}
            onClick={() => setText(example)}
            className="rounded-full bg-white px-3 py-1 text-xs font-medium text-graphite shadow-line hover:bg-mint"
          >
            {example}
          </button>
        ))}
      </div>
      <Button disabled={disabled || !text.trim()} onClick={() => onAnalyze(text)}>
        <Send size={16} />
        Analyze request
      </Button>
    </div>
  );
}

export function AudioUploader({
  onAnalyze,
  disabled,
}: {
  onAnalyze: (file: File) => void;
  disabled?: boolean;
}) {
  const [file, setFile] = useState<File | null>(null);

  function onChange(event: ChangeEvent<HTMLInputElement>) {
    setFile(event.target.files?.[0] ?? null);
  }

  return (
    <div className="space-y-4">
      <label className="flex min-h-40 cursor-pointer flex-col items-center justify-center rounded-lg border border-dashed border-moss/40 bg-white/70 p-6 text-center transition hover:bg-mint/50">
        <Upload className="mb-3 text-moss" size={28} />
        <span className="text-sm font-semibold text-ink">Upload WAV, MP3, M4A, OGG, or WEBM</span>
        <span className="mt-1 text-xs text-graphite/70">Legacy audio samples are supported for validation.</span>
        <input className="hidden" type="file" accept=".wav,.mp3,.m4a,.ogg,.webm,audio/*" onChange={onChange} />
      </label>
      {file && (
        <div className="flex items-center justify-between rounded-lg bg-white p-3 shadow-line">
          <span className="flex items-center gap-2 text-sm font-medium text-ink">
            <FileAudio size={16} />
            {file.name}
          </span>
          <span className="text-xs text-graphite/70">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
        </div>
      )}
      <Button disabled={disabled || !file} onClick={() => file && onAnalyze(file)}>
        <Upload size={16} />
        Analyze audio
      </Button>
    </div>
  );
}

export function VoiceRecorder({
  onAnalyze,
  disabled,
}: {
  onAnalyze: (blob: Blob) => void;
  disabled?: boolean;
}) {
  const recorder = useRecorder();
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-ink/10 bg-white p-5 shadow-line">
        <div className="mb-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-ink">Browser recording</p>
            <p className="text-xs text-graphite/70">Record a natural-language scheduling request.</p>
          </div>
          <span className={`h-3 w-3 rounded-full ${recorder.recording ? "bg-coral" : "bg-moss"}`} />
        </div>
        <div className="flex flex-wrap gap-3">
          {!recorder.recording ? (
            <Button disabled={disabled} onClick={recorder.start}>
              <Mic size={16} />
              Start recording
            </Button>
          ) : (
            <Button variant="danger" onClick={recorder.stop}>
              <Square size={16} />
              Stop
            </Button>
          )}
          <Button disabled={disabled || !recorder.audioBlob} variant="secondary" onClick={() => recorder.audioBlob && onAnalyze(recorder.audioBlob)}>
            <Send size={16} />
            Analyze recording
          </Button>
        </div>
      </div>
      {recorder.audioUrl && <audio className="w-full" controls src={recorder.audioUrl} />}
      {recorder.error && <ErrorAlert message={recorder.error} />}
    </div>
  );
}

