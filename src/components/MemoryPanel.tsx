import { Database, Clock, Brain, Layers, ArrowRight } from "lucide-react";

const MemoryPanel = () => {
  const memoryFeatures = [
    {
      icon: Clock,
      title: "Temporal Reasoning",
      description: "Track research evolution over time with timestamped episodic memories",
    },
    {
      icon: Brain,
      title: "Context Retention",
      description: "Maintain session context and recall previous research insights",
    },
    {
      icon: Layers,
      title: "Memory Consolidation",
      description: "Automatically merge and consolidate related memories for efficiency",
    },
  ];

  const sampleMemories = [
    {
      timestamp: "2 hours ago",
      content: "Explored GNN architectures for molecular property prediction",
      type: "Research",
    },
    {
      timestamp: "Yesterday",
      content: "Reviewed protein folding literature and AlphaFold methodology",
      type: "Literature",
    },
    {
      timestamp: "3 days ago",
      content: "Generated hypothesis: Few-shot learning with graph priors",
      type: "Hypothesis",
    },
  ];

  return (
    <section id="memory" className="py-24 relative">
      <div className="container mx-auto px-6">
        {/* Section header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-6">
            <Database className="h-4 w-4 text-primary" />
            <span className="text-sm text-muted-foreground">Under the Hood</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
            Persistent <span className="gradient-text">Memory</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            MemMachine provides episodic memory capabilities that allow the system
            to remember and build upon previous research sessions.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Features */}
          <div className="space-y-6">
            {memoryFeatures.map((feature, index) => (
              <div
                key={feature.title}
                className="glass-card p-6 hover:border-primary/50 transition-all duration-300 animate-fade-in"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="flex items-start gap-4">
                  <div className="p-2.5 rounded-xl bg-primary/10 text-primary">
                    <feature.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold mb-2">{feature.title}</h3>
                    <p className="text-sm text-muted-foreground">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Memory timeline */}
          <div className="glass-card p-6 animate-fade-in" style={{ animationDelay: "0.3s" }}>
            <div className="flex items-center gap-2 mb-6">
              <Database className="h-5 w-5 text-primary" />
              <h3 className="font-semibold">Recent Memories</h3>
            </div>

            <div className="space-y-4">
              {sampleMemories.map((memory, index) => (
                <div
                  key={index}
                  className="relative pl-6 pb-4 border-l border-border last:border-l-transparent"
                >
                  {/* Timeline dot */}
                  <div className="absolute -left-1.5 top-0 w-3 h-3 rounded-full bg-primary" />

                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="text-sm text-foreground mb-1">
                        {memory.content}
                      </p>
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                          {memory.type}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {memory.timestamp}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-4 border-t border-border">
              <a
                href="#"
                className="inline-flex items-center gap-2 text-sm text-primary hover:text-primary/80 transition-colors"
              >
                View all memories
                <ArrowRight className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MemoryPanel;
