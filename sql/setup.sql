-- Estrutura reproduzivel do projeto NASA CMR.
-- Use este script em projeto Supabase novo. No atual ele preserva os dados.
CREATE TABLE IF NOT EXISTS public.colecoes (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  cmr_id TEXT NOT NULL UNIQUE,
  title TEXT, short_name TEXT, version_id TEXT, data_center TEXT,
  processing_level TEXT, collection_type TEXT,
  time_start TIMESTAMPTZ, updated_at TIMESTAMPTZ,
  platforms JSONB, organizations JSONB, summary TEXT,
  online_access BOOLEAN, raw_data JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS public.execucoes (
  id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  executado_em TIMESTAMPTZ DEFAULT NOW(),
  registros_processados INTEGER DEFAULT 0,
  lotes INTEGER DEFAULT 0, erros INTEGER DEFAULT 0,
  status TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS public.controle_pipeline (
  nome TEXT PRIMARY KEY,
  proxima_pagina INTEGER NOT NULL DEFAULT 1,
  atualizado_em TIMESTAMPTZ DEFAULT NOW()
);

INSERT INTO public.controle_pipeline (nome, proxima_pagina)
VALUES ('cmr', 1) ON CONFLICT (nome) DO NOTHING;

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conname = 'execucoes_status_check'
      AND conrelid = 'public.execucoes'::regclass
  ) THEN
    ALTER TABLE public.execucoes ADD CONSTRAINT execucoes_status_check
      CHECK (status IN ('concluido', 'erro_parcial', 'erro_critico'));
  END IF;
END $$;

ALTER TABLE public.colecoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.execucoes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.controle_pipeline ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Leitura publica colecoes" ON public.colecoes;
CREATE POLICY "Leitura publica colecoes" ON public.colecoes
FOR SELECT TO anon, authenticated USING (true);
DROP POLICY IF EXISTS "Leitura publica execucoes" ON public.execucoes;
CREATE POLICY "Leitura publica execucoes" ON public.execucoes
FOR SELECT TO anon, authenticated USING (true);

REVOKE ALL ON public.controle_pipeline FROM anon, authenticated;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
ON public.colecoes, public.execucoes FROM anon, authenticated;
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT SELECT ON public.colecoes, public.execucoes TO anon, authenticated;
GRANT ALL ON public.colecoes, public.execucoes, public.controle_pipeline TO service_role;

-- Nunca disponibilize a chave SERVICE_ROLE no front-end.
