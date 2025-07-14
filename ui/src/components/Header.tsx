import React from "react";
import { Github } from "lucide-react";

interface HeaderProps {
  glassStyle: string;
}

const Header: React.FC<HeaderProps> = ({ glassStyle }) => {
  const handleImageError = (
    e: React.SyntheticEvent<HTMLImageElement, Event>
  ) => {
    console.error("Failed to load Tavily logo");
    console.log("Image path:", e.currentTarget.src);
    e.currentTarget.style.display = "none";
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-[30vh] mb-32 pt-[15vh]">
      <div className="text-center">
        <h1 className="text-[58px] font-medium text-[#1a202c] font-['Sora'] tracking-[-1px] leading-[52px] text-center mx-auto antialiased">
          Brand Reputation Check
        </h1>
        <p className="text-gray-600 text-lg font-['Sora'] mt-4">
          Measure social feedback to quantify trust, loyalty, and reputation
          trends
        </p>
      </div>
    </div>
  );
};

export default Header;
