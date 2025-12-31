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
  const severityToStatus = (severity: string): "good" | "medium" | "bad" => {
    if (severity === "NEEDS_WORK") return "bad";
    if (severity === "WARNING") return "medium";
    return "good";
  };

  return (
    <div className="bg-gradient-card backdrop-blur-xl border border-border rounded-3xl p-6 md:p-8 shadow-card print-friendly">
      <h3 className="text-xl font-semibold text-foreground mb-6">Resume Tips & Ideas</h3>
      <div className="space-y-3">
        {tips.map((tip, index) => (
          <div 
            key={tip.id || index}
            className="animate-fade-in-up"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <TipItem text={tip.message} status={severityToStatus(tip.severity)} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default TipsList;
