from graphviz import Digraph

# Create directed graph
dot = Digraph(comment="saxs arch", format="pdf")

# Dynamic graph size
dot.attr(size="12,12")  # width,height in inches
dot.attr(ratio="expand")  # expand the canvas to fit nodes
dot.attr(splines="ortho")  # nicer edges
dot.attr(nodesep="0.8")  # space between nodes
dot.attr(ranksep="1.2")  # vertical space between ranks

# Top-to-bottom layout
# dot.attr(rankdir="TB", splines="ortho", nodesep="0.8", ranksep="1.2")
# =====================
# Clusters
# =====================


# Start node pinned at top
with dot.subgraph() as s:
    s.attr(rank="source")  # rank=source puts it at top
    s.node("__START__", shape="box", style="filled", color="lightgreen")

# End node pinned at bottom
with dot.subgraph() as e:
    e.attr(rank="sink")  # rank=sink puts it at bottom
    e.node("__END__", shape="box", style="filled", color="lightcoral")


with dot.subgraph(
    name="cluster_COMPILER",
) as COMPILER:  # <-- must start with cluster_
    COMPILER.attr(label="COMPILER", style="filled", color="lightyellow")

    COMPILER.node("BG_spec", "BG_spec")
    COMPILER.node("FILTER_spec", "FILTER_spec")
    COMPILER.node("PEAKFIND_spec", "PEAKFIND_spec")

    COMPILER.node("PEAKPROCESS_spec", "PEAKPROCESS_spec")

    COMPILER.node("FIND_policy", "FIND_policy")
    COMPILER.node("PROCESS_policy", "PROCESS_policy")


with dot.subgraph(
    name="cluster_SCHEDULER",
) as SCHEDULER:  # <-- must start with cluster_
    SCHEDULER.attr(label="SCHEDULER", style="filled", color="lightyellow")

    SCHEDULER.node("SCHEDULER", "SCHEDULER")


dot.edge("BG_spec", "FILTER_spec")
dot.edge("FILTER_spec", "PEAKFIND_spec")
dot.edge("PEAKFIND_spec", "PEAKPROCESS_spec")
dot.edge("PEAKPROCESS_spec", "PEAKFIND_spec")


dot.edge("__START__", "SCHEDULER")
dot.edge("SCHEDULER", "__END__", color="red")

# =====================
# Export to PDF
# =====================
dot.render("langgraph_clustered", view=True)
