

pjt_manufacturers
id, global_id, local_id

pjt_temperatures
id, global_id, local_id

pjt_genders
id, global_id, local_id

pjt_transition_protections
id, global_id, local_id

pjt_transition_adhesives
id, global_id, local_id

pjt_transition_sizes
id, global_id, local_id

pjt_transition_materials
id, global_id, local_id

pjt_transition_families
id, global_id, local_id

pjt_transition_shapes
id, global_id, local_id

pjt_cads
id, global_id, local_id

pjt_cavity_locks
id, global_id, local_id

pjt_colors
id, global_id, local_id

pjt_datasheets
id, global_id, local_id

pjt_directions
id, global_id, local_id

pjt_images
id, global_id, local_id

pjt_ip_fluids
id, global_id, local_id

pjt_ip_solids
id, global_id, local_id

pjt_ip_supps
id, global_id, local_id

pjt_materials
id, global_id, local_id

pjt_series
id, global_id, local_id

pjt_families
id, global_id, local_id

pjt_ip_ratings
id, global_id, local_id

pjt_transition_series
id, global_id, local_id

pjt_transitions
id, global_id, local_id

pjt_transition_maps
id, global_id, local_id

pjt_transition_branches
id, global_id, local_id

pjt_boots
id, global_id, local_id

pjt_bundle_cover_series
id, global_id, local_id

pjt_bundle_cover_resistances
id, global_id, local_id

pjt_bundle_cover_materials
id, global_id, local_id

pjt_bundle_cover_rigidities
id, global_id, local_id

pjt_bundle_covers
id, global_id, local_id,


pjt_covers
id, global_id, local_id

pjt_cpa_locks
id, global_id, local_id

pjt_tpa_locks
id, global_id, local_id

pjt_seals
id, global_id, local_id

pjt_wires
id, global_id, local_id

pjt_terminals
id, global_id, local_id

pjt_housings
id, global_id, local_id

pjt_cavity_maps
id, global_id, local_id

pjt_cavities
id, global_id, local_id, id


schematic_housings
id, project_id, x1, y1, x2, y2,

schematic_terminals
id, project_id, x1, y1, x2, y2,

schematic_bundles
id, project_id, x1, y1, x2, y2,

schematic_transitions
id, project_id, x1, y1, x2, y2,


schematic_wires
id, project_id, x1, y1, x2, y2,

schematic_layouts
id, project_id, x, y

schematics
id, project_id


projects
id, name, schematic_id, plan_id


project_parts
id,project_id, part_id, part_type


part_types

TRANSITION = 1
BOOT = 2
BUNDLE_COVER = 3
COVER = 4
CPA_LOCK = 5
TPA_LOCK = 6
SEAL = 7
WIRE = 8
TERMINAL = 9
HOUSING = 10


