import { defineCollection } from 'astro:content';
import { docsLoader } from '@astrojs/starlight/loaders';
import { docsSchema } from '@astrojs/starlight/schema';

// Alleen Starlight docs blijven als content collection.
// Bouwelementen, lagen en materialen zitten in src/data/*.yaml
// en worden direct geïmporteerd via de Vite YAML plugin.
export const collections = {
	docs: defineCollection({ loader: docsLoader(), schema: docsSchema() }),
};
