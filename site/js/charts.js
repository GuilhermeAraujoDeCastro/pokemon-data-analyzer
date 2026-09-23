// Graficos em SVG puro (sem lib externa) -- dataset e' pequeno o bastante
// pra nao precisar de canvas/WebGL, e SVG herda as variaveis de cor do CSS,
// entao o tema claro/escuro se aplica sem nenhum codigo extra aqui.
const NS = "http://www.w3.org/2000/svg";

function el(tag, attrs = {}) {
  const node = document.createElementNS(NS, tag);
  for (const [key, value] of Object.entries(attrs)) node.setAttribute(key, value);
  return node;
}

export function barChart(container, data, { color = "var(--accent)", valueFormat = (v) => v.toFixed(1) } = {}) {
  container.innerHTML = "";
  if (!data.length) {
    container.textContent = "Sem dados.";
    return;
  }

  const width = 560, height = 280, padding = { top: 16, right: 10, bottom: 64, left: 34 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;
  const maxValue = Math.max(...data.map((d) => d.value), 1);
  const barWidth = innerW / data.length;

  const svg = el("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": "Grafico de barras" });

  data.forEach((d, i) => {
    const barHeight = (d.value / maxValue) * innerH;
    const x = padding.left + i * barWidth + barWidth * 0.1;
    const y = padding.top + (innerH - barHeight);
    svg.appendChild(el("rect", { x, y, width: barWidth * 0.8, height: barHeight, fill: color, rx: 3 }));

    const label = el("text", {
      x: x + barWidth * 0.4, y: height - padding.bottom + 14, "text-anchor": "end",
      "font-size": "10", fill: "var(--muted)",
      transform: `rotate(-40 ${x + barWidth * 0.4} ${height - padding.bottom + 14})`,
    });
    label.textContent = d.label;
    svg.appendChild(label);

    const valueLabel = el("text", { x: x + barWidth * 0.4, y: y - 4, "text-anchor": "middle", "font-size": "10", fill: "var(--text)" });
    valueLabel.textContent = valueFormat(d.value);
    svg.appendChild(valueLabel);
  });

  container.appendChild(svg);
}

export function scatterChart(container, points, { xLabel = "", yLabel = "", color = "var(--success)" } = {}) {
  container.innerHTML = "";
  if (!points.length) {
    container.textContent = "Sem dados.";
    return;
  }

  const width = 560, height = 320, padding = { top: 10, right: 10, bottom: 40, left: 50 };
  const innerW = width - padding.left - padding.right;
  const innerH = height - padding.top - padding.bottom;
  const xs = points.map((p) => p.x);
  const ys = points.map((p) => p.y);
  const minX = Math.min(...xs), maxX = Math.max(...xs);
  const minY = Math.min(...ys), maxY = Math.max(...ys);
  const scaleX = (x) => padding.left + ((x - minX) / (maxX - minX || 1)) * innerW;
  const scaleY = (y) => padding.top + innerH - ((y - minY) / (maxY - minY || 1)) * innerH;

  const svg = el("svg", { viewBox: `0 0 ${width} ${height}`, role: "img", "aria-label": "Grafico de dispersao" });

  svg.appendChild(el("line", { x1: padding.left, y1: padding.top, x2: padding.left, y2: height - padding.bottom, stroke: "var(--border)" }));
  svg.appendChild(el("line", { x1: padding.left, y1: height - padding.bottom, x2: width - padding.right, y2: height - padding.bottom, stroke: "var(--border)" }));

  for (const p of points) {
    svg.appendChild(el("circle", { cx: scaleX(p.x), cy: scaleY(p.y), r: 3.5, fill: color, "fill-opacity": 0.7 }));
  }

  const xLabelEl = el("text", { x: width / 2, y: height - 6, "text-anchor": "middle", "font-size": "11", fill: "var(--muted)" });
  xLabelEl.textContent = xLabel;
  svg.appendChild(xLabelEl);

  const yLabelEl = el("text", {
    x: 12, y: height / 2, "text-anchor": "middle", "font-size": "11", fill: "var(--muted)",
    transform: `rotate(-90 12 ${height / 2})`,
  });
  yLabelEl.textContent = yLabel;
  svg.appendChild(yLabelEl);

  container.appendChild(svg);
}

export function correlationHeatmap(container, labels, matrix) {
  container.innerHTML = "";
  const table = document.createElement("table");
  table.className = "heatmap";

  const thead = document.createElement("thead");
  const headRow = document.createElement("tr");
  headRow.appendChild(document.createElement("th"));
  for (const label of labels) {
    const th = document.createElement("th");
    th.textContent = label;
    headRow.appendChild(th);
  }
  thead.appendChild(headRow);
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  matrix.forEach((row, i) => {
    const tr = document.createElement("tr");
    const rowHeader = document.createElement("th");
    rowHeader.textContent = labels[i];
    tr.appendChild(rowHeader);
    row.forEach((value) => {
      const td = document.createElement("td");
      td.textContent = Number.isNaN(value) ? "-" : value.toFixed(2);
      td.style.backgroundColor = colorForCorrelation(value);
      tr.appendChild(td);
    });
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  container.appendChild(table);
}

function colorForCorrelation(value) {
  if (Number.isNaN(value)) return "transparent";
  // -1 a 1 -> vermelho (negativo) ate azul (positivo)
  const t = (value + 1) / 2;
  const r = Math.round(217 - t * (217 - 63));
  const g = Math.round(83 + t * (140 - 83));
  const b = Math.round(79 + t * (201 - 79));
  return `rgba(${r}, ${g}, ${b}, 0.55)`;
}
