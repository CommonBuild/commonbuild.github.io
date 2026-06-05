/**
 * Centrale data-toegang voor bouwelementen, lagen en materialen.
 *
 * Import de drie YAML-bestanden en exporteer getypte arrays + een
 * helper die alles joined tot verrijkte ElementRecord-objecten.
 *
 * Gebruik in Astro frontmatter:
 *   import { getElements, getElementById } from '../../data/index.ts';
 */

import rawElements from './elements.yaml';
import rawLayers   from './layers.yaml';
import rawMaterials from './materials.yaml';

// ── Types ─────────────────────────────────────────────────────────────────────

export interface MaterialRecord {
  id: string;
  name: string;
  category: string;
  description?: string;
  unit: 'm²' | 'lm' | 'm³' | 'kg' | 'stuk';
  price_per_unit?: number;
  price_currency: string;
  ifc_material_name?: string;
  supplier?: string;
  supplier_url?: string;
  tags: string[];
}

export interface LayerRecord {
  element_id: string;
  position: number;
  name: string;
  material_id?: string;
  thickness_mm: number;
  function: string;
}

export interface ElementRecord {
  id: string;
  name: string;
  category: 'walls' | 'floors' | 'roofs';
  subcategory?: 'external' | 'internal' | 'flat' | 'sloped';
  ifc_class: string;
  description?: string;
  total_thickness_mm: number;
  u_value: number;
  fire_rating: string;
  tags: string[];
}

// Laag verrijkt met materiaaldata
export interface EnrichedLayer extends LayerRecord {
  material: MaterialRecord | null;
}

// Element verrijkt met gesorteerde, verrijkte lagen
export interface EnrichedElement extends ElementRecord {
  layers: EnrichedLayer[];
}

// ── Ruwe data ─────────────────────────────────────────────────────────────────

export const materials = rawMaterials as MaterialRecord[];
export const layers    = rawLayers    as LayerRecord[];
export const elements  = rawElements  as ElementRecord[];

// ── Lookup maps ───────────────────────────────────────────────────────────────

export const materialById  = new Map(materials.map(m => [m.id, m]));
export const layersByElement = layers.reduce<Record<string, LayerRecord[]>>((acc, l) => {
  (acc[l.element_id] ??= []).push(l);
  return acc;
}, {});

// ── Join-helpers ──────────────────────────────────────────────────────────────

function enrichLayers(elementId: string): EnrichedLayer[] {
  return (layersByElement[elementId] ?? [])
    .sort((a, b) => a.position - b.position)
    .map(l => ({ ...l, material: l.material_id ? (materialById.get(l.material_id) ?? null) : null }));
}

export function getElements(filterFn?: (e: ElementRecord) => boolean): EnrichedElement[] {
  const filtered = filterFn ? elements.filter(filterFn) : elements;
  return filtered.map(e => ({ ...e, layers: enrichLayers(e.id) }));
}

export function getElementById(id: string): EnrichedElement | undefined {
  const e = elements.find(el => el.id === id);
  if (!e) return undefined;
  return { ...e, layers: enrichLayers(e.id) };
}
