from rdflib import Graph, RDF, OWL, RDFS, Namespace, URIRef
import re
from difflib import SequenceMatcher

## an ontology is just a graph of triples. Finding entities means searching that graph for triples with specific patterns. RDFLib gives you g.subjects(), g.objects(), and g.triples() to search in different ways.
def load_ontology(filepath):
    """Load an ontology and extract classes, object properties, and data properties."""
    g = Graph()
    g.parse(filepath, format="xml")
    
    # Helper: filter out blank nodes and OWL/RDF built-in URIs
    def is_real_entity(uri):
        uri_str = str(uri)
        return (not uri_str.startswith("http://www.w3.org/")
                and not uri_str.startswith("_:")
                and "#" in uri_str)
    
    classes = sorted([s for s in g.subjects(RDF.type, OWL.Class) if is_real_entity(s)]) # only looking for rdf:type and owl:class
    obj_props = sorted([s for s in g.subjects(RDF.type, OWL.ObjectProperty) if is_real_entity(s)])  #finds everything declared as an object property
    data_props = sorted([s for s in g.subjects(RDF.type, OWL.DatatypeProperty) if is_real_entity(s)]) #finds everything declared as a data property
    #the real enetitys are just filters to remove the owl pre defined entities 
    
    return g, classes, obj_props, data_props


path1 = r"C:\Users\User\MSC-software-eng\Knowleadge-graphs\CWK-Part2\Ontology-Alignment-OA-\OAEI-INM713-IN3067\OAEI-INM713-IN3067\conference\ontologies\cmt.owl"

path2 = r"C:\Users\User\MSC-software-eng\Knowleadge-graphs\CWK-Part2\Ontology-Alignment-OA-\OAEI-INM713-IN3067\OAEI-INM713-IN3067\conference\ontologies\conference.owl"

g1, classes1, obj1, data1 = load_ontology(path1)
g2, classes2, obj2, data2 = load_ontology(path2)

print("cMT")
print(f"Classes: {len(classes1)}, Object Props: {len(obj1)}, Data Props: {len(data1)}")
print("Class names:", [str(c).split('#')[-1] for c in classes1])
print()
print("cONFERENCE")
print(f"Classes: {len(classes2)}, Object Props: {len(obj2)}, Data Props: {len(data2)}")
print("Class names:", [str(c).split('#')[-1] for c in classes2])


# EXTRACT & NORMALIZE LABELS

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
print("\nCMT: raw & normalised")
for c in classes1:
    raw = get_label(c, g1)
    norm = normalise_label(raw)
    print(f"  {raw:30s}  '{norm}'")

print("\nCONFERENCE: raw & normalised ")
for c in classes2:
    raw = get_label(c, g2)
    norm = normalise_label(raw)
    print(f"  {raw:30s}  '{norm}'")


#####  Compare strings with similarity scoring ########

def string_similarity(s1, s2):
    """Compute similarity between two strings (0 to 1)."""
    return SequenceMatcher(None, s1, s2).ratio()


# Compare every CMT class against every Conference class
THRESHOLD = 0.6  # only keep matches above this

print("\string comparison (classes)")
print(f"Comparing {len(classes1)} CMT classes x {len(classes2)} Conference classes")
print(f"Threshold: {THRESHOLD}\n")

matches_found = []

for c1 in classes1:
    label1 = normalise_label(get_label(c1, g1))
    
    for c2 in classes2:
        label2 = normalise_label(get_label(c2, g2))
        
        sim = string_similarity(label1, label2)
        
        if sim >= THRESHOLD:
            matches_found.append((label1, label2, sim, c1, c2))

# Sort by similarity score (highest first)
matches_found.sort(key=lambda x: x[2], reverse=True)

# Print results
print(f"Found {len(matches_found)} candidate matches:\n")
print(f"  {'CMT label':30s} {'Conference label':30s} {'Score':>6s}")
print(f"  {'-'*30} {'-'*30} {'-'*6}")
for label1, label2, sim, c1, c2 in matches_found:
    print(f"  {label1:30s} {label2:30s} {sim:6.3f}")



####### Output mappings as Turtle #########

# moved up or down
OUTPUT_THRESHOLD = 0.8

# Filter to only keep the best match per entity and avoid the duplicates
best_matches = {}
for label1, label2, sim, c1, c2 in matches_found:
    if sim >= OUTPUT_THRESHOLD:
        # For each CMT entity, keep only its highest-scoring match
        key = str(c1)
        if key not in best_matches or sim > best_matches[key][2]:
            best_matches[key] = (c1, c2, sim)

# create the otput
output = Graph()
OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

print(f"\noutput mappings (threshold={OUTPUT_THRESHOLD})\n")

for c1, c2, sim in best_matches.values():
    output.add((c1, OWL.equivalentClass, c2))
    label1 = normalise_label(get_label(c1, g1))
    label2 = normalise_label(get_label(c2, g2))
    print(f"  {label1:30s} ≡ {label2:30s} ({sim:.3f})")

# Save to file
output_file = "my-cmt-conference.ttl"
output.serialize(destination=output_file, format="turtle")
print(f"\nSaved {len(best_matches)} mappings to {output_file}")



########## Evaluate against the reference alignment  ############

# Load the reference alignment
ref = Graph()
ref_path = r"C:\Users\User\MSC-software-eng\Knowleadge-graphs\CWK-Part2\Ontology-Alignment-OA-\OAEI-INM713-IN3067\OAEI-INM713-IN3067\conference\cmt-conference.ttl"
ref.parse(ref_path, format="turtle")

# Extract mapping pairs from both graphs
def extract_mappings(graph):
    """Pull out all (subject, object) pairs from equivalentClass/Property/sameAs triples."""
    mappings = set()
    for pred in [OWL.equivalentClass, OWL.equivalentProperty, OWL.sameAs]:
        for s, p, o in graph.triples((None, pred, None)):
            mappings.add((str(s), str(o)))
    return mappings

our_mappings = extract_mappings(output)
ref_mappings = extract_mappings(ref)

# Calculate metrics
correct = our_mappings & ref_mappings  # intersection — what we got right
precision = len(correct) / len(our_mappings) if our_mappings else 0
recall = len(correct) / len(ref_mappings) if ref_mappings else 0
f_score = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

print(f"\nEvaluation")
print(f"Test mappings:       {len(our_mappings)}")
print(f"Reference mappings: {len(ref_mappings)}")
print(f"Correct (overlap):  {len(correct)}")
print(f"")
print(f"Precision: {precision:.3f}  ({len(correct)}/{len(our_mappings)} correct in test)")
print(f"Recall:    {recall:.3f}  ({len(correct)}/{len(ref_mappings)} from originial in test)")
print(f"F-score:   {f_score:.3f}")
print(f"\n--- Correct matches ---")
for s, o in sorted(correct):
    print(f"  {s.split('#')[-1]:30s} ≡ {o.split('#')[-1]}")
print(f"\n--- False positives (found in test but wrong) ---")
for s, o in sorted(our_mappings - ref_mappings):
    print(f"  {s.split('#')[-1]:30s} ≡ {o.split('#')[-1]}")
print(f"\n--- Missed (in reference not in test) ---")
for s, o in sorted(ref_mappings - correct):
    print(f"  {s.split('#')[-1]:30s} ≡ {o.split('#')[-1]}")