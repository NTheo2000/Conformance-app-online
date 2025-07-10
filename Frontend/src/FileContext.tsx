import React, { createContext, useState, useContext, ReactNode } from 'react';

interface ExtractedElement {
  id: string;
  name: string;
}

interface TraceFitness {
  trace: string;
  conformance: number;
}
interface TraceSequence {
  trace: string;
  sequence: string[];
}
interface OutcomeBin {
  range: [number, number];
  traceCount: number;
  percentageEndingCorrectly: number;
}
interface RoleConformance {
  role: string;
  averageConformance: number;
  traceCount: number;
}
interface ResourceConformance {
  resource: string;
  avg_conformance: number;
  traceCount: number;
}
export interface UniqueSequenceBin {
  bin: number;
  uniqueSequences: number;
  sequences: string[][];
}



interface ConformanceBin {
  averageConformance: number;
  traceCount: number;
}

export interface ActivityDeviation {
  name: string;
  skipped: number;
  inserted: number;
  skipped_percent: number;
  inserted_percent: number;
}

interface ActivityDeviationResult {
  deviations: ActivityDeviation[];
  total_traces: number;
}

interface FileContextType {
  // File contents
  bpmnFileContent: string | null;
  xesFileContent: string | null;

  
  amountConformanceData: any[];
  setAmountConformanceData: React.Dispatch<React.SetStateAction<any[]>>;

  // Extracted BPMN elements
  extractedElements: ExtractedElement[];

  // Conformance data
  fitnessData: TraceFitness[];
  conformanceBins: ConformanceBin[];

  resourceConformance: ResourceConformance[];
setResourceConformance: React.Dispatch<React.SetStateAction<ResourceConformance[]>>;


  // Activity deviation stats
  activityDeviations: ActivityDeviationResult;
  outcomeBins: OutcomeBin[];
 desiredOutcomes: string[];
 roleConformance: RoleConformance[];
 uniqueSequences: UniqueSequenceBin[];
setUniqueSequences: React.Dispatch<React.SetStateAction<UniqueSequenceBin[]>>;


  // Setters
  setBpmnFileContent: (content: string | null) => void;
  setXesFileContent: (content: string | null) => void;
  setExtractedElements: (elements: ExtractedElement[]) => void;
  setFitnessData: (data: TraceFitness[]) => void;
  setConformanceBins: (bins: ConformanceBin[]) => void;
  setActivityDeviations: (data: ActivityDeviationResult) => void;
  setOutcomeBins: (bins: OutcomeBin[]) => void;
  setDesiredOutcomes: (outcomes: string[]) => void;
  setRoleConformance: (data: RoleConformance[]) => void;
  traceSequences: TraceSequence[];
setTraceSequences: React.Dispatch<React.SetStateAction<TraceSequence[]>>;


  // Outcome distribution

}

// Create context
const FileContext = createContext<FileContextType | undefined>(undefined);

// Provider component
export const FileProvider = ({ children }: { children: ReactNode }) => {
  const [bpmnFileContent, setBpmnFileContent] = useState<string | null>(null);
  const [xesFileContent, setXesFileContent] = useState<string | null>(null);
  const [extractedElements, setExtractedElements] = useState<ExtractedElement[]>([]);
  const [fitnessData, setFitnessData] = useState<TraceFitness[]>([]);
  const [traceSequences, setTraceSequences] = useState<TraceSequence[]>([]);
  const [conformanceBins, setConformanceBins] = useState<ConformanceBin[]>([]);
  const [activityDeviations, setActivityDeviations] = useState<ActivityDeviationResult>({
    deviations: [],
    total_traces: 0
  });
  const [uniqueSequences, setUniqueSequences] = useState<UniqueSequenceBin[]>([]);
  const [amountConformanceData, setAmountConformanceData] = useState<any[]>([]);
  const [resourceConformance, setResourceConformance] = useState<ResourceConformance[]>([]);



  
  const [outcomeBins, setOutcomeBins] = useState<OutcomeBin[]>([]);
  const [desiredOutcomes, setDesiredOutcomes] = useState<string[]>([]);
  const [roleConformance, setRoleConformance] = useState<RoleConformance[]>([]);




  return (
    <FileContext.Provider
      value={{
        bpmnFileContent,
        xesFileContent,
        extractedElements,
        setBpmnFileContent,
        setXesFileContent,
        setExtractedElements,
        fitnessData,
        setFitnessData,
        conformanceBins,
        setConformanceBins,
        activityDeviations,
        setActivityDeviations,
        outcomeBins,
setOutcomeBins,
desiredOutcomes,
setDesiredOutcomes,
roleConformance,
  setRoleConformance,
setUniqueSequences,
  uniqueSequences,
   amountConformanceData,
  setAmountConformanceData,
  resourceConformance,
setResourceConformance,
traceSequences,
setTraceSequences,


      }}
    >
      {children}
    </FileContext.Provider>
  );
};

// Hook for using context
export const useFileContext = (): FileContextType => {
  const context = useContext(FileContext);
  if (!context) {
    throw new Error('useFileContext must be used within a FileProvider');
  }
  return context;
};





