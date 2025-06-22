import { SVGProps } from "react";
import { IdType, Edge as VisEdge, Node as VisNode } from 'vis-network';

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export interface Message {
  id: string;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
  file?: File;
  isError?: boolean;
  graph_dir_path: string;
}

export interface Playbook {
  id: string;
  name: string;
  type: 'malware' | 'exploit';
  description: string;
  indicators: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface GraphNode extends VisNode {
  id: IdType;
  label: string;
  type?: 'threat' | 'entity' | 'indicator';
  connections?: string[];
  color?: string;
  shape?: string;
  size?: number;
  title?: string;
}

export interface GraphEdge extends VisEdge {
  from: IdType;
  to: IdType;
  label?: string;
  title?: string;
  smooth?: {
    enabled: boolean;
    type: string;
    roundness: number;
  };
}

export interface GraphData {
  nodes: GraphNode[];
  edges: GraphEdge[];
}

export interface GraphFoldersNamesResponse {
  folders: string[];
}


export interface MTAPlayBook {
  sample_url: string;
  malware_name: string | string[];
  hunt_goal: string;
  generated_prompt: string
}