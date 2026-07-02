import fs from "fs"
import path from "path"
function walk(d){const r=[];for(const e of fs.readdirSync(d,{withFileTypes:true})){const p=path.join(d,e.name);if(e.isDirectory())r.push(...walk(p));else if(e.name.endsWith(".vue"))r.push(p.replace(/\\/g,"/"))}return r}
const all=new Set(["src/views/teacher","src/components/teacher"].flatMap(d=>walk(d)))
const withI18n=new Set(), ar=new Set()
for(const f of all){const c=fs.readFileSync(f,"utf8");if(c.includes("$t(")||c.includes("useI18n"))withI18n.add(f);if(/[\u0600-\u06FF]/.test(c))ar.add(f)}
console.log("Total vue:",all.size)
console.log("With i18n:",withI18n.size)
console.log("With Arabic:",ar.size)
