from rdflib import Graph, RDF, OWL, RDFS

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
    
    classes = sorted([s for s in g.subjects(RDF.type, OWL.Class) if is_real_entity(s)])
    obj_props = sorted([s for s in g.subjects(RDF.type, OWL.ObjectProperty) if is_real_entity(s)])
    data_props = sorted([s for s in g.subjects(RDF.type, OWL.DatatypeProperty) if is_real_entity(s)])
    
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