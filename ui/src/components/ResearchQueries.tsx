import React from "react";
import { ChevronDown, ChevronUp } from "lucide-react";
import { ResearchQueriesProps } from "../types";

const ResearchQueries: React.FC<ResearchQueriesProps> = ({
  queries,
  streamingQueries,
  isExpanded,
  onToggleExpand,
  isResetting,
  glassStyle,
}) => {
  const glassCardStyle = `${glassStyle} rounded-2xl p-6`;
  const fadeInAnimation = "transition-all duration-300 ease-in-out";

  return (
    <div
      className={`${glassCardStyle} ${fadeInAnimation} ${
        isResetting
          ? "opacity-0 transform -translate-y-4"
          : "opacity-100 transform translate-y-0"
      } font-['DM_Sans']`}
    >
      <div
        className="flex items-center justify-between cursor-pointer"
        onClick={onToggleExpand}
      >
        <h2 className="text-xl font-semibold text-gray-900">
          Found Social Media Address
        </h2>
        <button className="text-gray-600 hover:text-gray-900 transition-colors">
          {isExpanded ? (
            <ChevronUp className="h-6 w-6" />
          ) : (
            <ChevronDown className="h-6 w-6" />
          )}
        </button>
      </div>

      <div
        className={`overflow-hidden transition-all duration-500 ease-in-out ${
          isExpanded ? "mt-4 max-h-[1000px] opacity-100" : "max-h-0 opacity-0"
        }`}
      >
        <div className={`${glassStyle} rounded-xl p-4 w-full`}>
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Links</h3>
          <div className="space-y-3">
            {/* Show up to 3 streaming queries first */}
            {Object.entries(streamingQueries)
              .slice(0, 3)
              .map(([key, query]) => (
                <div
                  key={key}
                  className="backdrop-filter backdrop-blur-lg bg-white/80 border border-[#468BFF]/30 rounded-lg p-3"
                >
                  <span className="text-gray-600">{query.text}</span>
                </div>
              ))}

            {/* If streaming < 3, fill with completed queries */}
            {queries
              .slice(0, 3 - Object.keys(streamingQueries).length)
              .map((query, idx) => (
                <div
                  key={idx}
                  className="backdrop-filter backdrop-blur-lg bg-white/80 border border-gray-200 rounded-lg p-3"
                >
                  <span className="text-gray-600">{query.text}</span>
                </div>
              ))}
          </div>
        </div>
      </div>

      {!isExpanded && (
        <div className="mt-2 text-sm text-gray-600">
          {queries.length} social media links found
        </div>
      )}
    </div>
  );
};

export default ResearchQueries;
