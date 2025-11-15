"""Pipeline architecture visualization module.

This module generates a minimal, uniform visual representation of the SAXS
pipeline architecture using Graphviz, reflecting the actual project structure.

Architecture layers:
- Frontend: YAML parser and declarative specifications
- Compiler: Build-time components (SpecCompiler, Builders, Linkers)
- Runtime: Core execution components (Kernel, Pipeline, Scheduler)
- Processing: Data processing stages
- Registry: Stage and policy registries

The generated graph uses a clean, minimal design with a subtle color palette.
"""

from graphviz import Digraph

# Minimal color palette
COLOR_BG = "#f8f9fa"           # Light gray background
COLOR_PARSE = "#e3f2fd"        # Soft blue - parsing layer
COLOR_COMPILE = "#fff3e0"      # Soft orange - compilation layer
COLOR_RUNTIME = "#e8f5e9"      # Soft green - runtime layer
COLOR_STAGE = "#f3e5f5"        # Soft purple - processing stages
COLOR_REGISTRY = "#fce4ec"     # Soft pink - registry
COLOR_EDGE = "#546e7a"         # Blue-gray for edges
COLOR_EDGE_DATA = "#66bb6a"    # Green for data flow
COLOR_EDGE_BUILD = "#ff9800"   # Orange for build flow

dot = Digraph(comment="SAXS Pipeline Architecture", format="pdf")
dot.attr(rankdir="TB", bgcolor=COLOR_BG)
dot.attr(splines="ortho", nodesep="0.8", ranksep="1.2")
dot.attr(fontname="Helvetica", fontsize="11")

# Node style defaults
node_style = {"shape": "box", "style": "rounded,filled", "fontname": "Helvetica",
                 "fontsize": "10", "margin": "0.2,0.1"}

# =====================
# FRONTEND LAYER
# =====================
with dot.subgraph(name="cluster_FRONTEND") as frontend:
    frontend.attr(label="Frontend", style="rounded,filled",
                 fillcolor=COLOR_PARSE, fontsize="12")
    frontend.node("YAML", "YAML Config", fillcolor=COLOR_PARSE, **node_style)
    frontend.node("Parser", "DeclarativePipeline", fillcolor=COLOR_PARSE, **node_style)

# =====================
# COMPILER LAYER
# =====================
with dot.subgraph(name="cluster_COMPILER") as compiler:
    compiler.attr(label="Compiler", style="rounded,filled",
                 fillcolor=COLOR_COMPILE, fontsize="12")
    compiler.node("SpecCompiler", "SpecCompiler", fillcolor=COLOR_COMPILE, **node_style)
    compiler.node("StageBuilder", "StageBuilder", fillcolor=COLOR_COMPILE, **node_style)
    compiler.node("PolicyBuilder", "PolicyBuilder", fillcolor=COLOR_COMPILE, **node_style)
    compiler.node("StageLinker", "StageLinker", fillcolor=COLOR_COMPILE, **node_style)
    compiler.node("PolicyLinker", "PolicyLinker", fillcolor=COLOR_COMPILE, **node_style)

# =====================
# REGISTRY
# =====================
with dot.subgraph(name="cluster_REGISTRY") as registry:
    registry.attr(label="Registry", style="rounded,filled",
                 fillcolor=COLOR_REGISTRY, fontsize="12")
    registry.node("StageRegistry", "StageRegistry", fillcolor=COLOR_REGISTRY, **node_style)
    registry.node("PolicyRegistry", "PolicyRegistry", fillcolor=COLOR_REGISTRY, **node_style)

# =====================
# RUNTIME LAYER
# =====================
with dot.subgraph(name="cluster_RUNTIME") as runtime:
    runtime.attr(label="Runtime", style="rounded,filled",
                fillcolor=COLOR_RUNTIME, fontsize="12")
    runtime.node("Kernel", "BaseKernel", fillcolor=COLOR_RUNTIME, **node_style)
    runtime.node("Pipeline", "Pipeline", fillcolor=COLOR_RUNTIME, **node_style)
    runtime.node("Scheduler", "BaseScheduler", fillcolor=COLOR_RUNTIME, **node_style)

# =====================
# PROCESSING STAGES
# =====================
with dot.subgraph(name="cluster_STAGES") as stages:
    stages.attr(label="Processing Stages", style="rounded,filled",
               fillcolor=COLOR_STAGE, fontsize="12")
    stages.node("CutStage", "CutStage", fillcolor=COLOR_STAGE, **node_style)
    stages.node("FilterStage", "FilterStage", fillcolor=COLOR_STAGE, **node_style)
    stages.node("BackgroundStage", "BackgroundStage", fillcolor=COLOR_STAGE, **node_style)
    stages.node("FindPeakStage", "FindPeakStage", fillcolor=COLOR_STAGE, **node_style)
    stages.node("ProcessPeakStage", "ProcessPeakStage", fillcolor=COLOR_STAGE, **node_style)

# =====================
# POLICIES
# =====================
with dot.subgraph(name="cluster_POLICIES") as policies:
    policies.attr(label="Policies", style="rounded,filled",
                 fillcolor=COLOR_STAGE, fontsize="12")
    policies.node("ChainingPolicy", "SingleStageChainingPolicy",
                 fillcolor=COLOR_STAGE, shape="diamond", style="filled")

# =====================
# FRONTEND FLOW
# =====================
dot.edge("YAML", "Parser", color=COLOR_EDGE)
dot.edge("Parser", "SpecCompiler", color=COLOR_EDGE)

# =====================
# COMPILER FLOW
# =====================
dot.edge("SpecCompiler", "StageBuilder", color=COLOR_EDGE_BUILD)
dot.edge("SpecCompiler", "PolicyBuilder", color=COLOR_EDGE_BUILD)
dot.edge("StageBuilder", "StageLinker", color=COLOR_EDGE_BUILD)
dot.edge("PolicyBuilder", "PolicyLinker", color=COLOR_EDGE_BUILD)

# =====================
# REGISTRY CONNECTIONS
# =====================
dot.edge("StageRegistry", "StageBuilder", color=COLOR_EDGE, style="dashed")
dot.edge("PolicyRegistry", "PolicyBuilder", color=COLOR_EDGE, style="dashed")

# =====================
# BUILD TO RUNTIME
# =====================
dot.edge("StageLinker", "Kernel", color=COLOR_EDGE_BUILD)
dot.edge("PolicyLinker", "Kernel", color=COLOR_EDGE_BUILD)

# =====================
# RUNTIME FLOW
# =====================
dot.edge("Kernel", "Pipeline", color=COLOR_EDGE)
dot.edge("Pipeline", "Scheduler", color=COLOR_EDGE)

# =====================
# STAGE EXECUTION FLOW
# =====================
dot.edge("Scheduler", "CutStage", color=COLOR_EDGE_DATA)
dot.edge("CutStage", "FilterStage", color=COLOR_EDGE_DATA)
dot.edge("FilterStage", "BackgroundStage", color=COLOR_EDGE_DATA)
dot.edge("BackgroundStage", "FindPeakStage", color=COLOR_EDGE_DATA)
dot.edge("FindPeakStage", "ProcessPeakStage", color=COLOR_EDGE_DATA, label="conditional")
dot.edge("ProcessPeakStage", "FindPeakStage", color=COLOR_EDGE_DATA,
         style="dashed", label="loop")

# =====================
# POLICY CONNECTIONS
# =====================
dot.edge("ChainingPolicy", "FindPeakStage", color=COLOR_EDGE, style="dotted")
dot.edge("ChainingPolicy", "ProcessPeakStage", color=COLOR_EDGE, style="dotted")

# =====================
# EXPORT
# =====================
dot.render("langgraph_clustered", view=True)
