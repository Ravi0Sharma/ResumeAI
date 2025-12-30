import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";

const LandingPage = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const handleChooseFile = () => {
    fileInputRef.current?.click();
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + " B";
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " KB";
    return (bytes / (1024 * 1024)).toFixed(1) + " MB";
  };

  const handleProcess = () => {
    if (!selectedFile) return;
    
    setIsProcessing(true);
    
    // Simulate processing
    const processingTime = 900 + Math.random() * 500;
    setTimeout(() => {
      // Generate mock data
      const mockScore = 550 + Math.floor(Math.random() * 300);
      const mockTips = [
        { text: "You added Objective/Summary", status: "good" as const },
        { text: "Education details present", status: "good" as const },
        { text: "Experience added", status: "good" as const },
        { text: "Skills added", status: "good" as const },
        { text: "Projects added", status: "good" as const },
        { text: "Contact information complete", status: "medium" as const },
        { text: "Consider adding more keywords", status: "medium" as const },
        { text: "Add Certifications to strengthen your profile", status: "bad" as const },
        { text: "Add Achievements to stand out", status: "bad" as const },
        { text: "Add Interests to show personality", status: "bad" as const },
        { text: "Add Hobbies to appear well-rounded", status: "bad" as const },
      ];
      
      navigate("/result", { 
        state: { 
          score: mockScore, 
          tips: mockTips,
          fileName: selectedFile.name 
        } 
      });
    }, processingTime);
  };

  return (
    <div className="min-h-screen bg-noise relative">
      <div className="relative z-10 container mx-auto px-4 py-12 md:py-20">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center min-h-[80vh]">
          {/* Left column */}
          <div className="space-y-8">
            {/* Logo */}
            <div className="animate-fade-in-up">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-xl bg-primary flex items-center justify-center shadow-glow-primary">
                  <svg className="w-6 h-6 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>
                <span className="text-xl font-semibold text-foreground">ResumeAI</span>
              </div>
            </div>

            {/* Pill badge */}
            <div className="animate-fade-in-up-delay-1">
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-surface-light border border-border text-sm text-foreground-muted">
                <span className="w-2 h-2 rounded-full bg-success animate-pulse-glow" />
                What's new · Just shipped v1.0
              </span>
            </div>

            {/* Hero text */}
            <div className="animate-fade-in-up-delay-2 space-y-4">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground leading-tight">
                Analyze your resume with{" "}
                <span className="text-primary">AI precision</span>
              </h1>
              <p className="text-lg text-foreground-muted max-w-lg">
                Get instant feedback on your resume. Our AI analyzes your content and provides actionable tips to help you land your dream job.
              </p>
            </div>

            {/* Upload section */}
            <div className="animate-fade-in-up-delay-3 space-y-4">
              <div className="flex flex-col sm:flex-row gap-4">
                <button
                  onClick={handleProcess}
                  disabled={!selectedFile || isProcessing}
                  className="px-8 py-3.5 rounded-2xl font-medium transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed bg-primary text-primary-foreground hover:shadow-glow-primary hover:-translate-y-0.5 disabled:hover:translate-y-0 disabled:hover:shadow-none flex items-center justify-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                      </svg>
                      Processing...
                    </>
                  ) : (
                    "Process"
                  )}
                </button>
                
                <div className="flex items-center gap-3">
                  <input
                    ref={fileInputRef}
                    type="file"
                    id="resume-upload"
                    accept=".pdf,.doc,.docx"
                    onChange={handleFileChange}
                    disabled={isProcessing}
                    className="sr-only"
                    aria-label="Upload resume file"
                  />
                  <button
                    onClick={handleChooseFile}
                    disabled={isProcessing}
                    className="px-6 py-3.5 rounded-2xl font-medium border border-border bg-surface-light text-foreground hover:bg-surface hover:border-border-light transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 focus:ring-offset-background disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Choose file
                  </button>
                  <span className="text-sm text-foreground-muted">
                    {selectedFile ? "" : "No file chosen"}
                  </span>
                </div>
              </div>

              {/* Selected file info */}
              {selectedFile && (
                <div className="flex items-center gap-3 p-4 rounded-2xl bg-surface-light border border-border animate-fade-in-up">
                  <svg className="w-5 h-5 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-foreground truncate">{selectedFile.name}</p>
                    <p className="text-xs text-foreground-muted">{formatFileSize(selectedFile.size)}</p>
                  </div>
                  <button
                    onClick={() => setSelectedFile(null)}
                    disabled={isProcessing}
                    className="p-1 text-foreground-muted hover:text-foreground transition-colors disabled:opacity-50"
                    aria-label="Remove file"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right column - Illustration */}
          <div className="hidden lg:flex items-center justify-center">
            <div className="relative animate-float">
              {/* Main illustration container */}
              <div className="w-80 h-80 rounded-3xl bg-gradient-card border border-border shadow-card flex items-center justify-center relative overflow-hidden">
                {/* Decorative elements */}
                <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-transparent" />
                <div className="absolute top-4 left-4 w-24 h-3 rounded-full bg-foreground/10" />
                <div className="absolute top-10 left-4 w-32 h-3 rounded-full bg-foreground/5" />
                <div className="absolute top-16 left-4 w-20 h-3 rounded-full bg-foreground/10" />
                
                {/* Central icon */}
                <div className="relative z-10 w-24 h-24 rounded-2xl bg-primary/20 flex items-center justify-center shadow-glow-primary">
                  <svg className="w-12 h-12 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                </div>

                {/* Floating badges */}
                <div className="absolute -top-4 -right-4 px-3 py-1.5 rounded-full bg-success text-success-foreground text-xs font-medium shadow-glow-success">
                  ✓ Skills
                </div>
                <div className="absolute -bottom-4 -left-4 px-3 py-1.5 rounded-full bg-warning text-warning-foreground text-xs font-medium shadow-glow-warning">
                  ~ Experience
                </div>
                <div className="absolute bottom-8 -right-6 px-3 py-1.5 rounded-full bg-muted text-muted-foreground text-xs font-medium shadow-glow-muted">
                  ! Certs
                </div>
              </div>

              {/* Glow effect */}
              <div className="absolute inset-0 rounded-3xl bg-primary/20 blur-3xl -z-10 animate-pulse-glow" />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LandingPage;
