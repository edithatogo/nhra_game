"""Create a lightweight D3 interactive line chart for v13 outputs.

Writes:
  outputs/v13/interactive/network_externality.html
"""
from __future__ import annotations

from pathlib import Path

HTML = """<!doctype html>
<html>
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Network externality (interactive)</title>
<style>
  body { font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; color: #111; }
  .wrap { max-width: 980px; margin: 0 auto; }
  .note { background:#f7f7fb; padding:12px 14px; border-radius:12px; border:1px solid #eee; margin-bottom:16px;}
  svg { width: 100%; height: 420px; border: 1px solid #eee; border-radius: 12px; background: white; }
  .axis path, .axis line { stroke: #bbb; }
</style>
</head>
<body>
<div class="wrap">
  <h1>Network externality proxy</h1>
  <div class="note">Reads <code>../../v12/tables/trajectory_derived.csv</code>. Hover for values.</div>
  <svg id="chart" viewBox="0 0 980 420" preserveAspectRatio="xMidYMid meet"></svg>
</div>

<script src="https://d3js.org/d3.v7.min.js"></script>
<script>
(async function () {
  const url = "../../v12/tables/trajectory_derived.csv";
  const data = await d3.csv(url, d => ({
    year: +d.year,
    y: +d.network_externality
  }));

  const svg = d3.select("#chart");
  const W = 980, H = 420;
  const margin = {top: 30, right: 20, bottom: 45, left: 70};
  const w = W - margin.left - margin.right;
  const h = H - margin.top - margin.bottom;

  const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`);

  const x = d3.scaleLinear().domain(d3.extent(data, d => d.year)).range([0, w]);
  const y = d3.scaleLinear().domain(d3.extent(data, d => d.y)).nice().range([h, 0]);

  g.append("g").attr("class","axis").attr("transform", `translate(0,${h})`).call(d3.axisBottom(x).ticks(6).tickFormat(d3.format("d")));
  g.append("g").attr("class","axis").call(d3.axisLeft(y).ticks(6));

  const line = d3.line().x(d => x(d.year)).y(d => y(d.y));

  g.append("path")
    .datum(data)
    .attr("fill","none")
    .attr("stroke","#111")
    .attr("stroke-width",2.5)
    .attr("d", line);

  const tip = g.append("g").style("display","none");
  tip.append("circle").attr("r",5).attr("fill","#111");
  const label = tip.append("text").attr("x",10).attr("y",-10).style("font-size","14px");

  svg.on("mousemove", function(event) {
    const [mx,my] = d3.pointer(event, g.node());
    const year = Math.round(x.invert(mx));
    const i = d3.bisector(d => d.year).left(data, year);
    const d0 = data[Math.min(Math.max(i,0), data.length-1)];
    tip.style("display", null).attr("transform", `translate(${x(d0.year)},${y(d0.y)})`);
    label.text(`${d0.year}: ${d0.y.toFixed(3)}`);
  }).on("mouseleave", function() {
    tip.style("display","none");
  });
})();
</script>
</body>
</html>
"""


def main() -> None:
    out = Path("outputs/v13/interactive")
    out.mkdir(parents=True, exist_ok=True)
    (out / "network_externality.html").write_text(HTML, encoding="utf-8")


if __name__ == "__main__":
    main()
