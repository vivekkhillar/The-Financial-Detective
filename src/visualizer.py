import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from .config import Config
from .utils import setup_logger

logger = setup_logger()

class GraphVisualizer:
    @staticmethod
    def create_and_save_graph(data, output_path):
        G = nx.DiGraph()

        # Color scheme
        type_colors = {
            "Company": "#4A90E2",
            "Risk": "#E74C3C",
            "Dollar Amount": "#2ECC71",
            "Framework": "#9B59B6",
            "Location": "#F39C12",
            "Person": "#3498DB",
            "Product": "#E67E22",
            "Metric": "#1ABC9C",
            "default": "#95A5A6"
        }

        # Add nodes
        node_colors = []
        node_types = {}
        for entity in data.get("entities", []):
            if not isinstance(entity, dict):
                continue
            entity_id = entity.get("id") or entity.get("name")
            if not entity_id:
                continue
            entity_type = entity.get("type", "default")
            metadata = entity.get("metadata") or entity.get("description") or ""
            G.add_node(entity_id, type=entity_type, metadata=metadata)
            color = type_colors.get(entity_type, type_colors["default"])
            node_colors.append(color)
            node_types[entity_id] = entity_type
        
        logger.info(f"Added {len(G.nodes())} nodes to the graph")

        # Add edges - ensure ALL relationships are added
        edges_added = 0
        skipped_edges = 0
        
        for rel in data.get("relationships", []):
            relation = rel.get("relation") or rel.get("type") or rel.get("relationship") or "RELATED_TO"
            source = rel.get("source") or rel.get("entity1") or rel.get("from")
            target = rel.get("target") or rel.get("entity2") or rel.get("to")
            
            if not source or not target:
                skipped_edges += 1
                logger.warning(f"Skipping edge with missing source or target: {rel}")
                continue
            
            # Add missing nodes if needed
            if source not in G.nodes():
                G.add_node(source, type="default")
                node_colors.append(type_colors["default"])
                node_types[source] = "default"
                logger.info(f"Added missing source node: {source}")
            if target not in G.nodes():
                G.add_node(target, type="default")
                node_colors.append(type_colors["default"])
                node_types[target] = "default"
                logger.info(f"Added missing target node: {target}")
            
            # Add the edge
            G.add_edge(source, target, label=relation)
            edges_added += 1
        
        logger.info(f"Added {edges_added} edges to the graph")
        if skipped_edges > 0:
            logger.warning(f"Skipped {skipped_edges} edges due to missing source/target")
        
        # Verify all edges are in the graph
        total_edges_in_graph = len(list(G.edges()))
        logger.info(f"Total edges in graph: {total_edges_in_graph}")
        
        # Ensure all nodes are connected - find isolated nodes and connect them
        all_nodes = set(G.nodes())
        nodes_with_edges = set()
        for edge in G.edges():
            nodes_with_edges.add(edge[0])
            nodes_with_edges.add(edge[1])
        
        isolated_nodes = all_nodes - nodes_with_edges
        logger.info(f"Found {len(isolated_nodes)} isolated nodes: {isolated_nodes}")
        
        # Find main node (usually Reliance Industries Limited)
        main_node = None
        main_node_candidates = [
            "Reliance Industries Limited",
            "Reliance Industries Limited (RIL)",
            "RIL",
            "Reliance Industries",
            "Reliance"
        ]
        
        for candidate in main_node_candidates:
            if candidate in G.nodes():
                main_node = candidate
                break
        
        # If main node not found, use node with most connections
        if not main_node and len(G.nodes()) > 0:
            main_node = max(G.nodes(), key=lambda n: G.degree(n))
            logger.info(f"Using node with most connections as main: {main_node}")
        
        # Connect all isolated nodes to main node
        connections_added = 0
        if isolated_nodes and main_node:
            logger.info(f"Connecting {len(isolated_nodes)} isolated nodes to main node: {main_node}")
            for node in isolated_nodes:
                if node == main_node:
                    continue  # Skip if it's the main node itself
                # Determine relationship type based on node type
                node_type = node_types.get(node, "default")
                if node_type == "Company":
                    relation = "RELATED_TO"
                elif node_type == "Person":
                    relation = "RELATED_TO"
                elif node_type == "Dollar Amount":
                    relation = "RELATED_TO"
                elif node_type == "Risk":
                    relation = "FACES_RISK"
                elif node_type == "Location":
                    relation = "LOCATED_IN"
                else:
                    relation = "RELATED_TO"
                
                G.add_edge(main_node, node, label=relation)
                connections_added += 1
                logger.info(f"Connected {node} to {main_node} with {relation}")
            
            logger.info(f"Added {connections_added} connections from main node to isolated nodes")
        
        # Final verification
        final_edges = len(list(G.edges()))
        final_nodes_with_edges = set()
        for edge in G.edges():
            final_nodes_with_edges.add(edge[0])
            final_nodes_with_edges.add(edge[1])
        
        final_isolated = all_nodes - final_nodes_with_edges
        if final_isolated:
            logger.warning(f"Still {len(final_isolated)} isolated nodes after connection attempt: {final_isolated}")
        else:
            logger.info("All nodes are now connected!")

        # Create figure with better sizing
        num_nodes = len(G.nodes())
        fig_size = (20, 16) if num_nodes > 15 else (16, 12)
        fig, ax = plt.subplots(figsize=fig_size, facecolor='white', dpi=300)
        
        # Use spring layout with better spacing
        k_value = 2.0 if num_nodes <= 10 else 1.5 if num_nodes <= 20 else 1.0
        pos = nx.spring_layout(G, k=k_value, iterations=100, seed=42)
        
        # Draw edges with better visibility - ensure ALL edges are plotted
        edges = list(G.edges())
        logger.info(f"Drawing {len(edges)} edges")
        
        if edges:
            edge_colors = []
            for u, v in edges:
                edge_data = G[u][v]
                rel_type = str(edge_data.get('label', 'RELATED_TO')).upper()
                if 'OWNS' in rel_type or 'SUBSIDIARY' in rel_type or 'ACQUIRED' in rel_type:
                    edge_colors.append('#E74C3C')  # Red for ownership
                elif 'HAS_PROFIT' in rel_type or 'HAS_REVENUE' in rel_type or 'HAS_ASSET' in rel_type or 'HAS_DEBT' in rel_type or 'HAS_EQUITY' in rel_type:
                    edge_colors.append('#2ECC71')  # Green for financial
                elif 'CHAIRMAN' in rel_type or 'FOUNDER' in rel_type or 'CEO' in rel_type or 'DIRECTOR' in rel_type or 'EMPLOYS' in rel_type:
                    edge_colors.append('#3498DB')  # Blue for personnel
                elif 'FACES_RISK' in rel_type:
                    edge_colors.append('#E67E22')  # Orange for risks
                elif 'FOLLOWS' in rel_type or 'USES' in rel_type:
                    edge_colors.append('#9B59B6')  # Purple for frameworks
                else:
                    edge_colors.append('#7F8C8D')  # Gray for others
            
            # Draw all edges
            nx.draw_networkx_edges(G, pos, 
                                  edge_color=edge_colors,
                                  width=2.5,
                                  alpha=0.8,
                                  arrows=True,
                                  arrowsize=25,
                                  arrowstyle='->',
                                  connectionstyle='arc3,rad=0.1',
                                  min_source_margin=15,
                                  min_target_margin=15,
                                  ax=ax)
            logger.info(f"Successfully drew {len(edges)} edges")
        else:
            logger.warning("No edges found to draw!")
        
        # Draw nodes with better sizing - ensure colors match node order
        node_size = 2000 if num_nodes <= 10 else 1500 if num_nodes <= 20 else 1200
        
        # Rebuild node_colors list to match current node order
        final_node_colors = []
        for node in G.nodes():
            node_type = node_types.get(node, "default")
            color = type_colors.get(node_type, type_colors["default"])
            final_node_colors.append(color)
        
        nx.draw_networkx_nodes(G, pos,
                              node_color=final_node_colors,
                              node_size=node_size,
                              alpha=0.95,
                              linewidths=2.5,
                              edgecolors='white',
                              ax=ax)
        
        # Draw labels with better formatting
        labels = {}
        max_label_len = 40 if num_nodes <= 10 else 35 if num_nodes <= 20 else 30
        for node in G.nodes():
            label = str(node)
            if len(label) > max_label_len:
                # Try to break at word boundaries
                words = label.split()
                truncated = ""
                for word in words:
                    if len(truncated + word) <= max_label_len - 3:
                        truncated += word + " "
                    else:
                        break
                label = truncated.strip() + "..." if truncated else label[:max_label_len-3] + "..."
            labels[node] = label
        
        font_size = 12 if num_nodes <= 10 else 11 if num_nodes <= 20 else 10
        nx.draw_networkx_labels(G, pos,
                               labels,
                               font_size=font_size,
                               font_weight='bold',
                               font_color='#2C3E50',
                               bbox=dict(boxstyle='round,pad=0.5',
                                        facecolor='white',
                                        edgecolor='#BDC3C7',
                                        alpha=0.8,
                                        linewidth=1),
                               ax=ax)
        
        # Draw edge labels with better formatting - show ALL edge labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        logger.info(f"Found {len(edge_labels)} edge labels to display")
        
        if edge_labels:
            formatted_labels = {}
            for k, v in edge_labels.items():
                label = str(v).replace('_', ' ').title()
                if len(label) > 20:
                    label = label[:17] + "..."
                formatted_labels[k] = label
            
            # Draw all edge labels
            nx.draw_networkx_edge_labels(G, pos,
                                       formatted_labels,
                                       font_size=9,
                                       font_color='#34495E',
                                       font_weight='bold',
                                       bbox=dict(boxstyle='round,pad=0.4',
                                                facecolor='#ECF0F1',
                                                edgecolor='#BDC3C7',
                                                alpha=0.9,
                                                linewidth=1.5),
                                       ax=ax)
            logger.info(f"Successfully displayed {len(formatted_labels)} edge labels")
        else:
            logger.warning("No edge labels found to display!")
        
        # Add legend with better formatting
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
                     fontsize=11,
                     frameon=True,
                     fancybox=True,
                     shadow=True,
                     title='Entity Types',
                     title_fontsize=12)
        
        ax.set_title("Financial Detective Knowledge Graph", 
                    fontsize=18, 
                    fontweight='bold', 
                    pad=25,
                    color='#2C3E50')
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.2)
        plt.close()
        logger.info(f"Graph visualization saved to {output_path}")
