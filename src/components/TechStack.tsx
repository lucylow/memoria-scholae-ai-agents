import { Database, Network, Cpu, Zap, Target, Clock } from "lucide-react";

const TechStack = () => {
  const technologies = [
    {
      icon: Database,
      name: "MemMachine",
      description: "Episodic memory with temporal reasoning",
      color: "text-primary",
    },
    {
      icon: Network,
      name: "Neo4j",
      description: "Knowledge graph for concept relationships",
      color: "text-purple",
    },
    {
      icon: Cpu,
      name: "LangGraph",
      description: "Multi-agent orchestration framework",
      color: "text-cyan",
    },
  ];

  const metrics = [
    { icon: Zap, value: "2.8s", label: "Avg Latency" },
    { icon: Target, value: "98%", label: "Accuracy" },
    { icon: Clock, value: "24/7", label: "Uptime" },
  ];

  return (
    <section id="tech" className="py-24 relative">
      <div className="container mx-auto px-6">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-display font-bold mb-4">
            Powered by <span className="gradient-text">Advanced Tech</span>
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto">
            A carefully architected stack combining the best of memory systems, 
            graph databases, and AI orchestration.
          </p>
        </div>

        {/* Tech cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {technologies.map((tech, index) => (
            <div
              key={tech.name}
              className="glass-card p-8 hover:border-primary/50 transition-all duration-300 group animate-fade-in"
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className={`inline-flex p-3 rounded-xl bg-muted mb-4 ${tech.color}`}>
                <tech.icon className="h-8 w-8" />
              </div>
              <h3 className="text-xl font-semibold mb-2 group-hover:text-primary transition-colors">
                {tech.name}
              </h3>
              <p className="text-muted-foreground">{tech.description}</p>
            </div>
          ))}
        </div>

        {/* Metrics */}
        <div className="glass-card p-8">
          <div className="grid md:grid-cols-3 gap-8">
            {metrics.map((metric, index) => (
              <div
                key={metric.label}
                className="text-center animate-fade-in"
                style={{ animationDelay: `${0.3 + index * 0.1}s` }}
              >
                <metric.icon className="h-6 w-6 text-primary mx-auto mb-3" />
                <div className="text-4xl font-display font-bold gradient-text mb-1">
                  {metric.value}
                </div>
                <div className="text-sm text-muted-foreground">{metric.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};

export default TechStack;
