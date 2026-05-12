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
				{
					label: 'Element Library',
					items: [
						{ label: 'All Elements', link: '/elements/' },
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
