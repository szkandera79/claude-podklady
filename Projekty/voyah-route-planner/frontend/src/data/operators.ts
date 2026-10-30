/** Sjednocení názvů provozovatelů na názvy tarifů (přepis vrp_data/operators.py). */
const ALIASES: [string, string][] = [
  ["prazska energetika", "PRE"], ["pre ", "PRE"], ["pre(", "PRE"], ["pre-", "PRE"],
  ["e.on", "E.ON"], ["eon", "E.ON"], ["cez", "ČEZ"], ["lidl", "Lidl"], ["kaufland", "Kaufland"],
  ["tesla", "Tesla"], ["ionity", "IONITY"], ["mol", "MOL"], ["shell", "Shell"], ["omv", "OMV"], ["orlen", "Orlen"],
  ["innogy", "innogy"], ["teplarny brno", "Teplárny Brno"], ["chargee", "Chargee"],
];
const plain = (s: string) => " " + s.normalize("NFKD").replace(/[̀-ͯ]/g, "").toLowerCase().trim() + " ";

export function normalizeOperator(name: string | undefined | null): string {
  if (!name) return "Neznámý";
  const p = plain(name);
  if (["pre", "pre (cz)"].includes(p.trim())) return "PRE";
  for (const [k, out] of ALIASES) if (p.includes(k)) return out;
  return name.trim();
}
