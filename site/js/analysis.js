// Mesmas perguntas de pokedata/analysis.py, portadas pra JS puro -- assim
// os filtros (geracao/tipo/busca) recalculam tudo no navegador, sem
// precisar de um backend pra reprocessar o dataset.
export const STAT_KEYS = ["hp", "attack", "defense", "special_attack", "special_defense", "speed"];

export function typeCombinationCounts(rows) {
  const counts = new Map();
  for (const row of rows) {
    const key = `${capitalize(row.type_1)} / ${capitalize(row.type_2 || "Nenhum")}`;
    counts.set(key, (counts.get(key) || 0) + 1);
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1]);
}

export function rarestTypeCombination(rows) {
  const counts = typeCombinationCounts(rows);
  if (counts.length === 0) return null;
  const minimum = Math.min(...counts.map(([, count]) => count));
  const tied = counts.filter(([, count]) => count === minimum).sort((a, b) => a[0].localeCompare(b[0]));
  return { combo: tied[0][0], count: minimum };
}

export function averageStatByType(rows, stat) {
  const sums = new Map();
  const counts = new Map();
  for (const row of rows) {
    sums.set(row.type_1, (sums.get(row.type_1) || 0) + row[stat]);
    counts.set(row.type_1, (counts.get(row.type_1) || 0) + 1);
  }
  return [...sums.entries()]
    .map(([type, sum]) => [type, sum / counts.get(type)])
    .sort((a, b) => b[1] - a[1]);
}

export function fastestType(rows) {
  const averages = averageStatByType(rows, "speed");
  return averages.length ? { type: averages[0][0], avgSpeed: averages[0][1] } : null;
}

export function pearsonCorrelation(xs, ys) {
  const n = xs.length;
  if (n === 0) return NaN;
  const meanX = xs.reduce((a, b) => a + b, 0) / n;
  const meanY = ys.reduce((a, b) => a + b, 0) / n;
  let cov = 0, varX = 0, varY = 0;
  for (let i = 0; i < n; i++) {
    const dx = xs[i] - meanX;
    const dy = ys[i] - meanY;
    cov += dx * dy;
    varX += dx * dx;
    varY += dy * dy;
  }
  if (varX === 0 || varY === 0) return NaN; // sem variacao -> correlacao indefinida
  return cov / Math.sqrt(varX * varY);
}

export function correlationBetween(rows, keyA, keyB) {
  return pearsonCorrelation(rows.map((r) => r[keyA]), rows.map((r) => r[keyB]));
}

export function correlationMatrix(rows) {
  const columns = [...STAT_KEYS, "height_m", "weight_kg"];
  return columns.map((a) => columns.map((b) => correlationBetween(rows, a, b)));
}

export function topNByStat(rows, stat, n = 10) {
  return [...rows].sort((a, b) => b[stat] - a[stat]).slice(0, n);
}

export function findOutliers(rows, stat, k = 1.5) {
  const values = [...rows.map((r) => r[stat])].sort((a, b) => a - b);
  if (values.length < 4) return [];
  const quantile = (p) => {
    const pos = (values.length - 1) * p;
    const base = Math.floor(pos);
    const rest = pos - base;
    return values[base + 1] !== undefined ? values[base] + rest * (values[base + 1] - values[base]) : values[base];
  };
  const q1 = quantile(0.25);
  const q3 = quantile(0.75);
  const iqr = q3 - q1;
  const lower = q1 - k * iqr;
  const upper = q3 + k * iqr;
  return rows.filter((r) => r[stat] < lower || r[stat] > upper).sort((a, b) => b[stat] - a[stat]);
}

function capitalize(text) {
  return text ? text.charAt(0).toUpperCase() + text.slice(1) : text;
}
