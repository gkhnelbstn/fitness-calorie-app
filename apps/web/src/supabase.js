// Supabase istemcisi — env yoksa null (mock/prototip modu sürer).
// VITE_SUPABASE_URL + VITE_SUPABASE_ANON_KEY build sırasında gömülür (anon key public'tir;
// güvenlik backend JWT doğrulaması + RLS'tedir).
import { createClient } from '@supabase/supabase-js';

const url = import.meta.env.VITE_SUPABASE_URL || '';
const anonKey = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const supabase =
  url && anonKey
    ? createClient(url, anonKey, {
        auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true },
      })
    : null;

window.supabase = supabase;
