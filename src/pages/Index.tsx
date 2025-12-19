import Navbar from "@/components/Navbar";
import HeroSection from "@/components/HeroSection";
import TechStack from "@/components/TechStack";
import LiveDemo from "@/components/LiveDemo";
import AgentOrchestra from "@/components/AgentOrchestra";
import MemoryPanel from "@/components/MemoryPanel";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-background overflow-x-hidden">
      <Navbar />
      <HeroSection />
      <TechStack />
      <LiveDemo />
      <AgentOrchestra />
      <MemoryPanel />
      <Footer />
    </div>
  );
};

export default Index;
