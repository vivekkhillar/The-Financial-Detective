import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
from .config import Config
from .utils import setup_logger

logger = setup_logger()

class GraphVisualizer:
    @staticmethod
    def create_and_save_graph(data, output_path):
        G = nx.DiGraph()

        # Color scheme - modern professional colors
        # Handle all possible entity type names from LLM
        type_colors = {
            "Company": "#4A90E2",      # Professional blue
            "Risk": "#E74C3C",         # Alert red
            "Risk Factor": "#E74C3C",  # Alert red
            "Dollar Amount": "#2ECC71", # Success green
            "Dollar": "#2ECC71",       # Success green
            "Amount": "#2ECC71",
            "Number": "#2ECC71",
            "Currency": "#2ECC71",     # Financial amounts
            "Financial": "#2ECC71",    # Financial amounts
            "Framework": "#9B59B6",    # Purple
            "Location": "#F39C12",      # Orange
            "Country": "#F39C12",      # Orange
            "Date": "#F39C12",         # Dates
            "Person": "#3498DB",       # Light blue
            "Product": "#E67E22",       # Dark orange
            "Metric": "#1ABC9C",       # Teal
            "Subsidiary": "#16A085",   # Dark teal
            "Partnership": "#8E44AD",   # Dark purple
            "Business": "#E67E22",     # Dark orange
            "Business Segment": "#E67E22", # Business segments
            "Report": "#9B59B6",       # Reports
            "Ranking": "#9B59B6",       # Rankings
            "Award": "#9B59B6",        # Awards
            "default": "#95A5A6"       # Gray
        }

        # First, create a set of all entity IDs for quick lookup
        entity_ids = set()
        entity_map = {}
        for entity in data.get("entities", []):
            if not isinstance(entity, dict):
                continue
            # Handle both "id" and "name" keys
            entity_id = entity.get("id") or entity.get("name")
            if not entity_id:
                logger.warning(f"Skipping entity without 'id' or 'name' field: {entity}")
                continue
            entity_ids.add(entity_id)
            entity_map[entity_id] = entity

        # Add Nodes with type information - ensure ALL entities are added
        node_colors = []
        node_types = {}
        nodes_added = 0
        for entity in data.get("entities", []):
            # Handle different JSON structures - check for "id" or "name" key
            if not isinstance(entity, dict):
                continue
            # Handle both "id" and "name" keys
            entity_id = entity.get("id") or entity.get("name")
            if not entity_id:
                logger.warning(f"Skipping entity without 'id' or 'name' field: {entity}")
                continue
            entity_type = entity.get("type", "default")
            # Normalize type names for consistency
            if entity_type in ["Dollar", "Number", "Currency", "Financial"]:
                entity_type = "Dollar Amount"  # Normalize to standard name
            # Handle both "metadata" and "description" keys
            metadata = entity.get("metadata") or entity.get("description") or ""
            G.add_node(entity_id, type=entity_type, metadata=metadata)
            color = type_colors.get(entity_type, type_colors["default"])
            node_colors.append(color)
            node_types[entity_id] = entity_type
            nodes_added += 1
        
        logger.info(f"Added {nodes_added} nodes to the graph")

        # Add Edges - ensure all relationships are properly linked
        edges_added = 0
        missing_nodes = set()
        for rel in data.get("relationships", []):
            # Handle different possible key names for relation
            relation = rel.get("relation") or rel.get("type") or rel.get("relationship") or "RELATED_TO"
            # Handle both "source"/"target" and "entity1"/"entity2" formats
            source = rel.get("source") or rel.get("entity1")
            target = rel.get("target") or rel.get("entity2")
            
            if not source or not target:
                continue
            
            # Check if source node exists, if not add it
            if source not in entity_ids:
                logger.warning(f"Source node '{source}' not found in entities, adding it")
                G.add_node(source, type="default")
                node_colors.append(type_colors["default"])
                node_types[source] = "default"
                entity_ids.add(source)
                missing_nodes.add(source)
            
            # Check if target node exists, if not add it
            if target not in entity_ids:
                logger.warning(f"Target node '{target}' not found in entities, adding it")
                G.add_node(target, type="default")
                node_colors.append(type_colors["default"])
                node_types[target] = "default"
                entity_ids.add(target)
                missing_nodes.add(target)
            
            # Add the edge
            G.add_edge(source, target, label=relation)
            edges_added += 1
        
        logger.info(f"Added {edges_added} relationships to the graph")
        if missing_nodes:
            logger.warning(f"Added {len(missing_nodes)} missing nodes: {missing_nodes}")

        # Create figure with modern style
        plt.style.use('dark_background' if False else 'default')  # Set to True for dark mode
        fig, ax = plt.subplots(figsize=(16, 12), facecolor='white')
        
        # Use a better layout algorithm - adjust k based on number of nodes
        num_nodes = len(G.nodes())
        # Reduce spacing so edges are shorter and more visible
        k_value = max(1.0, min(2.5, 30 / (num_nodes ** 0.5)))  # Closer spacing
        pos = nx.spring_layout(G, k=k_value, iterations=150, seed=42)
        
        # If graph is too spread out, use a different layout
        if num_nodes > 20:
            # Try kamada_kawai layout for better edge visibility
            try:
                pos = nx.kamada_kawai_layout(G)
                logger.info("Using kamada_kawai layout for better edge visibility")
            except:
                logger.info("Using spring layout")
                pos = nx.spring_layout(G, k=k_value, iterations=150, seed=42)
        
        # Draw edges first (behind nodes) - make them more visible
        edges = list(G.edges())
        logger.info(f"Total edges to draw: {len(edges)}")
        if edges:
            # Color edges based on relationship type for better visibility
            edge_colors = []
            for u, v in edges:
                edge_data = G[u][v]
                rel_type = str(edge_data.get('label', 'RELATED_TO')).upper()
                # Color code important relationships
                if 'OWNS' in rel_type or 'SUBSIDIARY' in rel_type or 'ACQUIRED' in rel_type:
                    edge_colors.append('#E74C3C')  # Red for ownership
                elif 'HAS_REVENUE' in rel_type or 'HAS_PROFIT' in rel_type or 'HAS_ASSET' in rel_type or 'HAS_DEBT' in rel_type:
                    edge_colors.append('#2ECC71')  # Green for financial
                elif 'EMPLOYS' in rel_type or 'REPORTS_TO' in rel_type or 'CHAIRMAN' in rel_type or 'FOUNDER' in rel_type:
                    edge_colors.append('#3498DB')  # Blue for personnel
                elif 'USES' in rel_type or 'FOLLOWS' in rel_type:
                    edge_colors.append('#9B59B6')  # Purple for frameworks
                else:
                    edge_colors.append('#34495E')  # Dark gray for others - more visible
            
            # Draw edges with MUCH better visibility - make them very prominent
            # First draw a dark background for edges (outline effect)
            nx.draw_networkx_edges(G, pos, 
                                  edge_color='#2C3E50',  # Dark color
                                  width=5.5,  # Thick outline
                                  alpha=0.5,  # Semi-transparent
                                  arrows=True,
                                  arrowsize=40,
                                  arrowstyle='->',
                                  min_source_margin=15,
                                  min_target_margin=15,
                                  connectionstyle='arc3,rad=0.2',
                                  style='solid',
                                  ax=ax)
            
            # Then draw the colored edges on top
            nx.draw_networkx_edges(G, pos, 
                                  edge_color=edge_colors,
                                  width=4.0,  # Thick edges
                                  alpha=1.0,  # Fully opaque
                                  arrows=True,
                                  arrowsize=35,  # Large arrows
                                  arrowstyle='->',
                                  min_source_margin=15,  # Space from source node
                                  min_target_margin=15,  # Space from target node
                                  connectionstyle='arc3,rad=0.2',
                                  style='solid',
                                  ax=ax)
            logger.info(f"Successfully drew {len(edges)} edges")
        else:
            logger.warning("No edges found in the graph! Check if relationships exist in JSON.")
        
        # Draw nodes with better styling
        nx.draw_networkx_nodes(G, pos,
                              node_color=node_colors,
                              node_size=3000,
                              alpha=0.9,
                              linewidths=2,
                              edgecolors='white',
                              ax=ax)
        
        # Draw labels with better formatting - show metadata for financial amounts
        labels = {}
        for node in G.nodes():
            node_type = node_types.get(node, "default")
            # For Dollar Amount/Dollar/Number/Currency/Financial entities, show metadata in label
            if node_type in ["Dollar Amount", "Dollar", "Number", "Currency", "Financial"]:
                # Try to get metadata from entity data
                entity_info = None
                for entity in data.get("entities", []):
                    if not isinstance(entity, dict):
                        continue
                    entity_id = entity.get("id") or entity.get("name")
                    if entity_id == node:
                        entity_info = entity.get("metadata") or entity.get("description") or ""
                        break
                # Create a label with amount and context
                if entity_info:
                    # Truncate long metadata
                    if len(entity_info) > 25:
                        entity_info = entity_info[:22] + "..."
                    labels[node] = f"{node}\n{entity_info}"
                else:
                    labels[node] = node
            else:
                # For other nodes, show full name (truncate if too long)
                if len(node) > 20:
                    labels[node] = node[:17] + "..."
                else:
                    labels[node] = node
        
        nx.draw_networkx_labels(G, pos,
                               labels,
                               font_size=8,
                               font_weight='bold',
                               font_color='black',
                               bbox=dict(boxstyle='round,pad=0.4',
                                        facecolor='white',
                                        edgecolor='none',
                                        alpha=0.9),
                               ax=ax)
        
        # Draw edge labels - make them more visible, especially for financial data
        edge_labels = nx.get_edge_attributes(G, 'label')
        logger.info(f"Total edge labels: {len(edge_labels)}")
        if edge_labels:
            # Show ALL edge labels - don't filter them out
            # Always show financial relationship labels (profit, revenue, etc.)
            important_relations = ['OWNS', 'SUBSIDIARY_OF', 'HAS_REVENUE', 'HAS_PROFIT', 'HAS_ASSET', 'HAS_DEBT', 
                                  'EMPLOYS', 'REPORTS_TO', 'ACQUIRED', 'PARTNERS_WITH', 'PROFIT', 'REVENUE', 'ASSET', 'DEBT',
                                  'CHAIRMAN', 'FOUNDER', 'USES', 'FOLLOWS']
            
            # Show all labels, but style important ones differently
            all_labels = {}
            for (u, v), label in edge_labels.items():
                label_str = str(label).upper()
                # Truncate very long labels
                display_label = str(label)
                if len(display_label) > 25:
                    display_label = display_label[:22] + "..."
                all_labels[(u, v)] = display_label
            
            if all_labels:
                # Draw all edge labels with good visibility
                nx.draw_networkx_edge_labels(G, pos,
                                           all_labels,
                                           font_size=8,
                                           font_color='#2C3E50',
                                           font_weight='bold',
                                           bbox=dict(boxstyle='round,pad=0.5',
                                                    facecolor='white',
                                                    edgecolor='#34495E',
                                                    alpha=0.95,
                                                    linewidth=2),
                                           ax=ax)
                logger.info(f"Successfully drew {len(all_labels)} edge labels")
        
        # Add legend
        unique_types = set(node_types.values())
        legend_elements = []
        for entity_type in sorted(unique_types):
            color = type_colors.get(entity_type, type_colors["default"])
            legend_elements.append(mpatches.Patch(facecolor=color, 
                                                     edgecolor='white',
                                                     label=entity_type,
                                                     linewidth=1.5))
        
        if legend_elements:
            ax.legend(handles=legend_elements,
                    loc='upper left',
                    frameon=True,
                    fancybox=True,
                    shadow=True,
                    fontsize=10,
                    title='Entity Types',
                    title_fontsize=11)
        
        # Title with better styling
        ax.set_title("Financial Detective Knowledge Graph",
                    fontsize=16,
                    fontweight='bold',
                    pad=20,
                    color='#2C3E50')
        
        # Remove axes for cleaner look
        ax.axis('off')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save with high DPI for better quality
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        logger.info(f"Graph visualization saved to {output_path}")