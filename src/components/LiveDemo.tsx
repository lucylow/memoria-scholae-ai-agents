import { Search, Database, Network, Lightbulb, ArrowRight } from "lucide-react";

const LiveDemo = () => {
  const steps = [
    {
      icon: Search,
      title: "Query",
      description: "Natural language research question",
      example: '"How can GNNs help with few-shot protein structure prediction?"',
      color: "border-primary",
    },
    {
      icon: Database,
      title: "Memory",
      description: "Retrieve relevant episodic memories",
      example: "Previous research context & session history",
      color: "border-cyan",
    },
    {
      icon: Network,
      title: "Graph",
      description: "Traverse knowledge relationships",
      example: "GNN → Proteins → Structure → Few-shot",
      color: "border-purple",
    },
    {
      icon: Lightbulb,
      title: "Hypothesis",
      description: "Generate novel research insights",
      example: "Cross-domain synthesis & gap identification",
      color: "border-primary",
    },
  ];

  return (
    <section id="workflow" className="py-24 relative">
      <div className="container mx-auto px-6">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
            Live Demo <span className="gradient-text">Workflow</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Watch how a research query flows through our cognitive architecture
            to generate novel hypotheses.
          </p>
        </div>

        {/* Demo query */}
        <div className="glass-card p-6 mb-12 max-w-3xl mx-auto">
          <div className="flex items-center gap-3 mb-4">
            <Search className="h-5 w-5 text-primary" />
            <span className="text-sm text-muted-foreground">Research Query</span>
          </div>
          <p className="text-lg font-mono text-foreground">
            "How can GNNs help with few-shot protein structure prediction?"
          </p>
        </div>

        {/* Pipeline steps */}
        <div className="grid md:grid-cols-4 gap-4 relative">
          {steps.map((step, index) => (
            <div key={step.title} className="relative flex flex-col items-center">
              {/* Arrow between steps */}
              {index < steps.length - 1 && (
                <div className="hidden md:block absolute top-12 -right-4 z-10">
                  <ArrowRight className="h-8 w-8 text-muted-foreground/50" />
                </div>
              )}

              {/* Step card */}
              <div
                className={`glass-card p-6 w-full hover:border-primary/50 transition-all duration-300 animate-fade-in ${step.color}`}
                style={{ animationDelay: `${index * 0.15}s` }}
              >
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2 rounded-lg bg-muted">
                    <step.icon className="h-5 w-5 text-primary" />
                  </div>
                  <div>
                    <div className="text-xs text-muted-foreground">Step {index + 1}</div>
                    <h3 className="font-semibold">{step.title}</h3>
                  </div>
                </div>
                <p className="text-sm text-muted-foreground mb-3">
                  {step.description}
                </p>
                <div className="text-xs font-mono text-primary/80 bg-muted/50 p-2 rounded">
                  {step.example}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Result preview */}
        <div className="mt-12 glass-card p-8 max-w-3xl mx-auto animate-fade-in" style={{ animationDelay: "0.6s" }}>
          <div className="flex items-center gap-3 mb-4">
            <Lightbulb className="h-5 w-5 text-primary" />
            <span className="text-sm font-semibold">Generated Hypothesis</span>
          </div>
          <p className="text-muted-foreground leading-relaxed">
            "Based on your query, I discovered fascinating connections across your knowledge graph. 
            Graph Neural Networks could leverage the inherent graph structure of protein molecules 
            to enable few-shot learning by encoding structural priors, reducing the need for 
            extensive training data while maintaining prediction accuracy."
          </p>
        </div>
      </div>
    </section>
  );
};

export default LiveDemo;
