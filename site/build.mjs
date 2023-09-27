import { argv } from 'node:process'
import * as esbuild from 'esbuild'

switch(argv[2]) {
	case "dev":
		await dev()
		break
	case "prod":
		await prod()
		break
	default:
		print("USAGE: build dev|prod")
}

async function dev() {

	let ctx = await esbuild.context({
  		entryPoints: ['./src/main.jsx', './src/index.html'],
		loader: {
			'.html': 'text'
		},
  		outdir: 'srv'
	})

	await ctx.watch()

	let { host, port } = await ctx.serve({
		servedir: 'srv',
		host: 'localhost',
		port: '8000'
	})
}

async function prod() {
	let build = await esbuild.build({
  		entryPoints: ['./src/main.jsx', './src/index.html'],
		loader: {
			'.html': 'text'
		},
		target: [
			'es6',
			'chrome',
			'edge',
			'firefox',
			'ie',
			'ios',
			'opera',
			'safari'
		],
		drop: ['console', 'debugger'],
		dropLabes: ['TEST'],
		minify: true,
		treeShaking: true,
		bundle: true,
		outdir: 'build',
	})
}
