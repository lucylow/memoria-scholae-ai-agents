import { Brain, Github, FileText, Cpu, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";

const Navbar = () => {
  const navLinks = [
    { label: "Research App", href: "#demo", icon: Brain },
    { label: "Live Demo", href: "#workflow", icon: Cpu },
    { label: "Agent Orchestra", href: "#agents", icon: BookOpen },
    { label: "Documentation", href: "#docs", icon: FileText },
  ];

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 glass-card border-b border-border/30">
      <div className="container mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <a href="#" className="flex items-center gap-3 group">
            <div className="relative">
              <Brain className="h-8 w-8 text-primary transition-transform group-hover:scale-110" />
              <div className="absolute inset-0 bg-primary/30 blur-xl opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
            <span className="text-xl font-display font-bold gradient-text">
              Memoria Scholae
            </span>
          </a>

          {/* Nav Links */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                className="flex items-center gap-2 px-4 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors rounded-lg hover:bg-muted/50"
              >
                <link.icon className="h-4 w-4" />
                {link.label}
              </a>
            ))}
          </div>

          {/* CTA */}
          <div className="flex items-center gap-3">
            <a
              href="https://github.com/lucylow/memoria-scholae"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="ghost" size="sm" className="gap-2">
                <Github className="h-4 w-4" />
                <span className="hidden sm:inline">GitHub</span>
              </Button>
            </a>
            <Button size="sm" className="btn-primary gap-2">
              <Cpu className="h-4 w-4" />
              Try Demo
            </Button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
