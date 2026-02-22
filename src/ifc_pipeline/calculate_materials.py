import json

# Load the architectural data
try:
    with open("architectural_extracted.json", "r") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Error: architectural_extracted.json not found.")
    exit()

print("\n" + "="*85)
print("PROJECT ESTIMATOR: DUPLEX APARTMENT WALLS & MATERIALS")
print("="*85)

for room in data:
    name = room.get("RoomName", "Unknown Room")
    all_walls = room.get("Walls", [])
    
    # Select the 4 primary walls to define the room
    sorted_walls = sorted(all_walls, key=lambda x: x.get("Length", 0) * x.get("Unconnected Height", 0), reverse=True)
    main_walls = sorted_walls[:4]

    print(f"\nROOM: {name.upper()}")
    print("-" * 85)
    
    for i, wall in enumerate(main_walls, 1):
        h = wall.get("Unconnected Height", 0)
        l = wall.get("Length", 0)
        area = h * l
        mat_raw = wall.get("Name", "Standard").split(":")[1] if ":" in wall.get("Name", "") else "Partition"
        
        # --- ESTIMATION LOGIC ---
        # Time: ~0.5 hours per m2 for heavy walls, ~0.3 for light partitions
        if "CMU" in mat_raw or "Brick" in mat_raw:
            time_per_m2 = 0.5
            mat_type = "CMU Blocks"
            mat_count = int(area * 12.5) # Approx 12.5 blocks per m2
            secondary = "Mortar Mix"
            sec_qty = f"{int(area * 0.8)} bags"
        else:
            time_per_m2 = 0.3
            mat_type = "92mm Metal Studs"
            mat_count = int(l * 2) # 1 stud every 0.6m + tracks
            secondary = "Drywall Sheets"
            sec_qty = f"{int(area / 2.9) + 1} sheets"

        completion_time = area * time_per_m2

        print(f"Wall {i}: {h:.2f}m (H) x {l:.2f}m (L) | Area: {area:.2f}m2")
        print(f"   ⏱️  Est. Time to Complete: {completion_time:.1f} hours")
        print(f"   🧱 Materials needed: {mat_count} {mat_type}, {sec_qty} {secondary}")
        
        # Window Reporting
        if "Exterior" in wall.get("Name", ""):
            print(f"   🪟 WINDOW: 1.20m x 1.50m Standard Unit")
    
    print("="*85)