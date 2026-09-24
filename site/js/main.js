import { initTheme } from "./theme.js";
import { generationForId } from "./generations.js";
import {
  STAT_KEYS,
  averageStatByType,
  correlationMatrix,
  fastestType,
  findOutliers,
  rarestTypeCombination,
  topNByStat,
  typeCombinationCounts,
} from "./analysis.js";
import { barChart, correlationHeatmap, scatterChart } from "./charts.js";

const CORRELATION_LABELS = [...STAT_KEYS, "height_m", "weight_kg"];

initTheme();

const state = { rows: [], generation: "", type: "", search: "" };

async function loadData() {
  const response = await fetch("data/pokemon.json");
  if (!response.ok) throw new Error(`Nao consegui carregar data/pokemon.json (${response.status})`);
  const rows = await response.json();
  return rows.map((row) => ({ ...row, generation: generationForId(row.id) }));
}

function populateFilters(rows) {
  const generationSelect = document.getElementById("filter-generation");
  const generations = [...new Set(rows.map((r) => r.generation).filter((g) => g !== null))].sort((a, b) => a - b);
  for (const gen of generations) {
    const option = document.createElement("option");
    option.value = String(gen);
    option.textContent = `Geracao ${gen}`;
    generationSelect.appendChild(option);
  }

  const typeSelect = document.getElementById("filter-type");
  const types = [...new Set(rows.flatMap((r) => [r.type_1, r.type_2]).filter((t) => t && t !== "Nenhum"))].sort();
  for (const type of types) {
    const option = document.createElement("option");
    option.value = type;
    option.textContent = type;
    typeSelect.appendChild(option);
  }
}

function applyFilters() {
  return state.rows.filter((row) => {
    if (state.generation && String(row.generation) !== state.generation) return false;
    if (state.type && row.type_1 !== state.type && row.type_2 !== state.type) return false;
    if (state.search && !row.name.toLowerCase().includes(state.search.toLowerCase())) return false;
    return true;
  });
}

function renderStats(rows) {
  const grid = document.getElementById("stats-grid");
  grid.innerHTML = "";

  const cards = [];
  cards.push({ label: "Total de Pokémon", value: String(rows.length) });

  const rarest = rarestTypeCombination(rows);
  if (rarest) cards.push({ label: "Combinação mais rara", value: rarest.combo, sub: `${rarest.count} Pokémon` });

  const fastest = fastestType(rows);
  if (fastest) cards.push({ label: "Tipo mais rápido", value: fastest.type, sub: `${fastest.avgSpeed.toFixed(1)} vel. média` });

  const outliers = findOutliers(rows, "hp");
  cards.push({ label: "Outliers de HP", value: String(outliers.length), sub: outliers.slice(0, 3).map((o) => o.name).join(", ") || "nenhum" });

  for (const card of cards) {
    const div = document.createElement("div");
    div.className = "stat-card";
    div.innerHTML = `<div class="label">${card.label}</div><div class="value">${card.value}</div>${card.sub ? `<div class="sub">${card.sub}</div>` : ""}`;
    grid.appendChild(div);
  }
}

function renderCharts(rows) {
  const typeCounts = typeCombinationCounts(rows).slice(0, 10).map(([label, value]) => ({
    label: label.split(" / ")[0], value,
  }));
  barChart(document.getElementById("chart-types"), dedupeByLabel(typeCounts), { color: "var(--accent)", valueFormat: (v) => String(v) });

  const speedByType = averageStatByType(rows, "speed").slice(0, 10).map(([label, value]) => ({ label, value }));
  barChart(document.getElementById("chart-speed"), speedByType, { color: "var(--accent-2)" });

  const scatterPoints = rows.map((r) => ({ x: r.weight_kg, y: r.defense }));
  scatterChart(document.getElementById("chart-scatter"), scatterPoints, { xLabel: "Peso (kg)", yLabel: "Defesa", color: "var(--success)" });

  const topAttack = topNByStat(rows, "attack", 10).map((r) => ({ label: r.name, value: r.attack }));
  barChart(document.getElementById("chart-attack"), topAttack, { color: "var(--danger)", valueFormat: (v) => String(v) });

  correlationHeatmap(document.getElementById("chart-correlation"), CORRELATION_LABELS, correlationMatrix(rows));
}

function dedupeByLabel(entries) {
  const seen = new Map();
  for (const entry of entries) {
    if (!seen.has(entry.label)) seen.set(entry.label, entry);
  }
  return [...seen.values()];
}

function renderTable(rows) {
  const tbody = document.querySelector("#pokemon-table tbody");
  tbody.innerHTML = "";
  document.getElementById("table-count").textContent = String(rows.length);

  const fragment = document.createDocumentFragment();
  for (const row of rows) {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.id}</td><td>${row.name}</td><td>${row.type_1}</td><td>${row.type_2 || ""}</td>
      <td>${row.hp}</td><td>${row.attack}</td><td>${row.defense}</td><td>${row.speed}</td>`;
    fragment.appendChild(tr);
  }
  tbody.appendChild(fragment);
}

function render() {
  const rows = applyFilters();
  renderStats(rows);
  renderCharts(rows);
  renderTable(rows);
}

function wireFilters() {
  document.getElementById("filter-generation").addEventListener("change", (e) => {
    state.generation = e.target.value;
    render();
  });
  document.getElementById("filter-type").addEventListener("change", (e) => {
    state.type = e.target.value;
    render();
  });
  let searchTimer;
  document.getElementById("filter-search").addEventListener("input", (e) => {
    clearTimeout(searchTimer);
    const value = e.target.value;
    searchTimer = setTimeout(() => {
      state.search = value;
      render();
    }, 150);
  });
}

async function main() {
  wireFilters();
  try {
    state.rows = await loadData();
  } catch (err) {
    document.querySelector("main").innerHTML = `<p>Nao consegui carregar os dados: ${err.message}</p>`;
    return;
  }
  populateFilters(state.rows);
  render();
}

main();
