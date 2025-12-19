import { BookOpen, Search, AlertCircle, Layers, Lightbulb, FileText, Clock } from "lucide-react";

const AgentOrchestra = () => {
  const agents = [
    {
      icon: BookOpen,
      name: "Principal Investigator",
      role: "Orchestration",
      description: "Coordinates research workflow and delegates tasks to specialized agents",
      latency: "0.2s",
      status: "active",
    },
    {
      icon: Search,
      name: "Literature Scout",
      role: "Discovery",
      description: "Searches and retrieves relevant papers, citations, and research context",
      latency: "1.2s",
      status: "active",
    },
    {
      icon: AlertCircle,
      name: "Critic Agent",
      role: "Validation",
      description: "Evaluates claims, identifies weaknesses, and ensures research rigor",
      latency: "0.8s",
      status: "active",
    },
    {
      icon: Layers,
      name: "Synthesizer",
      role: "Analysis",
      description: "Combines insights across papers to identify patterns and themes",
      latency: "0.6s",
      status: "active",
    },
    {
      icon: Lightbulb,
      name: "Hypothesis Generator",
      role: "Creation",
      description: "Generates novel research hypotheses based on discovered gaps",
      latency: "0.9s",
      status: "active",
    },
    {
      icon: FileText,
      name: "Writing Agent",
      role: "Output",
      description: "Produces clear, structured research summaries and reports",
      latency: "0.4s",
      status: "active",
    },
  ];

  return (
    <section id="agents" className="py-24 relative">
      {/* Background accent */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-primary/5 to-transparent" />

      <div className="container mx-auto px-6 relative z-10">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
            Agent <span className="gradient-text">Orchestra</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            Six specialized AI agents working in concert to conduct comprehensive
            research analysis and hypothesis generation.
          </p>
        </div>

        {/* Agent grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {agents.map((agent, index) => (
            <div
              key={agent.name}
              className="glass-card p-6 hover:border-primary/50 transition-all duration-300 group animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                    <agent.icon className="h-5 w-5" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-lg">{agent.name}</h3>
                    <span className="text-xs text-primary bg-primary/10 px-2 py-0.5 rounded-full">
                      {agent.role}
                    </span>
                  </div>
                </div>
                {/* Status indicator */}
                <div className="flex items-center gap-1.5">
                  <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                  <span className="text-xs text-muted-foreground">Active</span>
                </div>
              </div>

              {/* Description */}
              <p className="text-sm text-muted-foreground mb-4">
                {agent.description}
              </p>

              {/* Latency */}
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Clock className="h-3.5 w-3.5" />
                <span>Avg latency: {agent.latency}</span>
              </div>
            </div>
          ))}
        </div>

        {/* System status */}
        <div className="mt-12 glass-card p-6 max-w-xl mx-auto">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full bg-green-500 animate-pulse" />
              <span className="font-medium">System Status: Operational</span>
            </div>
            <span className="text-sm text-muted-foreground">
              All 6 agents online
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default AgentOrchestra;
