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
        
        # Connect all isolated nodes to main node with meaningful relationships
        connections_added = 0
        if isolated_nodes and main_node:
            logger.info(f"Connecting {len(isolated_nodes)} isolated nodes to main node: {main_node}")
            for node in isolated_nodes:
                if node == main_node:
                    continue  # Skip if it's the main node itself
                
                # Get node data to check metadata
                node_data = G.nodes[node]
                node_type = node_types.get(node, "default")
                metadata = str(node_data.get('metadata', '') or '').lower()
                
                # Determine relationship type based on node type and metadata
                relation = "RELATED_TO"  # Default
                
                if node_type == "Company":
                    # Check metadata for ownership or operational context
                    if any(word in metadata for word in ['subsidiary', 'owned', 'acquired', 'stake']):
                        relation = "OWNS"
                    elif any(word in metadata for word in ['partner', 'joint venture', 'jv']):
                        relation = "PARTNERS_WITH"
                    else:
                        relation = "OPERATES"
                        
                elif node_type == "Person":
                    # Check metadata for role
                    if any(word in metadata for word in ['founder', 'established', 'created']):
                        relation = "FOUNDER"
                    elif any(word in metadata for word in ['director', 'managing', 'ceo', 'chairman']):
                        relation = "MANAGING_DIRECTOR"
                    elif any(word in metadata for word in ['employee', 'works', 'employed']):
                        relation = "EMPLOYS"
                    else:
                        relation = "EMPLOYS"  # Default for people
                        
                elif node_type == "Dollar Amount":
                    # Check metadata for financial context
                    if any(word in metadata for word in ['revenue', 'sales', 'income', 'turnover']):
                        relation = "HAS_REVENUE"
                    elif any(word in metadata for word in ['profit', 'earnings', 'net income']):
                        relation = "HAS_PROFIT"
                    elif any(word in metadata for word in ['asset', 'capital', 'investment']):
                        relation = "HAS_ASSET"
                    elif any(word in metadata for word in ['debt', 'loan', 'borrowing']):
                        relation = "HAS_DEBT"
                    elif any(word in metadata for word in ['equity', 'share', 'capital']):
                        relation = "HAS_EQUITY"
                    elif any(word in metadata for word in ['export', 'exported']):
                        relation = "HAS_EXPORTS"
                    elif any(word in metadata for word in ['csr', 'contribution', 'donation', 'charity']):
                        relation = "HAS_CSR_CONTRIBUTION"
                    else:
                        # Default: try to infer from node name
                        node_name_lower = str(node).lower()
                        if any(word in node_name_lower for word in ['revenue', 'sales', 'turnover']):
                            relation = "HAS_REVENUE"
                        elif any(word in node_name_lower for word in ['profit', 'earnings']):
                            relation = "HAS_PROFIT"
                        elif any(word in node_name_lower for word in ['asset']):
                            relation = "HAS_ASSET"
                        elif any(word in node_name_lower for word in ['debt', 'loan']):
                            relation = "HAS_DEBT"
                        elif any(word in node_name_lower for word in ['equity']):
                            relation = "HAS_EQUITY"
                        else:
                            relation = "HAS_REVENUE"  # Default for dollar amounts
                            
                elif node_type == "Risk":
                    relation = "FACES_RISK"
                    
                elif node_type == "Location":
                    relation = "LOCATED_IN"
                    
                elif node_type == "Product":
                    relation = "PRODUCES"
                    
                elif node_type == "Framework":
                    relation = "FOLLOWS"
                    
                elif node_type == "Metric":
                    # For metrics, use RELATED_TO to create meaningful labels like "Service growth is 14%"
                    relation = "RELATED_TO"
                    
                else:
                    # For unknown types, try to infer from metadata
                    if any(word in metadata for word in ['revenue', 'profit', 'asset', 'debt', 'equity']):
                        relation = "HAS_REVENUE"  # Default financial
                    else:
                        relation = "RELATED_TO"  # Will be formatted with meaningful context
                
                G.add_edge(main_node, node, label=relation)
                connections_added += 1
                logger.info(f"Connected {node} ({node_type}) to {main_node} with {relation} (metadata: {metadata[:50] if metadata else 'none'})")
            
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
        # Maximized figure size for better readability without zooming
        if num_nodes <= 15:
            fig_size = (30, 22)
        elif num_nodes <= 30:
            fig_size = (45, 34)
        elif num_nodes <= 50:
            fig_size = (60, 45)
        else:
            fig_size = (72, 54)  # Maximized for dense graphs - very readable without zoom
        fig, ax = plt.subplots(figsize=fig_size, facecolor='white', dpi=200)  # Lower DPI for faster rendering, larger size compensates
        
        # Use better layout algorithm based on graph size with improved spacing to prevent overlaps
        if num_nodes <= 15:
            # Small graphs: use spring layout with good spacing
            k_value = 4.0  # Further increased spacing
            pos = nx.spring_layout(G, k=k_value, iterations=400, seed=42)
        elif num_nodes <= 30:
            # Medium graphs: use kamada-kawai for better node distribution
            try:
                pos = nx.kamada_kawai_layout(G)
                # Scale positions to increase spacing
                scale_factor = 1.5
                for node in pos:
                    pos[node] = (pos[node][0] * scale_factor, pos[node][1] * scale_factor)
            except:
                # Fallback to spring if kamada-kawai fails
                pos = nx.spring_layout(G, k=3.0, iterations=250, seed=42)  # Further increased spacing
        else:
            # Large graphs: use circular layout around main node for better spacing
            if main_node and main_node in G.nodes():
                # Use circular layout for better distribution
                try:
                    # Try circular layout first
                    pos = nx.circular_layout(G)
                    # Move main node to center
                    main_pos = pos[main_node]
                    for node in pos:
                        if node != main_node:
                            # Spread nodes in a circle around main node
                            pos[node] = (pos[node][0] * 2.5, pos[node][1] * 2.5)
                    pos[main_node] = (0, 0)  # Center main node
                except:
                    # Fallback to spring layout with better spacing
                    pos = nx.spring_layout(G, k=2.5, iterations=200, seed=42)
                    # Adjust to make main node more central
                    center_x = sum(x for x, y in pos.values()) / len(pos)
                    center_y = sum(y for x, y in pos.values()) / len(pos)
                    main_pos = pos[main_node]
                    offset_x = center_x - main_pos[0]
                    offset_y = center_y - main_pos[1]
                    for node in pos:
                        pos[node] = (pos[node][0] + offset_x * 0.3, pos[node][1] + offset_y * 0.3)
            else:
                pos = nx.spring_layout(G, k=2.0, iterations=200, seed=42)  # Further increased spacing
        
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
            
            # Draw edges with variable curvature - some up, some down for better separation
            # This spreads edges vertically to avoid overlap
            import math
            
            # Draw edges one by one with varying curvature
            for i, (u, v) in enumerate(edges):
                # Alternate curvature direction: even indices curve up, odd curve down
                # Use modulo to create more variation
                curvature_base = 0.2 + (i % 5) * 0.05  # Vary between 0.2 and 0.4
                curvature_direction = 1 if (i % 2 == 0) else -1  # Alternate up/down
                curvature = curvature_base * curvature_direction
                
                # Get edge color
                edge_color = edge_colors[i]
                
                # Draw individual edge with custom curvature
                nx.draw_networkx_edges(G, pos,
                                      edgelist=[(u, v)],
                                      edge_color=[edge_color],
                                      width=2.0,
                                      alpha=0.6,
                                      arrows=True,
                                      arrowsize=18,
                                      arrowstyle='->',
                                      connectionstyle=f'arc3,rad={curvature}',
                                      min_source_margin=15,
                                      min_target_margin=15,
                                      ax=ax)
            logger.info(f"Successfully drew {len(edges)} edges")
        else:
            logger.warning("No edges found to draw!")
        
        # Draw nodes with better sizing - maximized nodes for better visibility
        node_size = 4000 if num_nodes <= 10 else 3500 if num_nodes <= 20 else 3000 if num_nodes <= 40 else 2500
        
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
        
        # Get edge labels first to use in node labels
        edge_labels = nx.get_edge_attributes(G, 'label')
        
        # Draw labels with better formatting - combine relationship info with node names
        # Maximize label length for better readability (larger figure compensates)
        labels = {}
        max_label_len = 70 if num_nodes <= 10 else 65 if num_nodes <= 20 else 60 if num_nodes <= 40 else 55
        
        # Collect incoming and outgoing relationships for each node
        incoming_relations = {}
        outgoing_relations = {}
        for (source, target), relation in edge_labels.items():
            # Incoming relationships (what points TO this node)
            if target not in incoming_relations:
                incoming_relations[target] = []
            incoming_relations[target].append((source, relation))
            
            # Outgoing relationships (what this node points TO)
            if source not in outgoing_relations:
                outgoing_relations[source] = []
            outgoing_relations[source].append((target, relation))
        
        # Simplify node labels - show only entity names, relationship info goes on edges
        for node in G.nodes():
            label = str(node).strip()
            
            # Special handling for main node - show name with optional Person relationships
            is_main_node = (main_node and node == main_node)
            node_type = node_types.get(node, 'default')
            
            # For main node, optionally show Person relationships (CHAIRMAN, FOUNDER) in the label
            # But keep it minimal - most relationship info will be on edges
            if is_main_node and node in incoming_relations:
                person_company_relations = ['CHAIRMAN', 'FOUNDER', 'MANAGING_DIRECTOR', 'CEO', 'DIRECTOR']
                relations = incoming_relations[node]
                person_rels = []
                for source, relation in relations:
                    rel_str = str(relation).strip().upper()
                    source_type = node_types.get(source, 'default')
                    if node_type == 'Company' and source_type == 'Person' and any(rel in rel_str for rel in person_company_relations):
                        rel_formatted = str(relation).strip().replace('_', ' ').replace('-', ' ')
                        words = rel_formatted.split()
                        rel_formatted = ' '.join(word.capitalize() for word in words)
                        person_rels.append(f"{rel_formatted}: {source}")
                
                # Only add Person relationships to main node label if there are any
                if person_rels:
                    label = f"{label} ({', '.join(person_rels[:2])})"  # Limit to 2 to keep it readable
            
            # For all other nodes, just show the entity name
            # Relationship information will be shown on edges
            
            # Truncate if too long (but be more lenient with main node)
            max_len_for_node = max_label_len * 2 if is_main_node else max_label_len
            if len(label) > max_len_for_node:
                # Try to break at word boundaries first
                words = label.split()
                truncated = ""
                for word in words:
                    if len(truncated + word) <= max_len_for_node - 3:
                        truncated += word + " "
                    else:
                        break
                if truncated:
                    label = truncated.strip() + "..."
                else:
                    # If no good break point, truncate but show more
                    label = label[:max_len_for_node-3] + "..."
            labels[node] = label
        
        # Maximize font size for better readability
        font_size = 16 if num_nodes <= 10 else 15 if num_nodes <= 20 else 14 if num_nodes <= 40 else 13
        
        # Ensure main node label is always visible and prominent
        if main_node and main_node in labels:
            # Make main node label larger and more prominent
            main_label = labels[main_node]
            # Remove main node from regular labels
            regular_labels = {k: v for k, v in labels.items() if k != main_node}
            
            # Draw regular labels first with better positioning to avoid overlaps
            # Adjust label positions to reduce overlap
            adjusted_pos = {}
            for node, (x, y) in pos.items():
                if node in regular_labels:
                    # Slight offset to reduce overlap
                    adjusted_pos[node] = (x, y + 0.02)  # Small vertical offset
                else:
                    adjusted_pos[node] = (x, y)
            
            if regular_labels:
                nx.draw_networkx_labels(G, adjusted_pos,
                                       regular_labels,
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
            
            # Draw main node label separately with larger font and more prominent styling
            # Use same adjusted position for main node
            main_pos_adjusted = {}
            if main_node in adjusted_pos:
                main_pos_adjusted[main_node] = adjusted_pos[main_node]
            else:
                main_pos_adjusted[main_node] = pos[main_node]
            
            nx.draw_networkx_labels(G, main_pos_adjusted,
                                   {main_node: main_label},
                                   font_size=font_size + 2,  # Larger font
                                   font_weight='bold',
                                   font_color='#000000',
                                   bbox=dict(boxstyle='round,pad=0.7',
                                            facecolor='#FFF9E6',  # Light yellow background
                                            edgecolor='#2C3E50',
                                            alpha=0.98,
                                            linewidth=2.0),  # Thicker border
                                   horizontalalignment='center',
                                   verticalalignment='center',
                                   ax=ax)
        else:
            # No main node or main node not in labels - draw all labels normally
            nx.draw_networkx_labels(G, pos,
                                   labels,
                                   font_size=font_size,
                                   font_weight='bold',
                                   font_color='#1A1A1A',
                                   bbox=dict(boxstyle='round,pad=0.6',
                                            facecolor='white',
                                            edgecolor='#34495E',
                                            alpha=0.95,
                                            linewidth=1.5),
                                   ax=ax)
        
        # Draw edge labels directly on edges with large, clear fonts for maximum visibility
        # Store original entity data for better metadata access
        entity_data_map = {}
        for entity in data.get("entities", []):
            if isinstance(entity, dict):
                entity_id = entity.get("id") or entity.get("name")
                if entity_id:
                    entity_data_map[entity_id] = entity
        
        edge_labels_dict = {}
        for (u, v), relation in edge_labels.items():
            rel_str = str(relation).strip().upper()
            
            # Format relationship nicely: "OWNS" -> "Owns", "HAS_REVENUE" -> "Has Revenue"
            rel_formatted = rel_str.replace('_', ' ').replace('-', ' ')
            words = rel_formatted.split()
            rel_formatted = ' '.join(word.capitalize() for word in words)
            
            # Get target node name and metadata for context
            target_name = str(v).strip()
            target_node_data = G.nodes.get(v, {})
            target_metadata = str(target_node_data.get('metadata', '') or '').strip()
            target_type = node_types.get(v, 'default')
            
            # Get original entity data for better metadata extraction
            target_entity = entity_data_map.get(v, {})
            target_description = str(target_entity.get('description', '') or target_entity.get('metadata', '') or '').strip()
            if not target_metadata and target_description:
                target_metadata = target_description
            
            # For RELATED_TO relationships, create meaningful labels from metadata
            if 'RELATED_TO' in rel_str:
                # Get source node metadata for context
                source_node_data = G.nodes.get(u, {})
                source_metadata = str(source_node_data.get('metadata', '') or '').strip()
                source_entity = entity_data_map.get(u, {})
                source_description = str(source_entity.get('description', '') or source_entity.get('metadata', '') or '').strip()
                if not source_metadata and source_description:
                    source_metadata = source_description
                
                # Combine all available metadata sources
                all_target_metadata = (target_metadata + " " + target_description).strip().lower()
                all_source_metadata = (source_metadata + " " + source_description).strip().lower()
                
                # Check if target is a percentage or metric (e.g., "14%", "6.5%", "30%")
                is_percentage = '%' in target_name or (any(char.isdigit() for char in target_name) and target_type in ['Metric', 'default'])
                
                if is_percentage:
                    # Use entity description directly instead of extracting keywords
                    # Prefer description over metadata, as it's more complete
                    description_to_use = target_description if target_description else target_metadata
                    
                    if description_to_use and len(description_to_use.strip()) > 0:
                        # Use the full description, but clean it up
                        description_clean = description_to_use.strip()
                        # Remove common prefixes/suffixes that might be redundant
                        description_clean = description_clean.replace('is ', '').replace('was ', '').replace('are ', '')
                        # Capitalize first letter
                        if description_clean:
                            description_clean = description_clean[0].upper() + description_clean[1:] if len(description_clean) > 1 else description_clean.upper()
                        # Create label: "Description is 6.5%"
                        edge_label = f"{description_clean} is {target_name}"
                    else:
                        # Fallback: try to extract from source description
                        source_desc = source_description if source_description else source_metadata
                        if source_desc and len(source_desc.strip()) > 0:
                            source_desc_clean = source_desc.strip()
                            source_desc_clean = source_desc_clean[0].upper() + source_desc_clean[1:] if len(source_desc_clean) > 1 else source_desc_clean.upper()
                            edge_label = f"{source_desc_clean} is {target_name}"
                        else:
                            # Final fallback: use "Growth" as default
                            edge_label = f"Growth is {target_name}"
                else:
                    # Not a percentage, use metadata or entity name
                    if target_metadata:
                        edge_label = f"{target_metadata[:45]}: {target_name}"
                    elif target_description:
                        edge_label = f"{target_description[:45]}: {target_name}"
                    else:
                        edge_label = target_name
            # For certain relationships, include target name
            elif any(rel in rel_str for rel in ['OWNS', 'PRODUCES', 'EMPLOYS', 'OPERATES', 'PARTNERS_WITH']):
                edge_label = f"{rel_formatted}: {target_name}"
            elif any(rel in rel_str for rel in ['HAS_REVENUE', 'HAS_PROFIT', 'HAS_ASSET', 'HAS_DEBT', 'HAS_EQUITY', 'HAS_EXPORTS', 'HAS_CSR_CONTRIBUTION']):
                # For financial relationships, show the relationship type and target value
                edge_label = f"{rel_formatted}: {target_name}"
            elif any(rel in rel_str for rel in ['CHAIRMAN', 'FOUNDER', 'MANAGING_DIRECTOR', 'CEO', 'DIRECTOR']):
                # For personnel relationships, show relationship type
                edge_label = rel_formatted
            else:
                # Default: show relationship type with target entity/metadata
                if target_metadata and len(target_metadata) > 0:
                    edge_label = f"{target_name}: {target_metadata[:40]}"
                else:
                    edge_label = f"{rel_formatted}: {target_name}"
            
            # Truncate if too long
            max_edge_label_len = 60
            if len(edge_label) > max_edge_label_len:
                edge_label = edge_label[:max_edge_label_len-3] + "..."
            
            edge_labels_dict[(u, v)] = edge_label
        
        # Draw edge labels with maximized, bold fonts for maximum visibility
        # Filter out edge labels that would overlap with nodes
        edge_label_font_size = max(14, font_size)  # Same or larger than node labels for visibility
        
        # Filter edge labels to avoid those that would overlap with nodes
        filtered_edge_labels = {}
        if edge_labels_dict:
            import math
            # Approximate node radius in layout coordinates (scaled based on node_size)
            node_radius = math.sqrt(node_size / math.pi) / 150  # Adjusted divisor for better filtering
            
            for (u, v), label in edge_labels_dict.items():
                # Get positions of source and target nodes
                u_pos = pos.get(u)
                v_pos = pos.get(v)
                
                if u_pos and v_pos:
                    # Calculate edge midpoint where label would be placed
                    mid_x = (u_pos[0] + v_pos[0]) / 2
                    mid_y = (u_pos[1] + v_pos[1]) / 2
                    
                    # Check distance from midpoint to all nodes
                    too_close_to_node = False
                    for node, node_pos in pos.items():
                        if node == u or node == v:
                            continue  # Skip source and target nodes
                        dist = math.sqrt((mid_x - node_pos[0])**2 + (mid_y - node_pos[1])**2)
                        if dist < node_radius * 2.0:  # If too close to a node, skip this label
                            too_close_to_node = True
                            break
                    
                    # Only add label if it's not too close to any node
                    if not too_close_to_node:
                        filtered_edge_labels[(u, v)] = label
        
        if filtered_edge_labels:
            # Draw edge labels - NetworkX automatically positions them to avoid edge overlap
            # Labels are placed at the midpoint of edges, offset to avoid the line
            nx.draw_networkx_edge_labels(G, pos,
                                        edge_labels=filtered_edge_labels,
                                        font_size=edge_label_font_size,
                                        font_weight='bold',
                                        font_color='#1A1A1A',  # Darker color for better contrast
                                        bbox=dict(boxstyle='round,pad=0.6',
                                                 facecolor='#FFFFE0',  # Light yellow background for visibility
                                                 edgecolor='#2C3E50',
                                                 alpha=0.98,
                                                 linewidth=2.0),  # Thicker border
                                        rotate=False,  # Keep labels horizontal to avoid overlap
                                        ax=ax)
            logger.info(f"Drew {len(filtered_edge_labels)} edge labels on edges (filtered {len(edge_labels_dict) - len(filtered_edge_labels)} that would overlap with nodes)")
        
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
