/* global console, process */

import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join } from "node:path";

const distAssets = join(process.cwd(), "dist", "assets");
if (!existsSync(distAssets)) throw new Error("Build dist/assets before checking Button CSS");

const cssFile = readdirSync(distAssets).find((file) => /^index-.*\.css$/.test(file));
if (!cssFile) throw new Error("Could not locate the Vite CSS bundle");

const css = readFileSync(join(distAssets, cssFile), "utf8");
const required = [".h-8", ".h-6", ".h-7", ".h-9", ".size-6", ".size-7", ".size-8", ".size-9", ":focus-visible"];
const missing = required.filter((selector) => !css.includes(selector));
const unsupported = ["has-data", "in-data", "ring-3", "active:not-aria", "aria-invalid"].filter((pattern) => css.includes(pattern));

if (missing.length || unsupported.length) {
  throw new Error(`Button CSS contract failed. Missing=${missing.join(",") || "none"}; Unsupported=${unsupported.join(",") || "none"}`);
}

console.log(`Button CSS contract passed: ${cssFile}`);
