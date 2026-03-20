-- MedResearch Mind — Complete Database Schema
-- Run in Supabase SQL Editor

CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================
-- User profiles
-- ============================================================
CREATE TABLE user_profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  full_name TEXT,
  institution TEXT,
  research_focus TEXT[],
  clinical_background BOOLEAN DEFAULT FALSE,
  plan TEXT DEFAULT 'free' CHECK (plan IN ('free','pro','lab')),
  papers_count INT DEFAULT 0,
  queries_count INT DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE user_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile" ON user_profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile" ON user_profiles FOR UPDATE USING (auth.uid() = id);
CREATE POLICY "Users can insert own profile" ON user_profiles FOR INSERT WITH CHECK (auth.uid() = id);

-- ============================================================
-- Sources (all input types)
-- ============================================================
CREATE TABLE sources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  source_type TEXT NOT NULL CHECK (source_type IN
    ('pdf','arxiv','pubmed','biorxiv','youtube',
     'blog','github','clinical_trial','url')),
  source_url TEXT,
  local_filename TEXT,
  title TEXT,
  authors TEXT[],
  institution TEXT,
  journal_or_venue TEXT,
  published_date DATE,
  processing_status TEXT DEFAULT 'pending'
    CHECK (processing_status IN ('pending','processing','completed','failed')),
  processing_error TEXT,
  raw_content TEXT,
  imaging_modalities TEXT[],
  anatomies TEXT[],
  conditions TEXT[],
  architectures TEXT[],
  datasets_used TEXT[],
  metrics_reported TEXT[],
  techniques TEXT[],
  limitations TEXT[],
  future_work TEXT[],
  clinical_relevance TEXT DEFAULT 'unknown'
    CHECK (clinical_relevance IN ('high','medium','low','unknown')),
  mesh_terms TEXT[],
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own sources" ON sources
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Chunks with vectors
-- ============================================================
CREATE TABLE chunks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  source_id UUID REFERENCES sources ON DELETE CASCADE NOT NULL,
  user_id UUID REFERENCES auth.users NOT NULL,
  content TEXT NOT NULL,
  page_number INT,
  section_name TEXT,
  chunk_index INT,
  embedding VECTOR(768),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE chunks ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own chunks" ON chunks
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Semantic memory — medical knowledge graph nodes
-- ============================================================
CREATE TABLE semantic_nodes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  entity_type TEXT NOT NULL CHECK (entity_type IN
    ('imaging_modality','anatomy','condition',
     'architecture','dataset','metric',
     'technique','limitation','finding')),
  entity_name TEXT NOT NULL,
  embedding VECTOR(768),
  source_ids UUID[],
  frequency INT DEFAULT 1,
  properties JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, entity_type, entity_name)
);

ALTER TABLE semantic_nodes ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own nodes" ON semantic_nodes
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Semantic edges
-- ============================================================
CREATE TABLE semantic_edges (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  source_node_id UUID REFERENCES semantic_nodes ON DELETE CASCADE,
  target_node_id UUID REFERENCES semantic_nodes ON DELETE CASCADE,
  relationship TEXT NOT NULL,
  weight FLOAT DEFAULT 1.0,
  source_paper_ids UUID[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE semantic_edges ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own edges" ON semantic_edges
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Sessions (episodic memory)
-- ============================================================
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  session_name TEXT,
  clinical_focus TEXT,
  session_summary TEXT,
  sources_accessed UUID[],
  queries_made TEXT[],
  gaps_explored TEXT[],
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  is_active BOOLEAN DEFAULT TRUE
);

ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own sessions" ON sessions
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Queries log
-- ============================================================
CREATE TABLE queries (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  session_id UUID REFERENCES sessions,
  query_text TEXT NOT NULL,
  query_type TEXT CHECK (query_type IN
    ('gap','qa','compare','experiment','extraction','clinical')),
  response TEXT,
  citations JSONB DEFAULT '[]',
  confidence FLOAT,
  sources_used UUID[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own queries" ON queries
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Gap reports
-- ============================================================
CREATE TABLE gap_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  source_ids UUID[],
  clinical_topic TEXT,
  gaps JSONB DEFAULT '[]',
  experiment_proposals JSONB DEFAULT '[]',
  report_pdf_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE gap_reports ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own gap reports" ON gap_reports
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Training data (THE MOAT)
-- ============================================================
CREATE TABLE training_data (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  interaction_type TEXT NOT NULL,
  input_context TEXT,
  system_output TEXT,
  outcome TEXT CHECK (outcome IN
    ('accepted','rejected','modified','ignored')),
  user_modification TEXT,
  modality TEXT,
  anatomy TEXT,
  condition TEXT,
  technique TEXT,
  quality_score FLOAT,
  user_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- No RLS on training_data — accessed by service key only

-- ============================================================
-- User patterns (procedural memory)
-- ============================================================
CREATE TABLE user_patterns (
  user_id UUID REFERENCES auth.users PRIMARY KEY,
  clinical_areas TEXT[],
  preferred_modalities TEXT[],
  interpretability_focus BOOLEAN DEFAULT FALSE,
  federated_focus BOOLEAN DEFAULT FALSE,
  edge_deployment_focus BOOLEAN DEFAULT FALSE,
  rare_disease_focus BOOLEAN DEFAULT FALSE,
  interaction_patterns JSONB DEFAULT '{}',
  last_updated TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE user_patterns ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own patterns" ON user_patterns
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Waitlist
-- ============================================================
CREATE TABLE waitlist (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  full_name TEXT,
  institution TEXT,
  clinical_role TEXT,
  research_area TEXT,
  referral_source TEXT,
  signed_up_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Comparison reports
-- ============================================================
CREATE TABLE comparisons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  source_ids UUID[],
  table_data JSONB DEFAULT '[]',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE comparisons ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own comparisons" ON comparisons
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Experiment proposals
-- ============================================================
CREATE TABLE experiments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users NOT NULL,
  gap_description TEXT,
  pico JSONB DEFAULT '{}',
  datasets JSONB DEFAULT '[]',
  architecture TEXT,
  evaluation_protocol TEXT,
  challenges TEXT[],
  compute_estimate TEXT,
  ablations TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE experiments ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own experiments" ON experiments
  FOR ALL USING (auth.uid() = user_id);

-- ============================================================
-- Vector similarity search function
-- ============================================================
CREATE OR REPLACE FUNCTION match_chunks(
  query_embedding VECTOR(768),
  match_count INT DEFAULT 10,
  filter_user_id UUID DEFAULT NULL,
  filter_source_ids UUID[] DEFAULT NULL
)
RETURNS TABLE (
  id UUID,
  source_id UUID,
  content TEXT,
  page_number INT,
  section_name TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    c.id,
    c.source_id,
    c.content,
    c.page_number,
    c.section_name,
    1 - (c.embedding <=> query_embedding) AS similarity
  FROM chunks c
  WHERE
    (filter_user_id IS NULL OR c.user_id = filter_user_id)
    AND (filter_source_ids IS NULL OR c.source_id = ANY(filter_source_ids))
  ORDER BY c.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- ============================================================
-- Indexes
-- ============================================================
CREATE INDEX ON chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX ON semantic_nodes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

CREATE INDEX idx_sources_user ON sources(user_id, created_at DESC);
CREATE INDEX idx_sources_modalities ON sources USING gin(imaging_modalities);
CREATE INDEX idx_sources_anatomies ON sources USING gin(anatomies);
CREATE INDEX idx_sources_conditions ON sources USING gin(conditions);
CREATE INDEX idx_chunks_source ON chunks(source_id, chunk_index);
CREATE INDEX idx_queries_user ON queries(user_id, created_at DESC);
CREATE INDEX idx_sessions_user ON sessions(user_id, is_active);
CREATE INDEX idx_training_type ON training_data(interaction_type, outcome);
CREATE INDEX idx_training_medical ON training_data(modality, anatomy, condition);
CREATE INDEX idx_semantic_nodes_user ON semantic_nodes(user_id, entity_type);
CREATE INDEX idx_semantic_edges_source ON semantic_edges(source_node_id);
CREATE INDEX idx_semantic_edges_target ON semantic_edges(target_node_id);
