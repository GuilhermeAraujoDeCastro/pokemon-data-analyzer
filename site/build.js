// Build de producao: empacota js/main.js com esbuild (resolve os imports
// dos outros modulos num arquivo so'), minifica o CSS tambem com esbuild, e
// ofusca o JS resultante com javascript-obfuscator -- mesmo padrao usado
// nos outros sites do portfolio, pra quem abrir o F12 no site publicado
// nao ver o codigo fonte legivel de cara.
//
// index.html e data/*.json sao so' copiados pra dist/ (JSON e' dado
// publico, nao faz sentido ofuscar).
//
// Rodar: npm install && npm run build
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import * as esbuild from "esbuild";
import JavaScriptObfuscator from "javascript-obfuscator";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const DIST = path.join(__dirname, "dist");
const COPY_ENTRIES = ["index.html", "data", "og.png"];

async function copyRecursive(src, dest) {
  const stat = await fs.stat(src).catch(() => null);
  if (!stat) return;
  if (stat.isDirectory()) {
    await fs.mkdir(dest, { recursive: true });
    for (const entry of await fs.readdir(src)) {
      await copyRecursive(path.join(src, entry), path.join(dest, entry));
    }
  } else {
    await fs.mkdir(path.dirname(dest), { recursive: true });
    await fs.copyFile(src, dest);
  }
}

function obfuscate(code) {
  return JavaScriptObfuscator.obfuscate(code, {
    compact: true,
    controlFlowFlattening: true,
    controlFlowFlatteningThreshold: 0.6,
    deadCodeInjection: true,
    deadCodeInjectionThreshold: 0.2,
    stringArray: true,
    stringArrayEncoding: ["base64"],
    stringArrayThreshold: 0.75,
    identifierNamesGenerator: "hexadecimal",
    selfDefending: false,
    disableConsoleOutput: false,
  }).getObfuscatedCode();
}

async function main() {
  await fs.rm(DIST, { recursive: true, force: true });
  await fs.mkdir(DIST, { recursive: true });

  for (const entry of COPY_ENTRIES) {
    await copyRecursive(path.join(__dirname, entry), path.join(DIST, entry));
  }

  const jsBundle = await esbuild.build({
    entryPoints: [path.join(__dirname, "js", "main.js")],
    bundle: true,
    format: "iife",
    target: "es2019",
    write: false,
    legalComments: "none",
  });
  await fs.mkdir(path.join(DIST, "js"), { recursive: true });
  await fs.writeFile(path.join(DIST, "js", "main.js"), obfuscate(jsBundle.outputFiles[0].text), "utf8");

  const cssBundle = await esbuild.build({
    entryPoints: [path.join(__dirname, "css", "styles.css")],
    bundle: true,
    minify: true,
    write: false,
    legalComments: "none",
  });
  await fs.mkdir(path.join(DIST, "css"), { recursive: true });
  await fs.writeFile(path.join(DIST, "css", "styles.css"), cssBundle.outputFiles[0].text, "utf8");

  console.log("Build concluido em dist/: JS empacotado e ofuscado, CSS minificado.");
}

main().catch((err) => {
  console.error("Falha no build:", err);
  process.exit(1);
});
