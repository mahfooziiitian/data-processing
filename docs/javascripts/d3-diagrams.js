/**
 * Shared D3.js helpers for docs/ diagrams.
 *
 * Loaded on every page via `extra_javascript` in mkdocs.yml, alongside the
 * D3 v7 library itself (from the jsDelivr/d3js.org CDN). Keep helpers here
 * generic and reusable — page-specific data/config stays inline in the
 * Markdown file that uses it (see docs/explanation/architecture.md for an
 * example), so this file doesn't need to grow with every new diagram.
 *
 * Usage pattern in a Markdown page (requires the `md_in_html` extension,
 * already enabled in mkdocs.yml):
 *
 *   <div id="my-chart" class="d3-diagram"></div>
 *   <script>
 *     window.addEventListener("DOMContentLoaded", function () {
 *       renderBarChart("#my-chart", [{ label: "A", value: 1 }]);
 *     });
 *   </script>
 */

/**
 * Render a simple horizontal bar chart into the element matched by
 * `selector`.
 *
 * @param {string} selector - CSS selector for the (empty) container element.
 * @param {{label: string, value: number}[]} data - Bars to draw.
 * @param {{width?: number, barHeight?: number, color?: string}} [options]
 */
function renderBarChart(selector, data, options) {
  const opts = Object.assign(
    { width: 480, barHeight: 32, color: "#3f51b5" },
    options
  );
  const margin = { top: 8, right: 48, bottom: 8, left: 120 };
  const height = data.length * opts.barHeight + margin.top + margin.bottom;
  const width = opts.width;

  const container = d3.select(selector);
  container.selectAll("*").remove();

  const svg = container
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`)
    .attr("width", "100%")
    .attr("height", height);

  const x = d3
    .scaleLinear()
    .domain([0, d3.max(data, (d) => d.value) || 1])
    .range([0, width - margin.left - margin.right]);

  const y = d3
    .scaleBand()
    .domain(data.map((d) => d.label))
    .range([margin.top, height - margin.bottom])
    .padding(0.2);

  const g = svg.append("g").attr("transform", `translate(${margin.left},0)`);

  g.selectAll("rect")
    .data(data)
    .join("rect")
    .attr("y", (d) => y(d.label))
    .attr("height", y.bandwidth())
    .attr("width", (d) => x(d.value))
    .attr("fill", opts.color);

  g.selectAll(".bar-label")
    .data(data)
    .join("text")
    .attr("class", "bar-label")
    .attr("x", (d) => x(d.value) + 6)
    .attr("y", (d) => y(d.label) + y.bandwidth() / 2)
    .attr("dy", "0.35em")
    .attr("font-size", "12px")
    .text((d) => d.value);

  svg
    .append("g")
    .attr("transform", `translate(${margin.left},0)`)
    .call(d3.axisLeft(y).tickSize(0))
    .call((axis) => axis.select(".domain").remove())
    .selectAll("text")
    .attr("font-size", "12px");
}
