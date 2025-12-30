import TipItem from "./TipItem";

interface Tip {
  text: string;
  status: "good" | "medium" | "bad";
}

interface TipsListProps {
  tips: Tip[];
}

const TipsList = ({ tips }: TipsListProps) => {
  return (
    <div className="bg-gradient-card backdrop-blur-xl border border-border rounded-3xl p-6 md:p-8 shadow-card print-friendly">
      <h3 className="text-xl font-semibold text-foreground mb-6">Resume Tips & Ideas</h3>
      <div className="space-y-3">
        {tips.map((tip, index) => (
          <div 
            key={index}
            className="animate-fade-in-up"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <TipItem text={tip.text} status={tip.status} />
          </div>
        ))}
      </div>
    </div>
  );
};

export default TipsList;
