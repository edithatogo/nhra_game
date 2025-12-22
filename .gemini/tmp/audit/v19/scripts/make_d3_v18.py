from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


HTML = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>NHRA v18 — Influence network (D3)</title>
<style>
  body { font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; }
  header { padding: 12px 16px; border-bottom: 1px solid #ddd; }
  #chart { width: 100vw; height: 92vh; }
  .link { stroke: #999; stroke-opacity: 0.6; }
  .node circle { stroke: #fff; stroke-width: 1.5px; }
  .label { font-size: 12px; pointer-events: none; }
</style>
</head>
<body>
<header>
  <strong>NHRA v18</strong> — influence network (one-way sensitivity edges). Drag nodes. Scroll to zoom.
</header>
<svg id="chart"></svg>

<script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
<script>
const data = __DATA__;

const svg = d3.select("#chart");
const width = window.innerWidth;
const height = window.innerHeight * 0.92;
svg.attr("viewBox", [0, 0, width, height]);

const g = svg.append("g");

svg.call(d3.zoom().on("zoom", (event) => g.attr("transform", event.transform)));

const links = data.links.map(d => Object.create(d));
const nodes = data.nodes.map(d => Object.create(d));

const scale = d3.scaleLinear()
  .domain(d3.extent(links, d => Math.abs(d.weight)))
  .range([0.8, 6.0]);

const link = g.append("g")
    .attr("stroke", "#999")
  .selectAll("line")
  .data(links)
  .join("line")
    .attr("class", "link")
    .attr("stroke-width", d => scale(Math.abs(d.weight)));

const node = g.append("g")
  .selectAll("g")
  .data(nodes)
  .join("g")
  .attr("class", "node")
  .call(d3.drag()
    .on("start", dragstarted)
    .on("drag", dragged)
    .on("end", dragended));

node.append("circle")
  .attr("r", d => d.kind === "outcome" ? 16 : 12)
  .attr("fill", d => d.kind === "outcome" ? "#ffeda0" : "#c6dbef");

node.append("text")
  .attr("class", "label")
  .attr("x", 14)
  .attr("y", 4)
  .text(d => d.id);

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(120))
  .force("charge", d3.forceManyBody().strength(-500))
  .force("center", d3.forceCenter(width / 2, height / 2));

simulation.on("tick", () => {
  link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

  node.attr("transform", d => `translate(${d.x},${d.y})`);
});

function dragstarted(event) {
  if (!event.active) simulation.alphaTarget(0.3).restart();
  event.subject.fx = event.subject.x;
  event.subject.fy = event.subject.y;
}
function dragged(event) {
  event.subject.fx = event.x;
  event.subject.fy = event.y;
}
function dragended(event) {
  if (!event.active) simulation.alphaTarget(0);
  event.subject.fx = null;
  event.subject.fy = null;
}
</script>
</body>
</html>
"""


def main() -> None:
    out = Path("outputs/v18")
    tables = out / "tables"
    plots = out / "plots"
    plots.mkdir(parents=True, exist_ok=True)

    infl = pd.read_csv(tables / "influence_edges.csv")
    sources = sorted(infl["source"].unique().tolist())
    targets = sorted(infl["target"].unique().tolist())

    nodes = [{"id": s, "kind": "param"} for s in sources] + [{"id": t, "kind": "outcome"} for t in targets]
    links = [{"source": r["source"], "target": r["target"], "weight": float(r["weight"])} for _, r in infl.iterrows()]

    payload = {"nodes": nodes, "links": links}
    html = HTML.replace("__DATA__", json.dumps(payload))
    (plots / "influence_network_d3.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
