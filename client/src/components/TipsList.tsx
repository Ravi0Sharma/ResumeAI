import TipItem from "./TipItem";

export interface ApiTip {
  id: string;
  message: string;
  severity: string;
}

interface TipsListProps {
  tips: ApiTip[];
}

const TipsList = ({ tips }: TipsListProps) => {
  const severityToStatus = (
    severity: string
  ): "good" | "medium" | "bad" | null => {
    if (severity === "NEEDS_WORK") return "bad";
    if (severity === "WARNING") return "medium";
    if (severity === "GOOD") return "good";
    return null;
  };

  return (
    <div className="bg-gradient-card backdrop-blur-xl border border-border rounded-3xl p-6 md:p-8 shadow-card print-friendly">
      <h3 className="text-xl font-semibold text-foreground mb-6">Resume Tips & Ideas</h3>
      <div className="space-y-3">
        {tips.map((tip, index) => (
          <div 
            key={tip.id}
            className="animate-fade-in-up"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            {!tip.id ? (
              <div className="p-4 rounded-2xl border border-border bg-surface-light text-foreground">
                Invalid API tip: missing id
              </div>
            ) : severityToStatus(tip.severity) === null ? (
              <div className="p-4 rounded-2xl border border-border bg-surface-light text-foreground">
                Invalid API tip severity: {String(tip.severity)}
              </div>
            ) : (
              <TipItem
                text={tip.message}
                status={severityToStatus(tip.severity) as "good" | "medium" | "bad"}
              />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default TipsList;
