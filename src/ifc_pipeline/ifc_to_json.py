import ifcopenshell
import json

path = "Duplex_A_20110907.ifc"
model = ifcopenshell.open(path)

spaces = model.by_type("IfcSpace")
output_data = []

for space in spaces:
    room_info = {
        "RoomName": space.LongName if space.LongName else space.Name,
        "Walls": [],
        "Windows": []
    }

    # NEW LOGIC: Look for 'BoundedBy' relationships to find walls
    boundaries = getattr(space, "BoundedBy", [])
    
    for boundary in boundaries:
        rel = getattr(boundary, "RelatedBuildingElement", None)
        if not rel:
            continue
            
        # Identify Walls
        if rel.is_a("IfcWall") or rel.is_a("IfcWallStandardCase"):
            wall_dims = {"Name": rel.Name}
            # Look for dimensions in Property Sets
            for p_rel in getattr(rel, "IsDefinedBy", []):
                if p_rel.is_a("IfcRelDefinesByProperties"):
                    pset = p_rel.RelatingPropertyDefinition
                    if pset.is_a("IfcPropertySet"):
                        for p in getattr(pset, "HasProperties", []):
                            if p.is_a("IfcPropertySingleValue"):
                                if any(w in p.Name for w in ["Height", "Length", "Width"]):
                                    wall_dims[p.Name] = p.NominalValue.wrappedValue
            room_info["Walls"].append(wall_dims)

    # Secondary check for Windows (Windows are often 'hosted' by walls)
    # We look for all windows and see if they are near this space
    for window in model.by_type("IfcWindow"):
        # For the Duplex, we'll check if the window is part of the space containment
        for rel_contain in getattr(space, "ContainsElements", []):
            if window in rel_contain.RelatedElements:
                room_info["Windows"].append({
                    "Name": window.Name,
                    "Height": getattr(window, "OverallHeight", 0),
                    "Width": getattr(window, "OverallWidth", 0)
                })

    output_data.append(room_info)

with open("architectural_extracted.json", "w") as f:
    json.dump(output_data, f, indent=4)

print(f"Success! Analyzed {len(output_data)} rooms with Boundary Logic.")