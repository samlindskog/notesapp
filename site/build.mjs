import { argv } from 'node:process';
import { sassPlugin } from 'esbuild-sass-plugin';
import * as esbuild from 'esbuild';
import { SourceMap } from 'node:module';

switch (argv[2]) {
   case 'dev':
      await dev();
      break;
   case 'prod':
      await prod();
      break;
   default:
      print('USAGE: build dev|prod');
}

async function dev() {
   let ctx = await esbuild.context({
      entryPoints: ['./src/main.jsx'],
      loader: {
         '.html': 'text',
         '.woff': 'text',
         '.woff2': 'text',
      },
      outdir: 'srv',
      bundle: true,
      logLevel: 'info',
      plugins: [sassPlugin()],
   });

   await ctx.watch();

   let { host, port } = await ctx.serve({
      servedir: 'srv',
      host: 'localhost',
      port: 8001,
      fallback: 'srv/index.html',
      onRequest: (args) => {
			console.log(Date.now())
         console.log(`path: ${args.path}`);
         console.log(`status: ${args.status}`);
      },
   });
}

async function prod() {
   let build = await esbuild.build({
      entryPoints: ['./src/main.jsx'],
      target: [
         'es6',
         'chrome',
         'edge',
         'firefox',
         'ie',
         'ios',
         'opera',
         'safari',
      ],
      drop: ['console', 'debugger'],
      dropLabes: ['TEST'],
      minify: true,
      treeShaking: true,
      bundle: true,
      outdir: 'build',
      logLevel: 'info',
   });
}
