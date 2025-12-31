interface TipItemProps {
  text: string;
  status: "good" | "medium" | "bad";
}

const TipItem = ({ text, status }: TipItemProps) => {
  const getStyles = () => {
    switch (status) {
      case "good":
        return {
          container: "border-success/30 bg-success/5 hover:shadow-glow-success",
          icon: "text-success",
          badge: "bg-success/20 text-success",
          badgeText: "GOOD",
        };
      case "medium":
        return {
          container: "border-warning/30 bg-warning/5 hover:shadow-glow-warning",
          icon: "text-warning",
          badge: "bg-warning/20 text-warning",
          badgeText: "MEDIUM",
        };
      case "bad":
        return {
          container: "border-muted/30 bg-muted/5 hover:shadow-glow-muted",
          icon: "text-muted",
          badge: "bg-muted/20 text-muted",
          badgeText: "NEEDS WORK",
        };
    }
  };

  const styles = getStyles();

  const getIcon = () => {
    switch (status) {
      case "good":
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
          </svg>
        );
      case "medium":
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 8v4m0 4h.01" />
          </svg>
        );
      case "bad":
        return (
          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
    }
  };

  return (
    <div 
      className={`flex items-center gap-4 p-4 rounded-2xl border transition-all duration-300 hover:-translate-y-0.5 ${styles.container}`}
    >
      <span className={`flex-shrink-0 ${styles.icon}`}>
        {getIcon()}
      </span>
      <span className="flex-1 text-foreground">{text}</span>
      <span className={`px-2.5 py-1 rounded-lg text-xs font-semibold ${styles.badge}`}>
        {styles.badgeText}
      </span>
    </div>
  );
};

export default TipItem;
