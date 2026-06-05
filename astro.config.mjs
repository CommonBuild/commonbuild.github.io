// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import { readFileSync } from 'node:fs';
import { load as yamlLoad } from 'js-yaml';

/** Vite plugin: importeer *.yaml bestanden als JS-module (geen extra dependency). */
const yamlPlugin = {
	name: 'vite-yaml',
	transform(_src, id) {
		if (!id.endsWith('.yaml') && !id.endsWith('.yml')) return;
		const parsed = yamlLoad(readFileSync(id, 'utf8'));
		return { code: `export default ${JSON.stringify(parsed)};`, map: null };
	},
};

export default defineConfig({
	site: 'https://commonbuild.github.io',
	vite: { plugins: [yamlPlugin] },
	integrations: [
		starlight({
			title: 'Commonbuild',
			description: 'Open source ecological self-build documentation and building element library.',
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/commonbuild' },
			],
			sidebar: [
				{ label: 'Home', link: '/' },
				{ label: 'Uitbouw Configurator', link: '/configurator/' },
				{
					label: 'Element Library',
					items: [
						{ label: 'All Elements', link: '/elements/' },
						{
							label: 'Walls',
							items: [
								{ label: 'External Walls', link: '/elements/?category=walls&sub=external' },
								{ label: 'Internal Walls', link: '/elements/?category=walls&sub=internal' },
							],
						},
						{ label: 'Floors', link: '/elements/?category=floors' },
						{
							label: 'Roofs',
							items: [
								{ label: 'Flat Roofs', link: '/elements/?category=roofs&sub=flat' },
								{ label: 'Sloped Roofs', link: '/elements/?category=roofs&sub=sloped' },
							],
						},
					],
				},
				{
					label: 'Guides',
					items: [{ autogenerate: { directory: 'guides' } }],
				},
			],
			customCss: ['./src/styles/global.css'],
		}),
	],
});
