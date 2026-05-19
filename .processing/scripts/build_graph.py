#!/usr/bin/env python3
"""
Build Graph — Knowledge graph builder
Two-pass: EXTRACTED edges + INFERRED edges with confidence
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime, timezone

PROJECT_ROOT = Path(__file__).parent.parent.parent
KB_DIR = PROJECT_ROOT / "knowledge-base"
GRAPH_DIR = PROJECT_ROOT / "graph"


def log_info(msg):
    print(f"\033[94m[INFO]\033[0m {msg}")


def log_success(msg):
    print(f"\033[92m[SUCCESS]\033[0m {msg}")


def get_all_pages():
    """Get all pages with metadata."""
    pages = {}
    if not KB_DIR.exists():
        return pages

    for md_file in KB_DIR.glob("*.md"):
        if md_file.name in ["index.md", "log.md", "overview.md"]:
            continue

        content = md_file.read_text(encoding='utf-8')

        # Extract frontmatter
        match = re.search(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if not match:
            continue

        fm = match.group(1)

        # Use filename as ID (shortcode derived from Title)
        shortcode = md_file.stem
        full_name_match = re.search(r'^full_name:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
        title_zh_match = re.search(r'^title_zh:\s*["\']?(.+?)["\']?\s*$', fm, re.MULTILINE)
        birth_match = re.search(r'^birth:\s*(.+?)\s*$', fm, re.MULTILINE)
        links_match = re.search(r'^links:\s*(\d+)', fm, re.MULTILINE)

        full_name = full_name_match.group(1).strip() if full_name_match else shortcode
        title_zh = title_zh_match.group(1).strip() if title_zh_match else ""
        birth = birth_match.group(1).strip() if birth_match else None
        link_count = int(links_match.group(1)) if links_match else 0

        pages[shortcode] = {
            "id": shortcode,
            "full_name": full_name,
            "title_zh": title_zh,
            "birth": birth,
            "links": link_count,
            "file": md_file.name
        }

    return pages


def extract_wikilinks(content):
    """Extract all wikilinks from content."""
    return re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)


def pass1_extract_edges():
    """Pass 1: Extract deterministic edges from wikilinks."""
    log_info("Pass 1: Extracting explicit links...")

    edges = []
    pages = get_all_pages()

    for page_id, page_data in pages.items():
        md_file = KB_DIR / page_data["file"]
        content = md_file.read_text(encoding='utf-8')

        wikilinks = extract_wikilinks(content)
        for target in wikilinks:
            if target in pages and target != page_id:
                edges.append({
                    "source": page_id,
                    "target": target,
                    "type": "EXTRACTED",
                    "weight": 1.0
                })

    log_info(f"Extracted {len(edges)} explicit edges")
    return edges


def pass2_infer_edges(pages, extracted_edges):
    """
    Pass 2: LLM inference for semantic relationships
    This is a simplified version - real implementation would call LLM
    """
    log_info("Pass 2: Inferring semantic relationships...")

    # Build quick lookup for subjects
    subject_map = {}
    for page_id, page_data in pages.items():
        # Read subject area from file
        md_file = KB_DIR / page_data["file"]
        content = md_file.read_text(encoding='utf-8')
        match = re.search(r'^subjects:\n((?:\s+- .+\n)*)', content, re.MULTILINE)
        if match:
            subjects = re.findall(r'- (.+)', match.group(1))
            subject_map[page_id] = subjects

    inferred = []
    extracted_pairs = set((e["source"], e["target"]) for e in extracted_edges)

    # Simple inference based on shared subjects
    for page_a, subs_a in subject_map.items():
        for page_b, subs_b in subject_map.items():
            if page_a >= page_b:
                continue
            if (page_a, page_b) in extracted_pairs:
                continue

            shared = set(s.lower() for s in subs_a) & set(s.lower() for s in subs_b)
            if shared:
                confidence = 0.5 + (len(shared) * 0.1)  # Boost for multiple shared
                confidence = min(confidence, 0.9)

                if confidence >= 0.7:
                    inferred.append({
                        "source": page_a,
                        "target": page_b,
                        "type": "INFERRED",
                        "confidence": round(confidence, 2),
                        "reason": f"Shared subject: {list(shared)[0]}"
                    })

    log_info(f"Inferred {len(inferred)} semantic edges (confidence >= 0.7)")
    return inferred


def community_detection(nodes, edges):
    """
    Simple community detection using label propagation
    This is a simplified version - real implementation would use Louvain
    """
    log_info("Detecting communities...")

    # Build adjacency list
    adj = {n: set() for n in nodes}
    for e in edges:
        if e["type"] in ["EXTRACTED", "INFERRED"]:
            adj[e["source"]].add(e["target"])
            adj[e["target"]].add(e["source"])

    # Label propagation
    labels = {n: i for i, n in enumerate(nodes)}

    def propagate():
        changed = False
        for n in nodes:
            if not adj[n]:
                continue
            neighbor_labels = [labels[neighbor] for neighbor in adj[n]]
            if neighbor_labels:
                most_common = max(set(neighbor_labels), key=neighbor_labels.count)
                if labels[n] != most_common:
                    labels[n] = most_common
                    changed = True
        return changed

    # Run propagation
    for _ in range(10):
        if not propagate():
            break

    # Renumber communities
    unique_labels = sorted(set(labels.values()))
    label_map = {old: new for new, old in enumerate(unique_labels)}
    communities = {n: label_map[labels[n]] for n in nodes}

    log_info(f"Found {len(unique_labels)} communities")
    return communities


def build_graph():
    """Main graph building function."""
    pages = get_all_pages()
    log_info(f"Processing {len(pages)} pages")

    if not pages:
        log_warn("No pages found")
        return

    # Pass 1: Extract
    extracted = pass1_extract_edges()

    # Pass 2: Infer
    inferred = pass2_infer_edges(pages, extracted)

    # Combine edges
    all_edges = extracted + inferred

    # Deduplicate
    seen = set()
    unique_edges = []
    for e in all_edges:
        key = (e["source"], e["target"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(e)

    # Community detection
    nodes_list = list(pages.keys())
    communities = community_detection(nodes_list, unique_edges)

    # Build node list with community info
    nodes = []
    for page_id, page_data in pages.items():
        nodes.append({
            "id": page_id,
            "title": page_data.get("full_name", page_id),
            "birth": page_data["birth"],
            "community": communities.get(page_id, 0),
            "type": "entity"
        })

    # Build graph JSON
    graph = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_nodes": len(nodes),
        "total_edges": len(unique_edges),
        "nodes": nodes,
        "edges": unique_edges,
        "communities": len(set(communities.values()))
    }

    # Save
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    graph_file = GRAPH_DIR / "graph.json"
    with open(graph_file, 'w', encoding='utf-8') as f:
        json.dump(graph, f, indent=2, ensure_ascii=False)

    log_success(f"Graph saved to {graph_file}")
    log_success(f"  Nodes: {len(nodes)}")
    log_success(f"  Edges: {len(unique_edges)}")
    log_success(f"  Communities: {graph['communities']}")

    # Generate HTML visualization
    generate_html(graph)


def generate_html(graph):
    """Generate interactive HTML visualization using vis.js."""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Art Historian Knowledge Graph</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        body { margin: 0; padding: 20px; font-family: sans-serif; }
        #graph { height: 80vh; border: 1px solid #ccc; }
        .controls { margin: 10px 0; }
    </style>
</head>
<body>
    <h1>Art Historian Knowledge Graph</h1>
    <div class="controls">
        <button onclick="focusCommunities()">Color by Community</button>
        <button onclick="focusLinks()">Color by Links</button>
    </div>
    <div id="graph"></div>
    <script>
        var nodes = new vis.DataSet([
"""

    # Add nodes
    node_lines = []
    colors = ['#4CAF50', '#2196F3', '#FF9800', '#9C27B0', '#F44336', '#00BCD4', '#FF5722', '#607D8B']
    for node in graph['nodes']:
        color = colors[node['community'] % len(colors)]
        title = f"{node['title']}"
        if node['birth'] and node['birth'] != 'null':
            title += f" ({node['birth']})"
        node_lines.append(f'{{id: "{node["id"]}", label: "{node["id"]}", title: "{title}", color: "{color}", community: {node["community"]}}}')

    html += ',\n'.join(node_lines)
    html += """        ]);

        var edges = new vis.DataSet([
"""

    # Add edges
    edge_lines = []
    for edge in graph['edges']:
        edge_type = edge.get('type', 'EXTRACTED')
        color = '#4CAF50' if edge_type == 'EXTRACTED' else '#FF9800'
        width = 2 if edge_type == 'EXTRACTED' else 1
        edge_lines.append(f'{{from: "{edge["source"]}", to: "{edge["target"]}", color: "{{color: \'{color}\'}}", width: {width}, type: "{edge_type}"}}')

    html += ',\n'.join(edge_lines)
    html += """        ]);

        var container = document.getElementById('graph');
        var data = { nodes: nodes, edges: edges };
        var options = {
            nodes: { shape: 'dot', size: 10 },
            edges: { arrows: { to: false } },
            physics: { stabilization: { iterations: 100 } }
        };
        var network = new vis.Network(container, data, options);

        function focusCommunities() {
            // Already colored by community by default
        }

        function focusLinks() {
            // Recolor by link count
        }
    </script>
</body>
</html>
"""

    html_file = GRAPH_DIR / "graph.html"
    html_file.write_text(html, encoding='utf-8')
    log_success(f"HTML visualization saved to {html_file}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Build knowledge graph')
    parser.add_argument('--full', action='store_true', help='Full rebuild')
    parser.add_argument('--incremental', action='store_true', help='Incremental')

    args = parser.parse_args()

    build_graph()


if __name__ == '__main__':
    main()
