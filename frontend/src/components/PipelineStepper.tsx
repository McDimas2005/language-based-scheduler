import { motion } from "framer-motion";
import { Bot, CalendarCheck, FileAudio, Mic, Sparkles } from "lucide-react";

const steps = [
  { label: "Voice/Text", icon: Mic },
  { label: "Whisper", icon: FileAudio },
  { label: "spaCy", icon: Sparkles },
  { label: "BERT", icon: Bot },
  { label: "Calendar", icon: CalendarCheck },
];

export function PipelineStepper() {
  return (
    <div className="grid gap-3 sm:grid-cols-5">
      {steps.map((step, index) => {
        const Icon = step.icon;
        return (
          <motion.div
            key={step.label}
            initial={{ opacity: 0, y: 12 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: index * 0.05 }}
            className="rounded-lg border border-ink/10 bg-white/70 p-4 shadow-line"
          >
            <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-mint text-moss">
              <Icon size={20} />
            </div>
            <p className="text-sm font-semibold text-ink">{step.label}</p>
          </motion.div>
        );
      })}
    </div>
  );
}

