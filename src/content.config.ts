import { defineCollection, z } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';
import { glob } from 'astro/loaders';

const layerSchema = z.object({
	position: z.number(),
	name: z.string(),
	material: z.string(),
	thickness_mm: z.number(),
	function: z.string(),
});

const elementSchema = z.object({
	name: z.string(),
	ifc_class: z.string(),
	description: z.string(),
	total_thickness_mm: z.number(),
	u_value: z.number(),
	fire_rating: z.string(),
	tags: z.array(z.string()),
	layers: z.array(layerSchema),
});

export const collections = {
	docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
	elements: defineCollection({
		loader: glob({ pattern: '**/*.{yaml,yml}', base: './src/content/elements' }),
		schema: elementSchema,
	}),
};
