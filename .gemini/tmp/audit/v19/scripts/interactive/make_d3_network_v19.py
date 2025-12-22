from __future__ import annotations

import json
from pathlib import Path

import pandas as pd


HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <title>NHRA game network (v19)</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 0; }}
    header {{ padding: 14px 16px; border-bottom: 1px solid #ddd; }}
    #wrap {{ display: grid; grid-template-columns: 320px 1fr; height: calc(100vh - 58px); }}
    #controls {{ padding: 12px 16px; border-right: 1px solid #ddd; overflow: auto; }}
    #viz {{ position: relative; }}
    svg {{ width: 100%; height: 100%; }}
    .k {{ font-weight: 600; }}
    .small {{ font-size: 12px; color: #444; }}
    .pill {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #f1f5f9; margin-right: 6px; }}
  </style>
  <script src="https://cdn.jsdelivr.net/npm/d3@7"></script>
</head>
<body>
<header>
  <span class="pill">v19</span>
  <span class="k">NHRA game network</span>
  <span class="small">Interactive view of games and outcomes. Node size reflects degree; links are conceptual (not causal identification).</span>
</header>
<div id="wrap">
  <div id="controls">
    <div class="k">Scenario</div>
    <select id="scenario"></select>
    <div style="height:12px"></div>
    <div class="k">Year</div>
    <input id="year" type="range" min="2025" max="2030" step="1" value="2025"/>
    <div class="small"><span id="year_label">2025</span></div>
    <div style="height:12px"></div>
    <div class="k">Metrics</div>
    <div class="small" id="metrics"></div>
    <hr/>
    <div class="small">
      This diagram is generated from model outputs. It is a *visual companion* to the simulation tables and is not a statistical causal graph.
    </div>
  </div>
  <div id="viz"></div>
</div>

<script>
const data = __DATA__;

const scenarios = Array.from(new Set(data.series.map(d => d.scenario))).sort();
const years = Array.from(new Set(data.series.map(d => +d.year))).sort((a,b)=>a-b);

const sel = d3.select("#scenario");
sel.selectAll("option")
  .data(scenarios)
  .enter()
  .append("option")
  .attr("value", d => d)
  .text(d => d);

const yearSlider = d3.select("#year")
  .attr("min", years[0])
  .attr("max", years[years.length-1])
  .attr("value", years[0]);

const yearLabel = d3.select("#year_label");
const metrics = d3.select("#metrics");

const width = document.body.clientWidth - 320;
const height = window.innerHeight - 58;

const svg = d3.select("#viz").append("svg")
  .attr("viewBox", [0,0,width,height]);

const link = svg.append("g")
  .attr("stroke", "#999")
  .attr("stroke-opacity", 0.6)
  .selectAll("line");

const node = svg.append("g")
  .attr("stroke", "#fff")
  .attr("stroke-width", 1.5)
  .selectAll("circle");

const label = svg.append("g")
  .attr("font-size", 12)
  .attr("fill", "#111")
  .selectAll("text");

const sim = d3.forceSimulation()
  .force("link", d3.forceLink().id(d => d.id).distance(110))
  .force("charge", d3.forceManyBody().strength(-260))
  .force("center", d3.forceCenter(width / 2, height / 2));

function updateMetrics() {
  const sc = sel.property("value");
  const yr = +yearSlider.property("value");
  yearLabel.text(yr);
  const row = data.series.find(d => d.scenario===sc && +d.year===yr);
  if (!row) return;
  metrics.html(`
    <div><span class="k">Pressure:</span> ${row.pressure_mean.toFixed(3)}</div>
    <div><span class="k">Offload (min):</span> ${row.offload_mean.toFixed(1)}</div>
    <div><span class="k">ED≤4h:</span> ${row.within4_mean.toFixed(3)}</div>
    <div><span class="k">RR:</span> ${row.rr_mean.toFixed(3)}</div>
    <div><span class="k">Eff gap:</span> ${row.effgap_mean.toFixed(3)}</div>
    <div><span class="k">NEP/cost:</span> ${(row.nep_mean/row.cost_mean).toFixed(3)}</div>
  `);
}

function renderGraph() {
  const nodes = data.nodes.map(d => Object.assign({}, d));
  const links = data.links.map(d => Object.assign({}, d));

  const deg = new Map();
  links.forEach(l => {
    deg.set(l.source, (deg.get(l.source)||0)+1);
    deg.set(l.target, (deg.get(l.target)||0)+1);
  });

  nodes.forEach(n => { n.r = 6 + 2*(deg.get(n.id)||0); });

  link.data(links).join("line")
    .attr("stroke-width", 1.4);

  const nsel = node.data(nodes).join("circle")
    .attr("r", d => d.r)
    .attr("fill", "#7dd3fc")
    .call(drag(sim));

  label.data(nodes).join("text")
    .text(d => d.label)
    .attr("dx", 10)
    .attr("dy", 4);

  sim.nodes(nodes).on("tick", () => {
    svg.selectAll("line")
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    svg.selectAll("circle")
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

    svg.selectAll("text")
      .attr("x", d => d.x)
      .attr("y", d => d.y);
  });

  sim.force("link").links(links);
  sim.alpha(1).restart();

  nsel.append("title").text(d => d.id);
}

function drag(simulation) {
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
  return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
}

sel.on("change", updateMetrics);
yearSlider.on("input", updateMetrics);

renderGraph();
updateMetrics();
</script>
</body>
</html>
"""


def main() -> None:
    repo = Path(__file__).resolve().parents[2]
    tables = repo / "outputs" / "v19" / "tables"
    out = repo / "outputs" / "v19" / "interactive"
    out.mkdir(parents=True, exist_ok=True)

    series = pd.read_csv(tables / "scenario_timeseries.csv")

    # minimal concept graph nodes/edges
    nodes = [
        {"id": "DEF", "label": "Definition"},
        {"id": "BARG", "label": "Bargaining"},
        {"id": "SHIFT", "label": "Cost shift"},
        {"id": "DISC", "label": "Discharge"},
        {"id": "GOV", "label": "Integration"},
        {"id": "COMP", "label": "Compliance"},
        {"id": "PRESS", "label": "Pressure"},
        {"id": "OFFLOAD", "label": "Offload"},
        {"id": "ED4H", "label": "ED≤4h"},
        {"id": "RR", "label": "Risk"},
        {"id": "NEP", "label": "NEP/cost"},
    ]
    links = [
        {"source": "SHIFT", "target": "PRESS"},
        {"source": "DISC", "target": "OFFLOAD"},
        {"source": "DISC", "target": "ED4H"},
        {"source": "PRESS", "target": "RR"},
        {"source": "NEP", "target": "SHIFT"},
        {"source": "GOV", "target": "SHIFT"},
        {"source": "COMP", "target": "DEF"},
        {"source": "BARG", "target": "DEF"},
        {"source": "PRESS", "target": "BARG"},
        {"source": "PRESS", "target": "COMP"},
    ]

    payload = {
        "nodes": nodes,
        "links": links,
        "series": series.to_dict(orient="records"),
    }
    html = HTML_TEMPLATE.replace("__DATA__", json.dumps(payload))
    (out / "nhra_game_network_v19.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    main()
