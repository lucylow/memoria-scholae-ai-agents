import { Play, Github, Sparkles, Brain, Network, Lightbulb, Database } from "lucide-react";
import { Button } from "@/components/ui/button";

const HeroSection = () => {
  const features = [
    { icon: Database, label: "Persistent Memory" },
    { icon: Network, label: "Graph Reasoning" },
    { icon: Brain, label: "Multi-Agent AI" },
    { icon: Lightbulb, label: "Hypothesis Generation" },
  ];

  return (
    <section className="relative min-h-screen flex items-center justify-center pt-20 overflow-hidden">
      {/* Animated background orbs */}
      <div className="orb orb-cyan w-96 h-96 -top-48 -left-48" />
      <div className="orb orb-purple w-80 h-80 top-1/4 -right-40" style={{ animationDelay: "2s" }} />
      <div className="orb orb-cyan w-64 h-64 bottom-20 left-1/4" style={{ animationDelay: "4s" }} />

      <div className="container mx-auto px-6 relative z-10">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass-card mb-8 animate-fade-in">
            <Sparkles className="h-4 w-4 text-primary" />
            <span className="text-sm text-muted-foreground">
              AI-Powered Research Assistant
            </span>
          </div>

          {/* Title */}
          <h1 className="text-5xl md:text-7xl font-display font-bold mb-6 animate-fade-in" style={{ animationDelay: "0.1s" }}>
            <span className="gradient-text">Memoria</span>{" "}
            <span className="text-foreground">Scholae</span>
          </h1>

          {/* Tagline with typing effect */}
          <p className="text-xl md:text-2xl text-primary glow-text mb-8 animate-fade-in" style={{ animationDelay: "0.2s" }}>
            Research That Remembers
          </p>

          {/* Description */}
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-10 animate-fade-in" style={{ animationDelay: "0.3s" }}>
            A cognitive architecture combining persistent episodic memory, 
            knowledge graph reasoning, and multi-agent collaboration for 
            breakthrough research discovery.
          </p>

          {/* Feature chips */}
          <div className="flex flex-wrap justify-center gap-3 mb-10 animate-fade-in" style={{ animationDelay: "0.4s" }}>
            {features.map((feature, index) => (
              <div
                key={feature.label}
                className="flex items-center gap-2 px-4 py-2 rounded-lg glass-card hover:border-primary/50 transition-colors cursor-default"
                style={{ animationDelay: `${0.5 + index * 0.1}s` }}
              >
                <feature.icon className="h-4 w-4 text-primary" />
                <span className="text-sm">{feature.label}</span>
              </div>
            ))}
          </div>

          {/* CTAs */}
          <div className="flex flex-wrap justify-center gap-4 animate-fade-in" style={{ animationDelay: "0.6s" }}>
            <Button size="lg" className="btn-primary gap-2 text-lg px-8">
              <Play className="h-5 w-5" />
              Watch Live Demo
            </Button>
            <a
              href="https://github.com/lucylow/memoria-scholae"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button size="lg" variant="outline" className="gap-2 text-lg px-8 border-border hover:bg-muted/50">
                <Github className="h-5 w-5" />
                View Source
              </Button>
            </a>
          </div>
        </div>
      </div>

      {/* Bottom gradient fade */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-background to-transparent" />
    </section>
  );
};

export default HeroSection;
