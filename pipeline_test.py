import re

def get_label(entity, graph):
    """Get the best label for an entity: rdfs:label if available, otherwise URI local name."""
    # Try rdfs:label first
    labels = list(graph.objects(entity, RDFS.label))
    if labels:
        return str(labels[0])
    # Fall back to URI local name
    uri = str(entity)
    return uri.split("#")[-1]

def normalise_label(label):
    """Turn 'PaperAbstract' or 'Conference_document' into 'paper abstract' or 'conference document'."""
    # Insert space before uppercase letters (split camelCase)
    label = re.sub(r'([a-z])([A-Z])', r'\1 \2', label)
    # Replace underscores and hyphens with spaces
    label = label.replace("_", " ").replace("-", " ")
    # Lowercase everything
    label = label.lower().strip()
    return label


# Show raw label -> normalised label for both ontologies
print("\n=== CMT: raw → normalised ===")
for c in classes1:
    raw = get_label(c, g1)
    norm = normalise_label(raw)
    print(f"  {raw:30s} → '{norm}'")

print("\n=== CONFERENCE: raw → normalised ===")
for c in classes2:
    raw = get_label(c, g2)
    norm = normalise_label(raw)
    print(f"  {raw:30s} → '{norm}'")