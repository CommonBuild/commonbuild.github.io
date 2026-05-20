// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

export default defineConfig({
	site: 'https://commonbuild.github.io',
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
