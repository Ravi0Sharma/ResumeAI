import { useEffect, useState } from "react";

interface ScoreCardProps {
  score: number;
  maxScore?: number;
}

const ScoreCard = ({ score, maxScore = 1000 }: ScoreCardProps) => {
  const [animatedWidth, setAnimatedWidth] = useState(0);
  const percentage = (score / maxScore) * 100;
  
  useEffect(() => {
    setAnimatedWidth(percentage);
  }, [percentage]);

  const getVerdict = () => {
    if (score >= 800) return { label: "Good", color: "bg-success text-success-foreground" };
    if (score >= 550) return { label: "Medium", color: "bg-warning text-warning-foreground" };
    return { label: "Needs Work", color: "bg-muted text-muted-foreground" };
  };

  const getProgressColor = () => {
    if (score >= 800) return "bg-success shadow-glow-success";
    if (score >= 550) return "bg-warning shadow-glow-warning";
    return "bg-muted shadow-glow-muted";
  };

  const verdict = getVerdict();

  return (
    <div className="bg-gradient-card backdrop-blur-xl border border-border rounded-3xl p-6 md:p-8 shadow-card print-friendly">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-lg font-medium text-foreground-muted mb-1">Resume Score</h2>
          <div className="flex items-baseline gap-2">
            <span className="text-5xl md:text-6xl font-bold text-foreground">{score}</span>
            <span className="text-xl text-foreground-muted">/ {maxScore}</span>
          </div>
        </div>
        <span className={`px-3 py-1.5 rounded-full text-sm font-medium ${verdict.color}`}>
          {verdict.label}
        </span>
      </div>
      
      {/* Progress bar */}
      <div className="mb-4">
        <div 
          className="h-3 bg-surface-light rounded-full overflow-hidden"
          role="progressbar"
          aria-valuenow={score}
          aria-valuemin={0}
          aria-valuemax={maxScore}
          aria-label={`Resume score: ${score} out of ${maxScore}`}
        >
          <div 
            className={`h-full rounded-full transition-all duration-1000 ease-out ${getProgressColor()}`}
            style={{ width: `${animatedWidth}%` }}
          />
        </div>
      </div>
      
      <p className="text-sm text-foreground-muted">
        Calculated from your resume content
      </p>
    </div>
  );
};

export default ScoreCard;
