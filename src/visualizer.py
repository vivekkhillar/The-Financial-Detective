import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import math
from .utils import setup_logger

# Configure matplotlib to properly display currency symbols ($ and ₹)
plt.rcParams['font.family'] = 'DejaVu Sans'  # Font that supports currency symbols
plt.rcParams['axes.unicode_minus'] = False  # Prevent minus sign rendering issues
plt.rcParams['font.size'] = 10  # Default font size
# Disable LaTeX rendering to prevent $ from being interpreted as math mode
plt.rcParams['text.usetex'] = False

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
            node_types[entity_id] = entity_type
        
        logger.info(f"Added {len(G.nodes())} nodes to the graph")

        # Add edges
        for rel in data.get("relationships", []):
            relation = rel.get("relation") or rel.get("type") or rel.get("relationship") or "RELATED_TO"
            source = rel.get("source") or rel.get("entity1") or rel.get("from")
            target = rel.get("target") or rel.get("entity2") or rel.get("to")
            
            if not source or not target:
                logger.warning(f"Skipping edge with missing source or target: {rel}")
                continue
            
            # Add missing nodes if needed
            if source not in G.nodes():
                G.add_node(source, type="default")
                node_types[source] = "default"
            if target not in G.nodes():
                G.add_node(target, type="default")
                node_types[target] = "default"
            
            G.add_edge(source, target, label=relation)
        
        logger.info(f"Added {len(G.edges())} edges to the graph")

        # Find isolated nodes and connect them to main node
        all_nodes = set(G.nodes())
        nodes_with_edges = {node for edge in G.edges() for node in edge}
        isolated_nodes = all_nodes - nodes_with_edges
        
        if isolated_nodes:
            logger.info(f"Found {len(isolated_nodes)} isolated nodes: {isolated_nodes}")
            
            # Find main node
            main_node_candidates = [
                "Reliance Industries Limited",
                "Reliance Industries Limited (RIL)",
                "RIL",
                "Reliance Industries",
                "Reliance"
            ]
            
            main_node = None
            for candidate in main_node_candidates:
                if candidate in G.nodes():
                    main_node = candidate
                    break
            
            if not main_node and len(G.nodes()) > 0:
                main_node = max(G.nodes(), key=lambda n: G.degree(n))
                logger.info(f"Using node with most connections as main: {main_node}")
            
            # Connect isolated nodes to main node
            if main_node:
                for node in isolated_nodes:
                    if node == main_node:
                        continue
                    
                    # Determine relationship type based on node type and metadata
                    node_data = G.nodes[node]
                    node_type = node_types.get(node, "default")
                    metadata = str(node_data.get('metadata', '') or '').lower()
                    
                    relation = GraphVisualizer._determine_relation_for_isolated_node(
                        node_type, metadata, str(node)
                    )
                    
                    G.add_edge(main_node, node, label=relation)
                    logger.info(f"Connected {node} ({node_type}) to {main_node} with {relation}")

        # Create figure with dynamic sizing
        num_nodes = len(G.nodes())
        fig_size = (30, 22) if num_nodes <= 15 else (45, 34) if num_nodes <= 30 else (50, 45) if num_nodes <= 50 else (60, 50)
        fig, ax = plt.subplots(figsize=fig_size, facecolor='white', dpi=200)

        # Calculate layout
        pos = GraphVisualizer._calculate_layout(G, num_nodes, main_node if main_node else None)

        # Draw edges
        edges = list(G.edges())
        if edges:
            edge_colors = [GraphVisualizer._get_edge_color(G[u][v].get('label', 'RELATED_TO')) 
                          for u, v in edges]
            
            # Draw edges with variable curvature
            for i, (u, v) in enumerate(edges):
                curvature_base = 0.2 + (i % 5) * 0.05
                curvature_direction = 1 if (i % 2 == 0) else -1
                curvature = curvature_base * curvature_direction
                
                nx.draw_networkx_edges(G, pos,
                                      edgelist=[(u, v)],
                                      edge_color=[edge_colors[i]],
                                      width=2.0,
                                      alpha=0.6,
                                      arrows=True,
                                      arrowsize=18,
                                      arrowstyle='->',
                                      connectionstyle=f'arc3,rad={curvature}',
                                      min_source_margin=15,
                                      min_target_margin=15,
                                      ax=ax)

        # Draw nodes
        node_size = 4000 if num_nodes <= 10 else 3500 if num_nodes <= 20 else 3000 if num_nodes <= 40 else 2500
        node_colors = [type_colors.get(node_types.get(node, "default"), type_colors["default"]) 
                      for node in G.nodes()]
        
        nx.draw_networkx_nodes(G, pos,
                              node_color=node_colors,
                              node_size=node_size,
                              alpha=0.95,
                              linewidths=2.5,
                              edgecolors='white',
                              ax=ax)

        # Draw node labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        # Create entity_data_map for isolated node labels
        entity_data_map = {entity.get("id") or entity.get("name"): entity 
                          for entity in data.get("entities", []) 
                          if isinstance(entity, dict) and (entity.get("id") or entity.get("name"))}
        labels = GraphVisualizer._create_node_labels(G, node_types, edge_labels, main_node, num_nodes, entity_data_map)
        font_size = 16 if num_nodes <= 10 else 15 if num_nodes <= 20 else 14 if num_nodes <= 40 else 16
        
        if main_node and main_node in labels:
            regular_labels = {k: v for k, v in labels.items() if k != main_node}
            if regular_labels:
                # Dollar signs are preserved - matplotlib will display them correctly with usetex=False
                nx.draw_networkx_labels(G, pos, regular_labels,
                                       font_size=font_size,
                                       font_weight='bold',
                                       font_color='#1A1A1A',
                                       bbox=dict(boxstyle='round,pad=0.5',
                                                facecolor='white',
                                                edgecolor='#34495E',
                                                alpha=0.95,
                                                linewidth=1.5),
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       ax=ax)
            
            # Dollar signs are preserved - matplotlib will display them correctly with usetex=False
            nx.draw_networkx_labels(G, pos, {main_node: labels[main_node]},
                                   font_size=font_size + 2,
                                   font_weight='bold',
                                   font_color='#000000',
                                   bbox=dict(boxstyle='round,pad=0.7',
                                            facecolor='#FFF9E6',
                                            edgecolor='#2C3E50',
                                            alpha=0.98,
                                            linewidth=2.0),
                                   horizontalalignment='center',
                                   verticalalignment='center',
                                   ax=ax)
        else:
            # Dollar signs are preserved - matplotlib will display them correctly with usetex=False
            nx.draw_networkx_labels(G, pos, labels,
                                   font_size=font_size,
                                   font_weight='bold',
                                   font_color='#1A1A1A',
                                   bbox=dict(boxstyle='round,pad=0.6',
                                            facecolor='white',
                                            edgecolor='#34495E',
                                            alpha=0.95,
                                            linewidth=1.5),
                                   ax=ax)

        # Edge labels removed - relationship info now shown in node labels

        # Add legend
        unique_types = set(node_types.values())
        legend_elements = [mpatches.Patch(facecolor=type_colors.get(t, type_colors["default"]),
                                          edgecolor='white',
                                          label=t,
                                          linewidth=1.5)
                          for t in sorted(unique_types)]
        
        if legend_elements:
            ax.legend(handles=legend_elements,
                     loc='upper left',
                     fontsize=13,
                     frameon=True,
                     fancybox=True,
                     shadow=True,
                     title='Entity Types',
                     title_fontsize=14)

        ax.set_title("Financial Detective Knowledge Graph",
                    fontsize=22,
                    fontweight='bold',
                    pad=25,
                    color='#2C3E50')
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white', pad_inches=0.2)
        plt.close()
        logger.info(f"Graph visualization saved to {output_path}")

    @staticmethod
    def _determine_relation_for_isolated_node(node_type, metadata, node_name):
        """Determine relationship type for isolated node based on type and metadata."""
        if node_type == "Company":
            if any(word in metadata for word in ['subsidiary', 'owned', 'acquired', 'stake']):
                return "OWNS"
            elif any(word in metadata for word in ['partner', 'joint venture', 'jv']):
                return "PARTNERS_WITH"
            return "OPERATES"
        elif node_type == "Person":
            if any(word in metadata for word in ['founder', 'established', 'created']):
                return "FOUNDER"
            elif any(word in metadata for word in ['director', 'managing', 'ceo', 'chairman']):
                return "MANAGING_DIRECTOR"
            return "EMPLOYS"
        elif node_type == "Dollar Amount":
            node_lower = node_name.lower()
            if any(word in metadata for word in ['revenue', 'sales', 'income', 'turnover']):
                return "HAS_REVENUE"
            elif any(word in metadata for word in ['profit', 'earnings', 'net income']):
                return "HAS_PROFIT"
            elif any(word in metadata for word in ['asset', 'capital', 'investment']):
                return "HAS_ASSET"
            elif any(word in metadata for word in ['debt', 'loan', 'borrowing']):
                return "HAS_DEBT"
            elif any(word in metadata for word in ['equity', 'share', 'capital']):
                return "HAS_EQUITY"
            elif any(word in metadata for word in ['export', 'exported']):
                return "HAS_EXPORTS"
            elif any(word in metadata for word in ['csr', 'contribution', 'donation', 'charity']):
                return "HAS_CSR_CONTRIBUTION"
            elif any(word in node_lower for word in ['revenue', 'sales', 'turnover']):
                return "HAS_REVENUE"
            elif any(word in node_lower for word in ['profit', 'earnings']):
                return "HAS_PROFIT"
            return "HAS_REVENUE"
        elif node_type == "Risk":
            return "FACES_RISK"
        elif node_type == "Location":
            return "LOCATED_IN"
        elif node_type == "Product":
            return "PRODUCES"
        elif node_type == "Framework":
            return "FOLLOWS"
        return "RELATED_TO"

    @staticmethod
    def _calculate_layout(G, num_nodes, main_node):
        """Calculate graph layout based on size."""
        if num_nodes <= 15:
            return nx.spring_layout(G, k=4.0, iterations=400, seed=42)
        elif num_nodes <= 30:
            try:
                pos = nx.kamada_kawai_layout(G)
                scale_factor = 1.5
                return {node: (pos[node][0] * scale_factor, pos[node][1] * scale_factor) 
                       for node in pos}
            except:
                return nx.spring_layout(G, k=3.0, iterations=250, seed=42)
        else:
            if main_node and main_node in G.nodes():
                try:
                    pos = nx.circular_layout(G)
                    main_pos = pos[main_node]
                    for node in pos:
                        if node != main_node:
                            pos[node] = (pos[node][0] * 2.5, pos[node][1] * 2.5)
                    pos[main_node] = (0, 0)
                    return pos
                except:
                    pos = nx.spring_layout(G, k=2.5, iterations=200, seed=42)
                    center_x = sum(x for x, y in pos.values()) / len(pos)
                    center_y = sum(y for x, y in pos.values()) / len(pos)
                    main_pos = pos[main_node]
                    offset_x = center_x - main_pos[0]
                    offset_y = center_y - main_pos[1]
                    return {node: (pos[node][0] + offset_x * 0.3, pos[node][1] + offset_y * 0.3) 
                           for node in pos}
            return nx.spring_layout(G, k=2.0, iterations=200, seed=42)

    @staticmethod
    def _get_edge_color(relation):
        """Get color for edge based on relationship type."""
        rel_str = str(relation).upper()
        if any(rel in rel_str for rel in ['OWNS', 'SUBSIDIARY', 'ACQUIRED']):
            return '#E74C3C'  # Red
        elif any(rel in rel_str for rel in ['HAS_PROFIT', 'HAS_REVENUE', 'HAS_ASSET', 'HAS_DEBT', 'HAS_EQUITY']):
            return '#2ECC71'  # Green
        elif any(rel in rel_str for rel in ['CHAIRMAN', 'FOUNDER', 'CEO', 'DIRECTOR', 'EMPLOYS']):
            return '#3498DB'  # Blue
        elif 'FACES_RISK' in rel_str:
            return '#E67E22'  # Orange
        elif any(rel in rel_str for rel in ['FOLLOWS', 'USES']):
            return '#9B59B6'  # Purple
        return '#7F8C8D'  # Gray

    @staticmethod
    def _create_node_labels(G, node_types, edge_labels, main_node, num_nodes, entity_data_map=None):
        """Create labels for nodes. Include edge label information in node labels."""
        max_label_len = 80 if num_nodes <= 10 else 75 if num_nodes <= 20 else 70 if num_nodes <= 40 else 65
        
        # Find isolated nodes (nodes without any edges)
        all_nodes = set(G.nodes())
        nodes_with_edges = {node for edge in G.edges() for node in edge}
        isolated_nodes = all_nodes - nodes_with_edges
        
        # Create edge labels dict to get formatted labels
        edge_labels_dict = GraphVisualizer._create_edge_labels(
            G, edge_labels, node_types, entity_data_map or {}
        )
        
        # Collect incoming and outgoing relationships for all nodes
        incoming_relations = {}
        outgoing_relations = {}
        for (source, target), relation in edge_labels.items():
            # Incoming relationships (what points TO this node)
            if target not in incoming_relations:
                incoming_relations[target] = []
            incoming_relations[target].append((source, edge_labels_dict.get((source, target), relation)))
            
            # Outgoing relationships (what this node points TO)
            if source not in outgoing_relations:
                outgoing_relations[source] = []
            outgoing_relations[source].append((target, edge_labels_dict.get((source, target), relation)))
        
        labels = {}
        for node in G.nodes():
            label = str(node).strip()
            # Ensure dollar signs are preserved in node labels
            if '$' in label:
                label = label.replace('\\$', '$')  # Unescape if escaped
                label = label.replace('US ', 'US$ ')  # Fix "US 65.2 billion" -> "US$ 65.2 billion"
            
            is_main_node = (main_node and node == main_node)
            is_isolated = node in isolated_nodes
            
            # Collect relationship information for this node
            relationship_parts = []
            
            # Add incoming relationships (what connects TO this node)
            if node in incoming_relations:
                for source, rel_label in incoming_relations[node][:3]:  # Limit to 3 incoming
                    # Ensure dollar signs are preserved in relationship labels
                    if isinstance(rel_label, str):
                        rel_label = rel_label.replace('\\$', '$').replace('US ', 'US$ ')
                    relationship_parts.append(rel_label)
            
            # Add outgoing relationships (what this node connects TO)
            if node in outgoing_relations:
                for target, rel_label in outgoing_relations[node][:3]:  # Limit to 3 outgoing
                    # Ensure dollar signs are preserved in relationship labels
                    if isinstance(rel_label, str):
                        rel_label = rel_label.replace('\\$', '$').replace('US ', 'US$ ')
                    relationship_parts.append(rel_label)
            
            # For isolated nodes, add metadata/description to label
            if is_isolated and entity_data_map:
                node_entity = entity_data_map.get(node, {})
                node_data = G.nodes.get(node, {})
                
                # Get metadata or description
                metadata = str(node_data.get('metadata', '') or '').strip()
                description = str(node_entity.get('description', '') or node_entity.get('metadata', '') or '').strip()
                
                # Use description if available, otherwise metadata
                additional_info = description if description else metadata
                
                if additional_info and len(additional_info.strip()) > 0:
                    additional_info = additional_info.strip()
                    if len(additional_info) > 50:
                        additional_info = additional_info[:47] + "..."
                    relationship_parts.append(additional_info)
            
            # Combine relationship information with node name
            if relationship_parts:
                # Limit total relationships to avoid very long labels
                rel_text = ", ".join(relationship_parts[:4])  # Max 4 relationships
                if len(rel_text) > 100:
                    rel_text = rel_text[:97] + "..."
                label = f"{label} ({rel_text})"
            
            # Truncate if too long
            max_len = max_label_len * 2 if is_main_node else max_label_len
            if len(label) > max_len:
                words = label.split()
                truncated = ""
                for word in words:
                    if len(truncated + word) <= max_len - 3:
                        truncated += word + " "
                    else:
                        break
                label = truncated.strip() + "..." if truncated else label[:max_len-3] + "..."
            
            labels[node] = label
        
        return labels

    @staticmethod
    def _create_edge_labels(G, edge_labels, node_types, entity_data_map):
        """Create formatted labels for edges."""
        edge_labels_dict = {}
        
        for (u, v), relation in edge_labels.items():
            rel_str = str(relation).strip().upper()
            rel_formatted = ' '.join(word.capitalize() for word in rel_str.replace('_', ' ').replace('-', ' ').split())
            
            target_name = str(v).strip()
            # Ensure dollar signs are preserved (matplotlib may escape them)
            # Replace any escaped dollar signs or ensure they're visible
            if '$' in target_name:
                # Ensure dollar sign is properly formatted
                target_name = target_name.replace('\\$', '$')  # Unescape if escaped
                target_name = target_name.replace('US ', 'US$ ')  # Fix "US 65.2 billion" -> "US$ 65.2 billion"
                target_name = target_name.replace('US$', 'US$')  # Ensure proper format
            
            target_node_data = G.nodes.get(v, {})
            target_metadata = str(target_node_data.get('metadata', '') or '').strip()
            target_type = node_types.get(v, 'default')
            target_entity = entity_data_map.get(v, {})
            target_description = str(target_entity.get('description', '') or target_entity.get('metadata', '') or '').strip()
            
            if not target_metadata and target_description:
                target_metadata = target_description
            
            # Format RELATED_TO relationships with entity descriptions
            if 'RELATED_TO' in rel_str:
                is_percentage = '%' in target_name or (any(char.isdigit() for char in target_name) and target_type in ['Metric', 'default'])
                
                if is_percentage:
                    description_to_use = target_description if target_description else target_metadata
                    if description_to_use and len(description_to_use.strip()) > 0:
                        description_clean = description_to_use.strip()
                        description_clean = description_clean.replace('is ', '').replace('was ', '').replace('are ', '')
                        if description_clean:
                            description_clean = description_clean[0].upper() + description_clean[1:] if len(description_clean) > 1 else description_clean.upper()
                        edge_label = f"{description_clean} is {target_name}"
                    else:
                        source_entity = entity_data_map.get(u, {})
                        source_description = str(source_entity.get('description', '') or source_entity.get('metadata', '') or '').strip()
                        if source_description:
                            source_desc_clean = source_description.strip()
                            source_desc_clean = source_desc_clean[0].upper() + source_desc_clean[1:] if len(source_desc_clean) > 1 else source_desc_clean.upper()
                            edge_label = f"{source_desc_clean} is {target_name}"
                        else:
                            edge_label = f"Growth is {target_name}"
                else:
                    edge_label = f"{target_metadata[:45]}: {target_name}" if target_metadata else (f"{target_description[:45]}: {target_name}" if target_description else target_name)
            elif any(rel in rel_str for rel in ['OWNS', 'PRODUCES', 'EMPLOYS', 'OPERATES', 'PARTNERS_WITH']):
                edge_label = f"{rel_formatted}: {target_name}"
            elif any(rel in rel_str for rel in ['HAS_REVENUE', 'HAS_PROFIT', 'HAS_ASSET', 'HAS_DEBT', 'HAS_EQUITY', 'HAS_EXPORTS', 'HAS_CSR_CONTRIBUTION']):
                edge_label = f"{rel_formatted}: {target_name}"
            elif any(rel in rel_str for rel in ['CHAIRMAN', 'FOUNDER', 'MANAGING_DIRECTOR', 'CEO', 'DIRECTOR']):
                # For personnel relationships, show relation with target entity name
                edge_label = f"{rel_formatted}: {target_name}"
            else:
                # Default: show relation with target entity name
                edge_label = f"{rel_formatted}: {target_name}"
            
            # Truncate if too long
            if len(edge_label) > 60:
                edge_label = edge_label[:57] + "..."
            
            edge_labels_dict[(u, v)] = edge_label
        
        return edge_labels_dict

    @staticmethod
    def _filter_overlapping_edge_labels(edge_labels_dict, pos, node_size):
        """Filter edge labels that would overlap with nodes."""
        filtered = {}
        if not edge_labels_dict:
            return filtered
        
        node_radius = math.sqrt(node_size / math.pi) / 150
        
        for (u, v), label in edge_labels_dict.items():
            u_pos = pos.get(u)
            v_pos = pos.get(v)
            
            if u_pos and v_pos:
                mid_x = (u_pos[0] + v_pos[0]) / 2
                mid_y = (u_pos[1] + v_pos[1]) / 2
                
                too_close = False
                for node, node_pos in pos.items():
                    if node == u or node == v:
                        continue
                    dist = math.sqrt((mid_x - node_pos[0])**2 + (mid_y - node_pos[1])**2)
                    if dist < node_radius * 2.0:
                        too_close = True
                        break
                
                if not too_close:
                    filtered[(u, v)] = label
        
        return filtered