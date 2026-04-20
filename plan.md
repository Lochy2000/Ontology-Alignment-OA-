For each class in ontology A:
    get its label (or name if no label)
    
    For each class in ontology B:
        get its label (or name if no label)
        
        score = isub(labelA, labelB)
        
        if score >= threshold:
            add mapping: classA owl:equivalentClass classB
            
Save all mappings to a .ttl file


## helper function

The above class would assumes the same use of labels.
but Ontologies can have different uri definitions so we need a helper function 
to handle all cases.
~
def get_label(entity):
    # rdfs:label returns a list, e.g. ["Reviewer"] or []
    labels = entity.label
    if labels:
        return labels[0]  # use the first label if it exists
    else:
        return entity.name  # fall back to the URI local name
~

## General pipeline
- Load onotlogies 
- Extract Entities, splitting and normalizing the entities into something compariable
- Get label for each entity. Usually two options:
The URI local name (the bit after #): e.g. http://cmt#PaperAbstract → PaperAbstract
An rdfs:label annotation if one exists: e.g. an entity might have rdfs:label "Paper Abstract" which is cleaner than the URI
- Compare for each entity in ontology A, compare its label(s) against every entity in ontology B (class vs class, property vs property). Compute a similarity score
- Filter keep only pairs above a threshold
- Output write the mappings as RDF triples
- Evaluate compare output against the reference alignment to get precision/recall/F-score