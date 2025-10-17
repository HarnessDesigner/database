import math
import os


BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))


def create_tables(con, cur):
    cur.execute('CREATE TABLE manufacturers('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'address TEXT DEFAULT "" NOT NULL, '
                'contact_person TEXT DEFAULT "" NOT NULL, '
                'phone TEXT DEFAULT "" NOT NULL, '
                'ext TEXT DEFAULT "" NOT NULL, '
                'email TEXT DEFAULT "" NOT NULL, '
                'website TEXT DEFAULT "" NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE temperatures('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE genders('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_protections('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_adhesives('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'code TEXT DEFAULT "" NOT NULL, '
                'description TEXT NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_sizes('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'min REAL NOT NULL, '
                'max REAL NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_materials('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_families('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_shapes('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE cads('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'path TEXT DEFAULT "" NOT NULL, '
                'data BLOB DEFAULT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE cavity_locks('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE colors('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'rgb INTEGER NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE datasheets('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'path TEXT DEFAULT "" NOT NULL, '
                'data BLOB DEFAULT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE directions('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE images('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'path TEXT DEFAULT "" NOT NULL, '
                'data BLOB DEFAULT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE ip_fluids('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'short_desc TEXT NOT NULL, '
                'description TEXT NOT NULL, '
                'icon_data BLOB DEFAULT NULL'                        
                ');')
    con.commit()

    cur.execute('CREATE TABLE ip_solids('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'short_desc TEXT NOT NULL, '
                'description TEXT NOT NULL, '
                'icon_data BLOB DEFAULT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE ip_supps('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'description TEXT NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE materials('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'symbol TEXT UNIQUE NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE series('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE families('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE ip_ratings('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'solid_id INTEGER DEFAULT 7 NOT NULL, '
                'fluid_id INTEGER DEFAULT 12 NOT NULL, '
                'supp_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (solid_id) REFERENCES ip_solids(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (fluid_id) REFERENCES ip_fluids(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (supp_id) REFERENCES ip_supps(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')

    cur.execute('CREATE TABLE transition_series('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'branch_count INTEGER DEFAULT 0 NOT NULL, '
                'tran_material_id INTEGER DEFAULT 0 NOT NULL, '
                'tran_family_id INTEGER DEFAULT 0 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'tran_protection_id INTEGER DEFAULT 0 NOT NULL, '
                'tran_shape_id INTEGER DEFAULT 0 NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (tran_material_id) REFERENCES transition_materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (tran_family_id) REFERENCES transition_families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, ' 
                'FOREIGN KEY (tran_protection_id) REFERENCES transition_protections(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (tran_shape_id) REFERENCES transition_shapes(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transitions('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'tran_series_id INTEGER DEFAULT 0 NOT NULL, '
                'tran_adhesive_id INTEGER DEFAULT 0 NOT NULL, '
                'tran_size_ids TEXT DEFAULT "[]" NOT NULL, '
                'FOREIGN KEY (tran_series_id) REFERENCES transition_series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (tran_adhesive_id) REFERENCES transition_ashesives(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_maps('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'tran_series_id INTEGER UNIQUE NOT NULL, '
                'overlay_id INTEGER DEFAULT NULL, '
                'image_id INTEGER DEFAULT NULL, '
                'num_branches INTEGER DEFAULT 0 NOT NULL, '
                'FOREIGN KEY (overlay_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (tran_series_id) REFERENCES transitions(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE transition_branches('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'tran_map_id INTEGER NOT NULL, '
                'idx INTEGER DEFAULT 0 NOT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'x INTEGER DEFAULT 0 NOT NULL, '
                'y INTEGER DEFAULT 0 NOT NULL, '
                'w INTEGER DEFAULT 0 NOT NULL, '
                'h INTEGER DEFAULT 0 NOT NULL, '
                'rgb INTEGER DEFAULT 255 NOT NULL, '
                'FOREIGN KEY (tran_map_id) REFERENCES transition_maps(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE boots('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 1 NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE bundle_cover_series('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE bundle_cover_resistances('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'value INTEGER NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE bundle_cover_materials('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE bundle_cover_rigidities('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()

    cur.execute('CREATE TABLE bundle_covers('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT NULL, '
                'min_size INTEGER DEFAULT 0 NOT NULL, '
                'max_size INTEGER DEFAULT 0 NOT NULL, '
                'wall TEXT DEFAULT "Single" NOT NULL, '
                'shrink_ratio TEXT DEFAULT "" NOT NULL, '
                'resistance_values INTEGER DEFAULT 0 NOT NULL, '
                'material_id INTEGER DEFAULT 0 NOT NULL, '
                'rigidity_id INTEGER DEFAULT 0 NOT NULL, '
                'shrink_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES bundle_cover_series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (material_id) REFERENCES bundle_cover_materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (rigidity_id) REFERENCES bundle_cover_rigidities(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (shrink_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE covers('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 1 NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'direction_id INTEGER DEFAULT 1 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'color_id INTEGER DEFAULT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'pins TEXT DEFAULT "" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (direction_id) REFERENCES directions(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE cpa_locks('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 1 NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'pins TEXT DEFAULT "" NOT NULL, '
                'color_id INTEGER DEFAULT 1 NOT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'terminal_size REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE tpa_locks('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 1 NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'pins TEXT DEFAULT "" NOT NULL, '
                'color_id INTEGER DEFAULT 1 NOT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'terminal_size REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE seals('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'type TEXT DEFAULT "" NOT NULL, '
                'hardness INTEGER DEFAULT -1 NOT NULL, '
                'color_id INTEGER DEFAULT NULL, '
                'lubricant TEXT DEFAULT "" NOT NULL, '
                'min_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 1 NOT NULL, '                
                'length REAL DEFAULT "0.0" NOT NULL, '
                'o_dia REAL DEFAULT "0.0" NOT NULL, '
                'i_dia REAL DEFAULT "0.0" NOT NULL, '
                'wire_dia_min REAL DEFAULT "0.0" NOT NULL, '
                'wire_dia_max REAL DEFAULT "0.0" NOT NULL, '                
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '    
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'                
                ');')
    con.commit()

    cur.execute('CREATE TABLE wires('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 1 NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'primary_color_id INTEGER DEFAULT 1 NOT NULL, '
                'addl_color_ids TEXT DEFAULT "[]" NOT NULL, '
                'core_material_id INTEGER DEFAULT 1 NOT NULL, '
                'num_conductors INTEGER DEFAULT 1 NOT NULL, '
                'shielded INTEGER DEFAULT 0 NOT NULL, '
                'tpi INTEGER DEFAULT 0 NOT NULL, '
                'conductor_dia_mm REAL DEFAULT "0.0" NOT NULL, '
                'size_mm2 REAL DEFAULT "0.0" NOT NULL, '
                'size_awg INTEGER DEFAULT 0 NOT NULL, '
                'od_mm REAL DEFAULT "0.0" NOT NULL, '
                'max_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (primary_color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (core_material_id) REFERENCES materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE terminals('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'gender_id INTEGER DEFAULT 1 NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'family_id INTEGER DEFAULT 1 NOT NULL, '
                'sealing INTEGER DEFAULT 0 NOT NULL, '
                'cavity_lock_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'material_id INTEGER DEFAULT 1 NOT NULL, '
                'blade_size REAL DEFAULT "0.0" NOT NULL, '
                'resistance_mohms REAL DEFAULT "0.0" NOT NULL, '
                'mating_cycles INTEGER DEFAULT 0 NOT NULL, '
                'max_vibration_g INTEGER DEFAULT 0 NOT NULL, '
                'max_current_ma INTEGER DEFAULT 0 NOT NULL, '
                'wire_size_min_awg INTEGER DEFAULT 20 NOT NULL, '
                'wire_size_max_awg INTEGER DEFAULT 20 NOT NULL, '
                'wire_dia_min REAL DEFAULT "0.0" NOT NULL, '
                'wire_dia_max REAL DEFAULT "0.0" NOT NULL, '
                'min_wire_cross REAL DEFAULT "0.0" NOT NULL, '
                'max_wire_cross REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (gender_id) REFERENCES genders(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cavity_lock_id) REFERENCES cavity_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '   
                'FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'                               
                ');')
    con.commit()

    cur.execute('CREATE TABLE housings('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 1 NOT NULL, '
                'series_id INTEGER DEFAULT 1 NOT NULL, '
                'gender_id INTEGER DEFAULT 1 NOT NULL, '
                'ip_rating_id INTEGER DEFAULT 1 NOT NULL, '
                'image_id INTEGER DEFAULT 1 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 1 NOT NULL, '
                'cad_id INTEGER DEFAULT 1 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 1 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 1 NOT NULL, '                
                'cavity_lock_id INTEGER DEFAULT 1 NOT NULL, '
                'direction_id INTEGER DEFAULT 1 NOT NULL, '    
                'sealed INTEGER DEFAULT 0 NOT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'centerline REAL DEFAULT "0.0" NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '    
                'rows INTEGER DEFAULT 0 NOT NULL, '    
                'num_pins INTEGER DEFAULT 0 NOT NULL, '
                'terminal_sizes TEXT DEFAULT "[]" NOT NULL, '
                'compat_cpas TEXT DEFAULT "[]" NOT NULL, '    
                'compat_tpas TEXT DEFAULT "[]" NOT NULL, '    
                'compat_covers TEXT DEFAULT "[]" NOT NULL, '    
                'compat_terminals TEXT DEFAULT "[]" NOT NULL, '    
                'compat_seals TEXT DEFAULT "[]" NOT NULL, '
                'mates_to TEXT DEFAULT "[]" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (gender_id) REFERENCES genders(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (ip_rating_id) REFERENCES ip_ratings(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES datasheets(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES cads(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (cavity_lock_id) REFERENCES terminal_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (wire_orientation_id) REFERENCES directions(id) ON DELETE SET DEFAULT ON UPDATE CASCADE' 
                ');')
    con.commit()

    cur.execute('CREATE TABLE cavity_maps('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'housing_id INTEGER UNIQUE NOT NULL, '
                'overlay_id INTEGER DEFAULT NULL, '
                'image_id INTEGER DEFAULT NULL, '
                'count INTEGER DEFAULT 0 NOT NULL, ' 
                'FOREIGN KEY (housing_id) REFERENCES housings(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (overlay_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES images(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()

    cur.execute('CREATE TABLE cavities('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'cavity_map_id INTEGER NOT NULL, '
                'idx INTEGER NOT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'size REAL DEFAULT "0.0" NOT NULL, '
                'x INTEGER DEFAULT 0 NOT NULL, '
                'y INTEGER DEFAULT 0 NOT NULL, '
                'w INTEGER DEFAULT 0 NOT NULL, '
                'h INTEGER DEFAULT 0 NOT NULL, '
                'rgb INTEGER DEFAULT 255 NOT NULL, '
                'FOREIGN KEY (cavity_map_id) REFERENCES cavity_maps(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()


def _build_temps():
    data = [(0, 'Unknown',)]

    for i in range(-100, 305, 5):
        if i > 0:
            i = '+' + str(i)
        else:
            i = str(i)

        i += '°C'
        data.append((len(data), i))

    return data


def _build_wires():
    color_mapping = {
        0: 'Black',
        1: 'Brown',
        2: 'Red',
        3: 'Orange',
        4: 'Yellow',
        5: 'Green',
        6: 'Blue',
        7: 'Violet',
        8: 'Gray',
        9: 'White'
    }

    def __awg_to_mm2(a: int) -> float:
        d_in = 0.005 * (92 ** ((36 - a) / 39))
        d_mm = d_in * 25.4
        area_mm2 = (math.pi / 4) * (d_mm ** 2)
        return round(area_mm2, 4)

    pn_template = 'M22759/32-{awg}-{primary}{secondary}'

    values = []

    for awg in range(8, 31, 2):
        mm_2 = __awg_to_mm2(awg)

        for p_id in range(10):
            part_number = pn_template.format(awg=awg, primary=p_id, secondary='')
            description = f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]} Tefzel milspec single conductor wire'

            values.append((part_number, 2, description, str(mm_2), awg, p_id, '[]', 7))
            for s_id in range(10):
                if p_id == s_id:
                    continue
                description = f'{awg}AWG ({mm_2}mm²) {color_mapping[p_id]}/{color_mapping[s_id]} Tefzel milspec single conductor wire'

                values.append((part_number + str(s_id), 2, description, str(mm_2), awg, p_id, f'[{str(s_id)}]', 7))

    return values


def preload_database(con, cur):

    data = (
        ('Unknown', '', '', '', ''),
        ('TE', '1-800-522-6752', '', '', 'https://www.te.com/en/home.html'),
        ('Bosch', '+49 304 036 94077',
         'Robert-Bosch-Platz 1\n70839 Gerlingen-Schillerhöhe\nGERMANY\n',
         'Connectors-Webshop-Hotline.PSCTS1-CO@de.bosch.com',
         'https://bosch-connectors.com/bcp/b2bshop-psconnectors/en/EUR'),
        ('Aptiv', '', '', '', 'https://www.aptiv.com/en/contact'),
        ('Molex', '+800-786-6539', '2222 Wellington Ct\nLisle, IL 60532, USA', '',
         'https://www.molex.com/en-us/products/connectors'),
        ('EPC', '', '', '', ''),
        ('Yazaki', '', '', '', ''),
    )

    cur.executemany('INSERT INTO manufacturers (name, phone, address, email, website) '
                    'VALUES (?, ?, ?, ?, ?);', data)

    cur.execute('INSERT INTO cads (path) VALUES("Not Entered");')
    con.commit()

    cur.execute('INSERT INTO datasheets (path) VALUES("Not Entered");')
    con.commit()

    cur.execute('INSERT INTO images (path) VALUES("Not Entered");')
    con.commit()

    cur.execute('INSERT INTO series (name) VALUES("Unknown");')
    con.commit()

    cur.execute('INSERT INTO families (name) VALUES("Unknown");')
    con.commit()

    data = (("Unknown",), ("Male",), ("Female",))
    cur.executemany('INSERT INTO genders (name) VALUES(?);', data)
    con.commit()

    data = (("Unknown",), ("Left",), ("Right",), ("Straight",), ("90°",), ("180°",), ("270°",))
    cur.executemany('INSERT INTO directions (name) VALUES(?);', data)
    con.commit()

    cur.executemany('INSERT INTO temperatures (id, name) VALUES (?, ?);', _build_temps())
    con.commit()

    data = (
        ('N/A', 'Unknown'),
        ('Sn', 'Tin'),
        ('Cu', 'Copper'),
        ('Al', 'Aluminum'),
        ('Au', 'Gold'),
        ('Ag', 'Silver'),
        ('Ag/Cu', 'Silver-plated Copper'),
        ('Sn/Cu', 'Tin-plated Copper'),
        ('Au/Cu', 'Gold-plated Copper'),
        ('Ag/Al', 'Silver-plated Aluminum'),
        ('Sn/Al', 'Tin-plated Aluminum'),
        ('Au/Al', 'Gold-plated Aluminum')
    )

    cur.executemany('INSERT INTO materials (symbol, desc) VALUES(?, ?);', data)
    con.commit()

    data = (
        ('Unknown/None',),
        ('Cavity Lock',),
        ('Locking Lance',),
        ('Flex Arm',),
        ('Insert Molded',),
        ('Molded On',),
        ('Nose Piece',),
        ('Press Fit',)
    )

    cur.executemany('INSERT INTO cavity_locks (name) VALUES (?);', data)
    con.commit()

    data = (
        (0, 'Black', 0x000000),
        (1, 'Brown', 0x8C7355),
        (2, 'Red', 0xFE0000),
        (3, 'Orange', 0xFFA500),
        (4, 'Yellow', 0xFFFF01),
        (5, 'Green', 0x28C629),
        (6, 'Blue', 0x0000FE),
        (7, 'Violet', 0x9400D4),
        (8, 'Gray', 0xA1A1A1),
        (9, 'White', 0xFFFFFF),
        (10, 'Natural', 0xE5D3BF),
        (11, 'Dark Red', 0x950606),
        (12, 'Red Brown', 0x942222),
        (13, 'Light Blue', 0x90D5FF),
        (14, 'Light Gray', 0xD3D3D3),
        (15, 'Transparent', 0xFFFFFF)
    )

    cur.executemany('INSERT INTO colors (id, name, rgb) VALUES(?, ?, ?);', data)
    con.commit()

    data = (
        (0, '0', 'No Protection', 'No protection against ingress of water.', None),
        (1, '1', 'Dripping water', 'Dripping water (vertically falling drops) shall have no unsafe effect on the specimen when mounted upright.', open(f'{BASE_PATH}/images/IPX1.png', 'rb').read()),
        (2, '2', 'Dripping water when tilted at 15°', 'Vertically dripping water shall have no harmful effect when the enclosure is tilted at an angle of 15° from its normal position.', open(f'{BASE_PATH}/images/IPX2.png', 'rb').read()),
        (3, '3', 'Spraying water', 'Water falling as a spray at any angle up to 60° from the vertical shall have no harmful effect.', open(f'{BASE_PATH}/images/IPX3.png', 'rb').read()),
        (4, '4', 'Splashing water', 'Water splashing against the enclosure from any direction shall have no harmful effect.', open(f'{BASE_PATH}/images/IPX4.png', 'rb').read()),
        (5, '5', 'Water jets', 'Water projected by a nozzle (6.3 mm) against enclosure from any direction shall have no harmful effects.', open(f'{BASE_PATH}/images/IPX5.png', 'rb').read()),
        (6, '6', 'Powerful water jets', 'Water projected in powerful jets (12.5 mm nozzle) against the enclosure from any direction shall have no harmful effects.', open(f'{BASE_PATH}/images/IPX6.png', 'rb').read()),
        (7, '7', 'Immersion, up to 1 meter', 'Ingress of water in harmful quantity shall not be possible when the enclosure is immersed in water.', open(f'{BASE_PATH}/images/IPX7.png', 'rb').read()),
        (8, '8', 'Immersion, 1 meter or more depth', 'The equipment is suitable for continuous immersion in water.', open(f'{BASE_PATH}/images/IPX8.png', 'rb').read()),
        (9, '9', 'Powerful high-temperature water jets', 'Protected against close-range high-pressure, high-temperature spray downs.', open(f'{BASE_PATH}/images/IPX9.png', 'rb').read()),
        (10, '6K', 'Powerful water jets with increased pressure', 'Water projected in powerful jets (6.3 mm nozzle) against the enclosure from any direction, under elevated pressure.', open(f'{BASE_PATH}/images/IPX6K.png', 'rb').read()),
        (11, '9K', 'Steam Cleaning', 'Protection against high-pressure, high-temperature jet sprays, wash-downs or steam-cleaning procedures', open(f'{BASE_PATH}/images/IPX9K.png', 'rb').read()),
        (12, 'X', 'Unknown', 'No data is available to specify a protection rating about this criterion.', None)
    )

    cur.executemany('INSERT INTO ip_fluids (id, name, short_desc, description, icon_data) VALUES (?, ?, ?, ?, ?);', data)
    con.commit()

    data = (
        (0, '0', 'No Protection', 'No protection against contact and ingress of objects.', None),
        (1, '1', '>= 50.00mm sized objects', 'Any large surface of the body, such as the back of a hand, but no protection against deliberate contact with a body part.', open(f'{BASE_PATH}/images/IP1X.png', 'rb').read()),
        (2, '2', '>= 12.50mm sized objects', 'Fingers or similar objects.', open(f'{BASE_PATH}/images/IP2X.png', 'rb').read()),
        (3, '3', '>= 2.50mm sized objects', 'Tools, thick wires, etc.', open(f'{BASE_PATH}/images/IP3X.png', 'rb').read()),
        (4, '4', '>= 1.00mm sized objects', 'Most wires, slender screws, large ants, etc.', open(f'{BASE_PATH}/images/IP4X.png', 'rb').read()),
        (5, '5', 'Dust Protected', 'Ingress of dust is not entirely prevented.', open(f'{BASE_PATH}/images/IP5X.png', 'rb').read()),
        (6, '6', 'Dust Tight', 'No ingress of dust.', open(f'{BASE_PATH}/images/IP6X.png', 'rb').read()),
        (7, 'X', 'Unknown', 'No data is available to specify a protection rating about this criterion.', None)
    )

    cur.executemany('INSERT INTO ip_solids (id, name, short_desc, description, icon_data) VALUES (?, ?, ?, ?, ?);', data)
    con.commit()

    data = (
        ('D', 'Wire'),
        ('G', 'Oil resistant'),
        ('F', 'Oil resistant'),
        ('H', 'High voltage apparatus'),
        ('M', 'Motion during water test'),
        ('S', 'Stationary during water test'),
        ('W', 'Weather conditions')
    )

    cur.executemany('INSERT INTO ip_supps (name, description) VALUES (?, ?);', data)
    con.commit()

    data = (('IPXX', 7, 12), ('IP01', 0, 1), ('IP02', 0, 2), ('IP03', 0, 3),
            ('IP04', 0, 4), ('IP05', 0, 5), ('IP06', 0, 6), ('IP07', 0, 7),
            ('IP08', 0, 8), ('IP09', 0, 9), ('IP06K', 0, 10), ('IP09K', 0, 11),
            ('IP0X', 0, 12), ('IP10', 1, 0), ('IP11', 1, 1), ('IP12', 1, 2),
            ('IP13', 1, 3), ('IP14', 1, 4), ('IP15', 1, 5), ('IP16', 1, 6),
            ('IP17', 1, 7), ('IP18', 1, 8), ('IP19', 1, 9), ('IP16K', 1, 10),
            ('IP19K', 1, 11), ('IP1X', 1, 12), ('IP20', 2, 0), ('IP21', 2, 1),
            ('IP22', 2, 2), ('IP23', 2, 3), ('IP24', 2, 4), ('IP25', 2, 5),
            ('IP26', 2, 6), ('IP27', 2, 7), ('IP28', 2, 8), ('IP29', 2, 9),
            ('IP26K', 2, 10), ('IP29K', 2, 11), ('IP2X', 2, 12), ('IP30', 3, 0),
            ('IP31', 3, 1), ('IP32', 3, 2), ('IP33', 3, 3), ('IP34', 3, 4),
            ('IP35', 3, 5), ('IP36', 3, 6), ('IP37', 3, 7), ('IP38', 3, 8),
            ('IP39', 3, 9), ('IP36K', 3, 10), ('IP39K', 3, 11), ('IP3X', 3, 12),
            ('IP40', 4, 0), ('IP41', 4, 1), ('IP42', 4, 2), ('IP43', 4, 3),
            ('IP44', 4, 4), ('IP45', 4, 5), ('IP46', 4, 6), ('IP47', 4, 7),
            ('IP48', 4, 8), ('IP49', 4, 9), ('IP46K', 4, 10), ('IP49K', 4, 11),
            ('IP4X', 4, 12), ('IP50', 5, 0), ('IP51', 5, 1), ('IP52', 5, 2),
            ('IP53', 5, 3), ('IP54', 5, 4), ('IP55', 5, 5), ('IP56', 5, 6),
            ('IP57', 5, 7), ('IP58', 5, 8), ('IP59', 5, 9), ('IP56K', 5, 10),
            ('IP59K', 5, 11), ('IP5X', 5, 12), ('IP60', 6, 0), ('IP61', 6, 1),
            ('IP62', 6, 2), ('IP63', 6, 3), ('IP64', 6, 4), ('IP65', 6, 5),
            ('IP66', 6, 6), ('IP67', 6, 7), ('IP68', 6, 8), ('IP69', 6, 9),
            ('IP66K', 6, 10), ('IP69K', 6, 11), ('IP6X', 6, 12), ('IPX0', 7, 0),
            ('IPX1', 7, 1), ('IPX2', 7, 2), ('IPX3', 7, 3), ('IPX4', 7, 4),
            ('IPX5', 7, 5), ('IPX6', 7, 6), ('IPX7', 7, 7), ('IPX8', 7, 8),
            ('IPX9', 7, 9), ('IPX6K', 7, 10), ('IPX9K', 7, 11))

    cur.executemany('INSERT INTO ip_ratings (name, solid_id, fluid_id) VALUES (?, ?, ?);', data)
    con.commit()

    cur.execute('INSERT INTO cpa_locks (part_number, description) VALUES("not-applicable", "Unknown/Not Applicable");')
    con.commit()

    cur.execute('INSERT INTO tpa_locks (part_number, description) VALUES("not-applicable", "Unknown/Not Applicable");')
    con.commit()

    cur.execute('INSERT INTO seals (part_number, description) VALUES("not-applicable", "Unknown/Not Applicable");')
    con.commit()

    cur.execute('INSERT INTO boots (part_number, description) VALUES("not-applicable", "Unknown/Not Applicable");')
    con.commit()

    cur.execute('INSERT INTO covers (part_number, description) VALUES("not-applicable", "Unknown/Not Applicable");')
    con.commit()

    cur.execute('INSERT INTO terminals (part_number, description) VALUES("not-applicable", "Unknown/Not Applicable");')
    con.commit()

    cur.executemany('INSERT INTO wires (part_number, mfg_id, description, size_mm2, size_awg, primary_color_id, addl_color_ids, core_material_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?);', _build_wires())
    con.commit()

    cur.execute('INSERT INTO housings (part_number, description) VALUES("not-applicable", "Unknown/Not Applicable");')
    con.commit()

    data = (
        (0, 'Not applicable'),
        (1, 'Long-Term Fluid Exposure at High Temperatures')
    )
    cur.executemany('INSERT INTO transition_protections (id, name) VALUES (?, ?);', data)
    con.commit()

    data = (
        (0, '', 'None'),
        (1, '86', 'Hot-melt, high performance.'),
        (2, '225', 'Precoated latent-curing epoxy/polyamide.')
    )
    cur.executemany('INSERT INTO transition_adhesives (id, code, description) VALUES (?, ?, ?);', data)
    con.commit()

    data = (
        (0, 'Not Applicable'),
        (1, 'Fluid Resistant Modified Elastomer',)
    )

    cur.executemany('INSERT INTO transition_materials (id, name) VALUES (?, ?);', data)
    con.commit()

    data = (
        (0, 'Not Applicable'),
        (1, 'DR-25')
    )
    cur.executemany('INSERT INTO transition_families (id, name) VALUES (?, ?);', data)
    con.commit()

    data = (
        (0, 'Not applicable'),
        (1, 'Tee'),
        (2, 'Tee (offset)'),
        (3, 'Wye'),
        (4, 'Wye (lowercase)'),
        (5, 'Double Wye'),
        (6, 'Manifold (straight)'),
        (7, 'Manifold (angled)'),
        (8, 'Straight'),
        (9, 'Cross'),
        (10, 'Tee (bulbous)'),
        (11, 'Tee (bulbous, offset)'),
        (12, 'Wye (bulbous)'),
        (13, 'Wye (bulbous, lowercase)'),
        (14, 'Double Wye (bulbous)'),
        (15, 'Manifold (bulbous, straight)'),
        (16, 'Manifold (bulbous, angled)'),
        (17, 'Straight (bulbous)'),
        (18, 'Cross (bulbous)'),
        (19, 'Double U'),
        (20, 'Double Y'),
        (21, 'Double Y (bulbous)')
    )
    cur.executemany('INSERT INTO transition_shapes (id, name) VALUES (?, ?);', data)
    con.commit()

    data = (
        (1, 2.8, 7.1),  # 502A812
        (2, 3.0, 6.6),  # 302A012, 322A112, 322A123, 342A112
        (3, 3.3, 6.6),  # 382A012
        (4, 3.5, 6.6),  # 562A011
        (5, 3.5, 9.4),  # 562A022
        (6, 3.6, 6.6),  # 301A011, 342A012, 342A024, 462A011
        (7, 3.8, 6.6),  # 322A012
        (8, 4.0, 9.0),  # 382W042
        (9, 4.3, 6.6),  # 602A114
        (10, 4.3, 11.4),  # 602A114
        (11, 4.6, 14.0),  # 403A123
        (12, 4.8, 12.2),  # 502A823
        (13, 5.1, 9.7),  # 422A813
        (14, 5.1, 10.1),  # 322A412
        (15, 5.3, 9.6),  # 322A315
        (16, 5.3, 10.2),  # 362A114
        (17, 5.3, 18.0),  # 322W204
        (18, 5.6, 10.6),  # 342A215
        (19, 5.6, 13.2),  # 422A716
        (20, 5.8, 13.2),  # 322A112, 322A134, 322A148
        (21, 6.0, 13.0),  # 462W023
        (22, 6.1, 13.2),  # 302A012, 302A024, 342A034, 342A112, 342A124, 382A012, 382A023
        (23, 6.3, 12.7),  # 462A214
        (24, 6.3, 26.0),  # 322W204
        (25, 6.6, 13.2),  # 322A024, 342A012, 462A011
        (26, 6.9, 13.2),  # 301A022, 462A023, 562A011, 562A022, 562A043
        (27, 7.1, 12.7),  # 402A013
        (28, 7.1, 20.3),  # 502A834
        (29, 7.3, 13.2),  # 342A313
        (30, 7.4, 13.2),  # 322A012
        (31, 7.4, 24.0),  # 362W214
        (32, 7.7, 15.2),  # 322A423
        (33, 7.9, 18.7),  # 342A215
        (34, 8.0, 20.0),  # 382W042
        (35, 8.1, 22.0),  # 403A134
        (36, 8.4, 13.2),  # 342A323
        (37, 8.6, 15.2),  # 362A024
        (38, 8.9, 17.7),  # 322A412
        (39, 8.9, 17.8),  # 322A514, 422A414, 423A014
        (40, 9.4, 19.3),  # 422A716
        (41, 9.7, 19.3),  # 462A034, 562A022, 562A022, 562A054
        (42, 9.9, 18.0),  # 342A313
        (43, 9.9, 27.9),  # 342A313
        (44, 10.0, 25.0),  # 462W023
        (45, 10.2, 20.0),  # 301A028
        (46, 10.2, 20.3),  # 322A434, 423A014
        (47, 10.7, 20.0),  # 362A014
        (48, 11.5, 18.2),  # 422A616
        (49, 11.9, 22.8),  # 502A812
        (50, 12.4, 26.9),  # 302A024, 302A037, 322A037, 322A123, 322A158, 342A124, 342A138, 382A023, 382A034, 462A046
        (51, 12.5, 27.0),  # 381A115
        (52, 12.5, 28.5),  # 381A115
        (53, 12.7, 26.9),  # 322A134, 342A024, 382A046
        (54, 12.7, 29.5),  # 403A145, 403A155
        (55, 12.7, 36.0),  # 502A845
        (56, 13.0, 26.9),  # 562A043, 562A067
        (57, 13.2, 26.9),  # 322A024, 462A023
        (58, 13.5, 26.9),  # 301A034, 341A015
        (59, 13.5, 28.4),  # 341A015
        (60, 13.7, 26.9),  # 342A034, 342A058
        (61, 13.7, 40.0),  # 362W214
        (62, 14.0, 24.1),  # 342A323
        (63, 14.0, 41.4),  # 342A323
        (64, 15.2, 25.4),  # 422A813
        (65, 15.2, 30.5),  # 322A514, 422A414, 423A014, 462A214
        (66, 15.3, 30.4),  # 322A434
        (67, 15.7, 30.5),  # 362A014
        (68, 16.3, 29.5),  # 322A315
        (69, 17.5, 25.4),  # 402A013
        (70, 17.5, 31.7),  # 403A123
        (71, 17.7, 35.5),  # 322A423
        (72, 18.0, 38.6),  # 382A034
        (73, 18.3, 35.6),  # 362A024
        (74, 18.5, 38.6),  # 562A054
        (75, 18.8, 30.5),  # 362A114
        (76, 18.8, 38.6),  # 462A034
        (77, 19.2, 27.4),  # 422A616
        (78, 20.3, 34.3),  # 502A823
        (79, 22.8, 44.4),  # 403A134
        (80, 25.4, 33.3),  # 602A114
        (81, 25.4, 55.6),  # 302A037, 322A148, 322A158, 342A138, 462A046
        (82, 26.7, 55.6),  # 562A067
        (83, 26.9, 55.6),  # 342A058, 382A046
        (84, 27.2, 55.6),  # 322A037
        (85, 27.4, 45.7),  # 462A060
        (86, 27.7, 52.1),  # 502A834
        (87, 30.2, 55.6),  # 301A048
        (88, 35.6, 62.5),  # 403A145
        (89, 35.6, 70.1),  # 403A155
        (90, 43.9, 83.8),  # 502A845
        (91, 54.6, 91.4),  # 462A060
        (92, 25.9, 55.6),  # 382A046
    )

    cur.executemany('INSERT INTO transition_sizes (id, min, max) VALUES (?, ?, ?);', data)
    con.commit()

    data = (
        (0, 'NA', 'Not applicable', 0, 0, 0, 0, 0, 0, 0, 0),
        (1, '301A', '', 1, 3, 1, 1, 6, 51, 1, 10),  #
        (2, '302A', '', 1, 3, 1, 1, 6, 51, 1, 10),  #
        (3, '322A0', '', 1, 3, 1, 1, 6, 51, 1, 11),  #
        (4, '322A1', '', 1, 3, 1, 1, 6, 51, 1, 10),  #
        (5, '322A3', '', 1, 3, 1, 1, 6, 51, 1, 11),  #
        (6, '322A4', '', 1, 3, 1, 1, 6, 51, 1, 10),  #
        (7, '322A5', '', 1, 3, 1, 1, 6, 51, 1, 11),  #
        (8, '322W', '', 1, 3, 1, 1, 6, 51, 1, 11),  #
        (9, '341A', '', 1, 3, 1, 1, 6, 51, 1, 13),  #
        (10, '342A0', '', 1, 3, 1, 1, 6, 51, 1, 13),  #
        (11, '342A1', '', 1, 3, 1, 1, 6, 51, 1, 13),  #
        (12, '342A2', '', 1, 3, 1, 1, 6, 51, 1, 12),  #
        (13, '342A3', '', 1, 3, 1, 1, 6, 51, 1, 4),  #
        (14, '362A', '', 1, 3, 1, 1, 6, 51, 1, 13),  #
        (15, '362W', '', 1, 3, 1, 1, 6, 51, 1, 13),  #
        (16, '381A', '', 1, 3, 1, 1, 6, 51, 1, 12),  #
        (17, '382A', '', 1, 3, 1, 1, 6, 51, 1, 12),  #
        (18, '382W', '', 1, 3, 1, 1, 6, 51, 1, 12),  #
        (19, '402A', '', 1, 4, 1, 1, 6, 51, 1, 19),  #
        (20, '403A', '', 1, 4, 1, 1, 6, 51, 1, 8),  #
        (21, '422A4', '', 1, 4, 1, 1, 6, 51, 1, 15),  #
        (22, '422A6', '', 1, 4, 1, 1, 6, 51, 1, 18),  #
        (23, '422A7', '', 1, 4, 1, 1, 6, 51, 1, 9),  #
        (24, '422A8', '', 1, 4, 1, 1, 6, 51, 1, 15),  #
        (25, '423A', '', 1, 4, 1, 1, 6, 51, 1, 15),  #
        (26, '462A0', '', 1, 4, 1, 1, 6, 51, 1, 21),  #
        (27, '462A2', '', 1, 4, 1, 1, 6, 51, 1, 16),  #
        (28, '462W', '', 1, 4, 1, 1, 6, 51, 1, 21),  #
        (29, '502A', '', 1, 5, 1, 1, 6, 51, 1, 8),  #
        (30, '562A', '', 1, 5, 1, 1, 6, 51, 1, 14),  #
        (31, '602A', '', 1, 6, 1, 1, 6, 51, 1, 8)  #
    )
    cur.executemany('INSERT INTO transition_series '
                    '(id, name, description, mfg_id, branch_count, tran_material_id, '
                    'tran_family_id, min_temp_id, max_temp_id, tran_protection_id, '
                    'tran_shape_id) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);', data)
    con.commit()

    data = (
        ('301A011-25-0', 1, 0, '[6, 6, 6]'),
        ('301A022-25-0', 1, 0, '[26, 26, 26]'),
        ('301A028-25-0', 1, 0, '[45, 45, 45]'),
        ('301A034-25-0', 1, 0, '[58, 58, 58]'),
        ('301A048-25-0', 1, 0, '[87, 87, 87]'),
        ('301A011-25/86-0', 1, 1, '[6, 6, 6]'),
        ('301A022-25/86-0', 1, 1, '[26, 26, 26]'),
        ('301A028-25/86-0', 1, 1, '[45, 45, 45]'),
        ('301A034-25/86-0', 1, 1, '[58, 58, 58]'),
        ('301A048-25/86-0', 1, 1, '[87, 87, 87]'),
        ('301A011-25/225-0', 1, 2, '[6, 6, 6]'),
        ('301A022-25/225-0', 1, 2, '[26, 26, 26]'),
        ('301A028-25/225-0', 1, 2, '[45, 45, 45]'),
        ('301A034-25/225-0', 1, 2, '[58, 58, 58]'),
        ('301A048-25/225-0', 1, 2, '[87, 87, 87]'),
        ('302A012-25-0', 2, 0, '[22, 2, 2]'),
        ('302A024-25-0', 2, 0, '[50, 22, 22]'),
        ('302A012-25/86-0', 2, 1, '[22, 2, 2]'),
        ('302A024-25/86-0', 2, 1, '[50, 22, 22]'),
        ('302A012-25/225-0', 2, 2, '[22, 2, 2]'),
        ('302A024-25/225-0', 2, 2, '[50, 22, 22]'),
        ('322A012-25-0', 3, 0, '[30, 7, 7]'),
        ('322A024-25-0', 3, 0, '[57, 25, 25]'),
        ('322A037-25-0', 3, 0, '[84, 57, 57]'),
        ('322A012-25/86-0', 3, 1, '[30, 7, 7]'),
        ('322A024-25/86-0', 3, 1, '[57, 25, 25]'),
        ('322A037-25/86-0', 3, 1, '[84, 57, 57]'),
        ('322A012-25/225-0', 3, 2, '[30, 7, 7]'),
        ('322A024-25/225-0', 3, 2, '[57, 25, 25]'),
        ('322A037-25/225-0', 3, 2, '[84, 57, 57]'),
        ('322A112-25-0', 4, 0, '[20, 20, 2]'),
        ('322A123-25-0', 4, 0, '[50, 50, 2]'),
        ('322A134-25-0', 4, 0, '[53, 53, 20]'),
        ('322A148-25-0', 4, 0, '[81, 81, 20]'),
        ('322A158-25-0', 4, 0, '[81, 81, 50]'),
        ('322A112-25/86-0', 4, 1, '[20, 20, 2]'),
        ('322A123-25/86-0', 4, 1, '[50, 50, 2]'),
        ('322A134-25/86-0', 4, 1, '[53, 53, 20]'),
        ('322A148-25/86-0', 4, 1, '[81, 81, 20]'),
        ('322A158-25/86-0', 4, 1, '[81, 81, 50]'),
        ('322A112-25/225-0', 4, 2, '[20, 20, 2]'),
        ('322A123-25/225-0', 4, 2, '[50, 50, 2]'),
        ('322A134-25/225-0', 4, 2, '[53, 53, 20]'),
        ('322A148-25/225-0', 4, 2, '[81, 81, 20]'),
        ('322A158-25/225-0', 4, 2, '[81, 81, 50]'),
        ('322A315-25-0', 5, 0, '[68, 15, 15]'),
        ('322A315-25/86-0', 5, 1, '[68, 15, 15]'),
        ('322A315-25/225-0', 5, 2, '[68, 15, 15]'),
        ('322A412-25-0', 6, 0, '[38, 14, 14]'),
        ('322A423-25-0', 6, 0, '[71, 32, 32]'),
        ('322A434-25-0', 6, 0, '[66, 46, 46]'),
        ('322A412-25/86-0', 6, 1, '[38, 14, 14]'),
        ('322A423-25/86-0', 6, 1, '[71, 32, 32]'),
        ('322A434-25/86-0', 6, 1, '[66, 46, 46]'),
        ('322A412-25/225-0', 6, 2, '[38, 14, 14]'),
        ('322A423-25/225-0', 6, 2, '[71, 32, 32]'),
        ('322A434-25/225-0', 6, 2, '[66, 46, 46]'),
        ('322A514-25-0', 7, 0, '[65, 39, 39]'),
        ('322A514-25/86-0', 7, 1, '[65, 39, 39]'),
        ('322A514-25/225-0', 7, 2, '[65, 39, 39]'),
        ('322W204-25-0', 8, 0, '[24, 17, 17]'),
        ('322W204-25/86-0', 8, 1, '[24, 17, 17]'),
        ('322W204-25/225-0', 8, 2, '[24, 17, 17]'),
        ('341A015-25-0', 9, 0, '[59, 58, 58]'),
        ('341A015-25/86-0', 9, 0, '[59, 58, 58]'),
        ('341A015-25/225-0', 9, 0, '[59, 58, 58]'),
        ('342A012-25-0', 10, 0, '[26, 26, 6]'),
        ('342A024-25-0', 10, 0, '[53, 53, 6]'),
        ('342A034-25-0', 10, 0, '[60, 60, 22]'),
        ('342A058-25-0', 10, 0, '[83, 83, 60]'),
        ('342A012-25/86-0', 10, 1, '[26, 26, 6]'),
        ('342A024-25/86-0', 10, 1, '[53, 53, 6]'),
        ('342A034-25/86-0', 10, 1, '[60, 60, 22]'),
        ('342A058-25/86-0', 10, 1, '[83, 83, 60]'),
        ('342A012-25/225-0', 10, 2, '[26, 26, 6]'),
        ('342A024-25/225-0', 10, 2, '[53, 53, 6]'),
        ('342A034-25/225-0', 10, 2, '[60, 60, 22]'),
        ('342A058-25/225-0', 10, 2, '[83, 83, 60]'),
        ('342A112-25-0', 11, 0, '[22, 2, 2]'),
        ('342A124-25-0', 11, 0, '[50, 22, 22]'),
        ('342A138-25-0', 11, 0, '[81, 50, 50]'),
        ('342A112-25/86-0', 11, 1, '[22, 2, 2]'),
        ('342A124-25/86-0', 11, 1, '[50, 22, 22]'),
        ('342A138-25/86-0', 11, 1, '[81, 50, 50]'),
        ('342A112-25/225-0', 11, 2, '[22, 2, 2]'),
        ('342A124-25/225-0', 11, 2, '[50, 22, 22]'),
        ('342A138-25/225-0', 11, 2, '[81, 50, 50]'),
        ('342A215-25-0', 12, 0, '[33, 18, 18]'),
        ('342A215-25/86-0', 12, 1, '[33, 18, 18]'),
        ('342A215-25/225-0', 12, 2, '[33, 18, 18]'),
        ('342A313-25-0', 13, 0, '[43, 42, 29]'),
        ('342A323-25-0', 13, 0, '[63, 62, 36]'),
        ('342A313-25/86-0', 13, 1, '[43, 42, 29]'),
        ('342A323-25/86-0', 13, 1, '[63, 62, 36]'),
        ('342A313-25/225-0', 13, 2, '[43, 42, 29]'),
        ('342A323-25/225-0', 13, 2, '[63, 62, 36]'),
        ('362A014-25-0', 14, 0, '[67, 67, 47]'),
        ('362A024-25-0', 14, 0, '[73, 73, 37]'),
        ('362A114-25-0', 14, 0, '[75, 75, 16]'),
        ('362A014-25/86-0', 14, 1, '[67, 67, 47]'),
        ('362A024-25/86-0', 14, 1, '[73, 73, 37]'),
        ('362A114-25/86-0', 14, 1, '[75, 75, 16]'),
        ('362A014-25/225-0', 14, 2, '[67, 67, 47'),
        ('362A024-25/225-0', 14, 2, '[73, 73, 37]'),
        ('362A114-25/225-0', 14, 2, '[75, 75, 16]'),
        ('362W214-25-0', 15, 0, '[61, 51, 51]'),
        ('362W214-25/86-0', 15, 2, '[61, 51, 51]'),
        ('362W214-25/225-0', 15, 2, '[61, 51, 51]'),
        ('381A115-25-0', 16, 0, '[52, 51, 51]'),
        ('381A115-25/86-0', 16, 2, '[52, 51, 51]'),
        ('381A115-25/225-0', 16, 2, '[52, 51, 51]'),
        ('382A012-25-0', 17, 0, '[22, 3, 3]'),
        ('382A023-25-0', 17, 0, '[50, 22, 22]'),
        ('382A034-25-0', 17, 0, '[72, 50, 50]'),
        ('382A046-25-0', 17, 0, '[92, 50, 50]'),
        ('382A012-25/86-0', 17, 1, '[22, 3, 3]'),
        ('382A023-25/86-0', 17, 1, '[50, 22, 22]'),
        ('382A034-25/86-0', 17, 1, '[72, 50, 50]'),
        ('382A046-25/86-0', 17, 1, '[92, 50, 50]'),
        ('382A012-25/225-0', 17, 2, '[22, 3, 3]'),
        ('382A023-25/225-0', 17, 2, '[50, 22, 22]'),
        ('382A034-25/225-0', 17, 2, '[72, 50, 50]'),
        ('382A046-25/225-0', 17, 2, '[92, 50, 50]'),
        ('382W042-25-0', 18, 0, '[34, 8, 8]'),
        ('382W042-25/86-0', 1, 18, '[34, 8, 8]'),
        ('382W042-25/225-0', 18, 2, '[34, 8, 8]'),
        ('402A013-25-0', 19, 0, '[69, 27, 27, 27]'),
        ('402A013-25/86-0', 19, 1, '[69, 27, 27, 27]'),
        ('402A013-25/225-0', 19, 2, '[69, 27, 27, 27]'),
        ('403A123-25-0', 20, 0, '[70, 11, 11, 11]'),
        ('403A134-25-0', 20, 0, '[79, 35, 35, 35]'),
        ('403A145-25-0', 20, 0, '[88, 54, 54, 54]'),
        ('403A155-25-0', 20, 0, '[89, 54, 54, 54]'),
        ('403A123-25/86-0', 20, 1, '[70, 11, 11, 11]'),
        ('403A134-25/86-0', 20, 1, '[79, 35, 35, 35]'),
        ('403A145-25/86-0', 20, 1, '[88, 54, 54, 54]'),
        ('403A155-25/86-0', 20, 1, '[89, 54, 54, 54]'),
        ('403A123-25/225-0', 20, 2, '[70, 11, 11, 11]'),
        ('403A134-25/225-0', 20, 2, '[79, 35, 35, 35]'),
        ('403A145-25/225-0', 20, 2, '[88, 54, 54, 54]'),
        ('403A155-25/225-0', 20, 2, '[89, 54, 54, 54]'),
        ('422A414-25-0', 21, 0, '[65, 39, 39, 39]'),
        ('422A414-25/86-0', 21, 1, '[65, 39, 39, 39]'),
        ('422A414-25/225-0', 21, 2, '[65, 39, 39, 39]'),
        ('422A616-25-0', 22, 0, '[77, 48, 77, 48]'),
        ('422A616-25/86-0', 22, 1, '[77, 48, 77, 48]'),
        ('422A616-25/225-0', 22, 2, '[77, 48, 77, 48]'),
        ('422A716-25-0', 23, 0, '[40, 19, 40, 19]'),
        ('422A716-25/86-0', 23, 1, '[40, 19, 40, 19]'),
        ('422A716-25/225-0', 23, 2, '[40, 19, 40, 19]'),
        ('422A813-25-0', 24, 0, '[64, 13, 13, 64]'),
        ('422A813-25/86-0', 24, 1, '[64, 13, 13, 64]'),
        ('422A813-25/225-0', 24, 2, '[64, 13, 13, 64]'),
        ('423A014-25-0', 25, 0, '[65, 39, 46, 65]'),
        ('423A014-25/86-0', 25, 1, '[65, 39, 46, 65]'),
        ('423A014-25/225-0', 25, 2, '[65, 39, 46, 65]'),
        ('462A011-25-0', 26, 0, '[25, 6, 6, 6]'),
        ('462A023-25-0', 26, 0, '[57, 25, 25, 25]'),
        ('462A034-25-0', 26, 0, '[76, 41, 41, 41]'),
        ('462A046-25-0', 26, 0, '[81, 50, 50, 50]'),
        ('462A060-25-0', 26, 0, '[91, 85, 85, 85]'),
        ('462A011-25/86-0', 26, 1, '[25, 6, 6, 6]'),
        ('462A023-25/86-0', 26, 1, '[57, 25, 25, 25]'),
        ('462A034-25/86-0', 26, 1, '[76, 41, 41, 41]'),
        ('462A046-25/86-0', 26, 1, '[81, 50, 50, 50]'),
        ('462A060-25/86-0', 26, 1, '[91, 85, 85, 85]'),
        ('462A011-25/225-0', 26, 2, '[25, 6, 6, 6]'),
        ('462A023-25/225-0', 26, 2, '[57, 25, 25, 25]'),
        ('462A034-25/225-0', 26, 2, '[76, 41, 41, 41]'),
        ('462A046-25/225-0', 26, 2, '[81, 50, 50, 50]'),
        ('462A060-25/225-0', 26, 2, '[91, 85, 85, 85]'),
        ('462A214-25-0', 27, 0, '[65, 23, 23, 65]'),
        ('462A214-25/86-0', 27, 1, '[65, 23, 23, 65]'),
        ('462A214-25/225-0', 27, 2, '[65, 23, 23, 65]'),
        ('462W023-25-0', 28, 0, '[44, 21, 21, 21]'),
        ('462W023-25/86-0', 28, 1, '[44, 21, 21, 21]'),
        ('462W023-25/225-0', 28, 2, '[44, 21, 21, 21]'),
        ('502A812-25-0', 29, 0, '[49, 1, 1, 1, 1]'),
        ('502A823-25-0', 29, 0, '[78, 12, 12, 12, 12]'),
        ('502A834-25-0', 29, 0, '[86, 28, 28, 28, 28]'),
        ('502A845-25-0', 29, 0, '[90, 55, 55, 55, 55]'),
        ('502A812-25/86-0', 29, 1, '[49, 1, 1, 1, 1]'),
        ('502A823-25/86-0', 29, 1, '[78, 12, 12, 12, 12]'),
        ('502A834-25/86-0', 29, 1, '[86, 28, 28, 28, 28]'),
        ('502A845-25/86-0', 29, 1, '[90, 55, 55, 55, 55]'),
        ('502A812-25/225-0', 29, 2, '[49, 1, 1, 1, 1]'),
        ('502A823-25/225-0', 29, 2, '[78, 12, 12, 12, 12]'),
        ('502A834-25/225-0', 29, 2, '[86, 28, 28, 28, 28]'),
        ('502A845-25/225-0', 29, 2, '[90, 55, 55, 55, 55]'),
        ('562A011-25-0', 30, 0, '[26, 4, 4, 4, 4]'),
        ('562A022-25-0', 30, 0, '[41, 5, 5, 5, 5]'),
        ('562A032-25-0', 30, 0, '[41, 26, 26, 26, 26]'),
        ('562A043-25-0', 30, 0, '[56, 26, 26, 26, 26]'),
        ('562A054-25-0', 30, 0, '[74, 41, 41, 41, 41]'),
        ('562A067-25-0', 30, 0, '[82, 56, 56, 56, 56]'),
        ('562A011-25/86-0', 30, 1, '[26, 4, 4, 4, 4]'),
        ('562A022-25/86-0', 30, 1, '[41, 5, 5, 5, 5]'),
        ('562A032-25/86-0', 30, 1, '[41, 26, 26, 26, 26]'),
        ('562A043-25/86-0', 30, 1, '[56, 26, 26, 26, 26]'),
        ('562A054-25/86-0', 30, 1, '[74, 41, 41, 41, 41]'),
        ('562A067-25/86-0', 30, 1, '[82, 56, 56, 56, 56]'),
        ('562A011-25/225-0', 30, 2, '[26, 4, 4, 4, 4]'),
        ('562A022-25/225-0', 30, 2, '[41, 5, 5, 5, 5]'),
        ('562A032-25/225-0', 30, 2, '[41, 26, 26, 26, 26]'),
        ('562A043-25/225-0', 30, 2, '[56, 26, 26, 26, 26]'),
        ('562A054-25/225-0', 30, 2, '[74, 41, 41, 41, 41]'),
        ('562A067-25/225-0', 30, 2, '[82, 56, 56, 56, 56]'),
        ('602A114-25-0', 31, 0, '[80, 10, 10, 10, 10, 9]'),
        ('602A114-25/86-0', 31, 1, '[80, 10, 10, 10, 10, 9]'),
        ('602A114-25/225-0', 31, 2, '[80, 10, 10, 10, 10, 9]'),
    )

    cur.executemany('INSERT INTO transitions (part_number, tran_series_id, '
                    'tran_adhesive_id, tran_size_ids) VALUES (?, ?, ?, ?);', data)
    con.commit()


def read_csv(line):
    res = []
    item = ''
    quote = False

    for char in line:
        if char == '"':
            quote = not quote
            continue

        if char == ',' and not quote:
            res.append(item)
            item = ''
            continue

        item += char

    res.append(item)

    for i, item in enumerate(res):
        if item.isdigit():
            item = int(item)

        else:
            try:
                item = float(item)
            except:
                pass

        res[i] = item

    return res


def get_color_id(con, cur, color):
    if not color:
        return None

    cur.execute(f'SELECT id FROM colors WHERE name = "{color}";')
    res = cur.fetchall()
    return res[0][0]


def get_mfg_id(con, cur, mfg):
    cur.execute(f'SELECT id FROM manufacturers WHERE name = "{mfg}";')
    res = cur.fetchall()
    return res[0][0]


def get_material_id(con, cur, material):
    cur.execute(f'SELECT id FROM materials WHERE symbol = "{material}";')
    res = cur.fetchall()
    return res[0][0]


def get_cavity_lock_id(con, cur, name):
    if not name:
        return 1

    cur.execute(f'SELECT id FROM cavity_locks WHERE name = "{name}";')
    res = cur.fetchall()
    return res[0][0]


def get_temperature_id(con, cur, temp):
    if not temp:
        return 0

    if temp > 0:
        temp = f'+{temp}°C'
    else:
        temp = f'{temp}°C'

    cur.execute(f'SELECT id FROM temperatures WHERE name = "{temp}";')
    res = cur.fetchall()
    return res[0][0]


def get_image_id(con, cur, image):
    if not image:
        return 1

    cur.execute(f'SELECT id FROM images WHERE path = "{image}";')
    res = cur.fetchall()
    if res:
        return res[0][0]

    cur.execute(f'INSERT INTO images (path) VALUES ("{image}");')
    con.commit()
    return cur.lastrowid


def get_cad_id(con, cur, cad):
    if not cad:
        return 1

    cur.execute(f'SELECT id FROM cads WHERE path = "{cad}";')
    res = cur.fetchall()
    if res:
        return res[0][0]

    cur.execute(f'INSERT INTO cads (path) VALUES ("{cad}");')
    con.commit()
    return cur.lastrowid


def get_series_id(con, cur, series, mfg_id):
    if not series:
        return 1

    cur.execute(f'SELECT id FROM series WHERE name = "{series}" AND mfg_id = {mfg_id};')
    res = cur.fetchall()
    if res:
        return res[0][0]

    cur.execute(f'INSERT INTO series (mfg_id, name) VALUES ({mfg_id}, "{series}");')
    con.commit()
    return cur.lastrowid


def get_gender_id(con, cur, gender):
    if not gender:
        return 1

    cur.execute(f'SELECT id FROM genders WHERE name = "{gender}";')
    res = cur.fetchall()
    return res[0][0]


def get_direction_id(con, cur, direction):
    if not direction:
        return 1

    cur.execute(f'SELECT id FROM directions WHERE name = "{direction}";')
    res = cur.fetchall()
    if res:
        return res[0][0]

    cur.execute(f'INSERT INTO directions (name) VALUES ("{direction}");')
    con.commit()
    return cur.lastrowid


def get_family_id(con, cur, family, mfg_id):
    if not family:
        return 1

    cur.execute(f'SELECT id FROM families WHERE name = "{family}" AND mfg_id = {mfg_id};')
    res = cur.fetchall()
    if res:
        return res[0][0]

    cur.execute(f'INSERT INTO families (mfg_id, name) VALUES ({mfg_id}, "{family}");')
    con.commit()
    return cur.lastrowid


def load_tpa_locks(con, cur):
    with open(r'C:\Users\drsch\Desktop\HarnessMaker\tpa_locks.csv', 'r') as f:
        data = f.read().split('\n')

    for line in data:

        (
            part_number,
            mfg,
            family,
            series,
            pins,
            color,
            min_temp,
            max_temp,
            length,
            width,
            height,
            terminal_size,
            image_path,
            cad_path
        ) = read_csv(line)

        part_number = str(part_number)
        length = float(length)
        width = float(width)
        height = float(height)
        family = str(family)
        series = str(series)
        color = str(color)
        image_path = str(image_path)
        cad_path = str(cad_path)
        pins = str(pins)
        terminal_size = float(terminal_size)

        mfg_id = get_mfg_id(con, cur, mfg)
        min_temp_id = get_temperature_id(con, cur, int(min_temp))
        max_temp_id = get_temperature_id(con, cur, int(max_temp))
        image_id = get_image_id(con, cur, image_path)
        cad_id = get_cad_id(con, cur, cad_path)
        series_id = get_series_id(con, cur, series, mfg_id)
        family_id = get_family_id(con, cur, family, mfg_id)
        color_id = get_color_id(con, cur, color)

        cur.execute('INSERT INTO tpa_locks (part_number, mfg_id, family_id, series_id, image_id, ' 
                    'cad_id, min_temp_id, max_temp_id, pins, color_id, length, width, height, terminal_size) ' 
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, family_id, series_id, image_id, cad_id, min_temp_id,
                     max_temp_id, pins, color_id, length, width, height, terminal_size))
        con.commit()


def load_cpa_locks(con, cur):
    with open(r'C:\Users\drsch\Desktop\HarnessMaker\cpa_locks.csv', 'r') as f:
        data = f.read().split('\n')

    for line in data:

        (
            part_number,
            mfg,
            family,
            series,
            pins,
            color,
            min_temp,
            max_temp,
            length,
            width,
            height,
            terminal_size,
            image_path,
            cad_path
        ) = read_csv(line)

        part_number = str(part_number)
        length = float(length)
        width = float(width)
        height = float(height)
        family = str(family)
        series = str(series)
        color = str(color)
        image_path = str(image_path)
        cad_path = str(cad_path)
        pins = str(pins)
        terminal_size = float(terminal_size)

        mfg_id = get_mfg_id(con, cur, mfg)
        min_temp_id = get_temperature_id(con, cur, int(min_temp))
        max_temp_id = get_temperature_id(con, cur, int(max_temp))
        image_id = get_image_id(con, cur, image_path)
        cad_id = get_cad_id(con, cur, cad_path)
        series_id = get_series_id(con, cur, series, mfg_id)
        family_id = get_family_id(con, cur, family, mfg_id)
        color_id = get_color_id(con, cur, color)

        cur.execute('INSERT INTO cpa_locks (part_number, mfg_id, family_id, series_id, image_id, ' 
                    'cad_id, min_temp_id, max_temp_id, pins, color_id, length, width, height, terminal_size) ' 
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, family_id, series_id, image_id, cad_id, min_temp_id,
                     max_temp_id, pins, color_id, length, width, height, terminal_size))
        con.commit()


def load_covers(con, cur):

    with open(r'C:\Users\drsch\Desktop\HarnessMaker\covers.csv', 'r') as f:
        data = f.read().split('\n')

    for line in data:
        (
            part_number, mfg, series, direction, length, width, height, min_temp,
            max_temp, pins, color, image_path, cad_path
        ) = read_csv(line)

        part_number = str(part_number)
        length = float(length)
        width = float(width)
        height = float(height)
        series = str(series)
        color = str(color)
        image_path = str(image_path)
        cad_path = str(cad_path)
        pins = str(pins)
        direction = str(direction)

        mfg_id = get_mfg_id(con, cur, mfg)
        min_temp_id = get_temperature_id(con, cur, int(min_temp))
        max_temp_id = get_temperature_id(con, cur, int(max_temp))
        image_id = get_image_id(con, cur, image_path)
        cad_id = get_cad_id(con, cur, cad_path)
        series_id = get_series_id(con, cur, series, mfg_id)
        color_id = get_color_id(con, cur, color)
        direction_id = get_direction_id(con, cur, direction)

        cur.execute('INSERT INTO covers (part_number, mfg_id, series_id, image_id, direction_id, ' 
                    'cad_id, min_temp_id, max_temp_id, pins, color_id, length, width, height) ' 
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, series_id, image_id, direction_id, cad_id, min_temp_id,
                     max_temp_id, pins, color_id, length, width, height))
        con.commit()


def load_seals(con, cur):

    with open(r'C:\Users\drsch\Desktop\HarnessMaker\seals.csv', 'r') as f:
        data = f.read().split('\n')

    for line in data:
        l_data = read_csv(line)
        try:
            (
                part_number, mfg, series, type_, hardness, color, lubricant, min_temp,
                max_temp, length, o_dia, i_dia, wire_dia_min, wire_dia_max, image_path, cad_path
            ) = l_data
        except:
            print(l_data)
            raise

        part_number = str(part_number)
        type_ = str(type_)
        length = float(length)
        o_dia = float(o_dia)
        i_dia = float(i_dia)
        series = str(series)
        color = str(color)
        image_path = str(image_path)
        cad_path = str(cad_path)
        hardness = int(hardness)
        lubricant = str(lubricant)
        wire_dia_min = float(wire_dia_min)
        wire_dia_max = float(wire_dia_max)

        mfg_id = get_mfg_id(con, cur, mfg)
        min_temp_id = get_temperature_id(con, cur, int(min_temp))
        max_temp_id = get_temperature_id(con, cur, int(max_temp))
        image_id = get_image_id(con, cur, image_path)
        cad_id = get_cad_id(con, cur, cad_path)
        series_id = get_series_id(con, cur, series, mfg_id)
        color_id = get_color_id(con, cur, color)

        cur.execute('INSERT INTO seals (part_number, mfg_id, series_id, type, hardness, color_id, '
                    'lubricant, min_temp_id, max_temp_id, length, o_dia, i_dia, wire_dia_min, '
                    'wire_dia_max, image_id, cad_id) ' 
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, series_id, type_, hardness, color_id, lubricant,
                     min_temp_id, max_temp_id, length, o_dia, i_dia, wire_dia_min, wire_dia_max,
                     image_id, cad_id))
        con.commit()


def load_terminals(con, cur):

    with open(r'C:\Users\drsch\Desktop\HarnessMaker\terminals.csv', 'r') as f:
        data = f.read().split('\n')

    for line in data:
        l_data = read_csv(line)
        try:
            (
                part_number, mfg, family, series, min_wire_cross, max_wire_cross,
                gender, _, material, sealed, _, _, wire_dia_min, wire_dia_max, _,
                lock_type,  blade_size, _, _, _, _, _, _, image_path, cad_path
            ) = l_data
        except:
            print(l_data)
            raise

        part_number = str(part_number)
        lock_type = str(lock_type)

        if not wire_dia_min:
            wire_dia_min = '0.0'

        if not wire_dia_max:
            wire_dia_max = '0.0'

        if not min_wire_cross:
            min_wire_cross = '0.0'

        if not max_wire_cross:
            max_wire_cross = '0.0'

        if not blade_size:
            blade_size = '0.0'

        wire_dia_min = float(wire_dia_min)
        wire_dia_max = float(wire_dia_max)
        min_wire_cross = float(min_wire_cross)
        max_wire_cross = float(max_wire_cross)
        series = str(series)
        gender = str(gender)
        image_path = str(image_path)
        cad_path = str(cad_path)
        blade_size = float(blade_size)
        sealed = str(sealed)
        if sealed == 'yes':
            sealing = 1
        else:
            sealing = 0

        material = str(material)
        material_id = get_material_id(con, cur, material.title())
        mfg_id = get_mfg_id(con, cur, mfg)
        image_id = get_image_id(con, cur, image_path)
        cad_id = get_cad_id(con, cur, cad_path)
        series_id = get_series_id(con, cur, series, mfg_id)
        family_id = get_family_id(con, cur, family, mfg_id)
        cavity_lock_id = get_cavity_lock_id(con, cur, lock_type.title())
        gender_id = get_gender_id(con, cur, gender.title())

        cur.execute('INSERT INTO terminals (part_number, mfg_id, gender_id, series_id, '
                    'family_id, sealing, cavity_lock_id, image_id, cad_id, material_id, '
                    'blade_size, wire_dia_min, wire_dia_max, min_wire_cross, max_wire_cross) ' 
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, gender_id, series_id, family_id, sealing, cavity_lock_id,
                     image_id, cad_id, material_id, blade_size, wire_dia_min, wire_dia_max, min_wire_cross,
                     max_wire_cross))
        con.commit()


def load_housings(con, cur):
    with open(r'C:\Users\drsch\Desktop\HarnessMaker\housings.csv', 'r') as f:
        data = f.read().split('\n')

    for line in data:
        l_data = read_csv(line)
        try:
            (
                part_number, mfg, family, series, num_pins, rows, centerline,
                gender, cable_exit,
                color, sealing, min_temp, max_temp, length, width, height,
                terminal_lock, terminal_sizes,
                compat_terminals, compat_seals, compat_covers, compat_cpas,
                compat_tpas, mates_to, image_path, cad_path
            ) = l_data
        except:
            print(l_data)
            raise

        part_number = str(part_number)
        mfg_id = get_mfg_id(con, cur, str(mfg))
        family_id = get_family_id(con, cur, str(family), mfg_id)
        series_id = get_series_id(con, cur, str(series), mfg_id)

        if not num_pins:
            num_pins = '0'

        num_pins = int(num_pins)

        if not rows:
            rows = '0'

        rows = int(rows)

        if not centerline:
            centerline = '0.0'

        centerline = float(centerline)

        gender_id = get_gender_id(con, cur, str(gender).title())

        if cable_exit == 180:
            cable_exit = 'Straight'
        elif cable_exit == 270:
            cable_exit = 'Left'
        elif cable_exit == 90:
            cable_exit = 'Right'
        else:
            cable_exit = 'Straight'

        wire_orientation_id = get_direction_id(con, cur, cable_exit)

        color_id = get_color_id(con, cur, str(color).title())

        if color_id is None:
            color_id = 0

        sealing = str(sealing).lower()
        if sealing == 'sealed':
            sealed = 1
        else:
            sealed = 0

        if not min_temp:
            min_temp = 0

        if not max_temp:
            max_temp = 0

        min_temp_id = get_temperature_id(con, cur, int(min_temp))
        max_temp_id = get_temperature_id(con, cur, int(max_temp))

        if not length:
            length = '0.0'

        length = float(length)

        if not width:
            width = '0.0'

        width = float(width)

        if not height:
            height = '0.0'

        height = float(height)

        cavity_lock_id = get_cavity_lock_id(con, cur, str(terminal_lock).title())

        if isinstance(terminal_sizes, (int, float)):
            terminal_sizes = str(float(terminal_sizes))

        terminal_sizes = [item.strip() for item in str(terminal_sizes).split(',')]
        terminal_sizes = ', '.join(terminal_sizes)
        terminal_sizes = f'[{terminal_sizes}]'

        if not mates_to:
            mates_to = '[]'

        if not compat_terminals:
            compat_terminals = '[]'

        if not compat_seals:
            compat_seals = '[]'

        if not compat_covers:
            compat_covers = '[]'

        if not compat_cpas:
            compat_cpas = '[]'

        if not compat_tpas:
            compat_tpas = '[]'

        cad_id = get_cad_id(con, cur, cad_path)

        image_id = get_image_id(con, cur, image_path)

        cur.execute('INSERT INTO housings (part_number, mfg_id, family_id, series_id, num_pins, rows, centerline, gender_id, ' 
                    'wire_orientation_id, color_id, sealed, min_temp_id, max_temp_id, length, width, '
                    'height, cavity_lock_id, terminal_sizes, mates_to, compat_terminals, compat_seals, ' 
                    'compat_covers, compat_cpas, compat_tpas, image_id, cad_id) ' 
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (part_number, mfg_id, family_id, series_id, num_pins, rows, centerline, gender_id,
                     wire_orientation_id, color_id, sealed, min_temp_id, max_temp_id, length, width,
                     height, cavity_lock_id, terminal_sizes, mates_to, compat_terminals, compat_seals,
                     compat_covers, compat_cpas, compat_tpas, image_id, cad_id))
        con.commit()


import cv2

from PIL import Image


def set_image_data(con, cur, data):
    if not data:
        return 1

    cur.execute(f'INSERT INTO images (path, data) VALUES (?, ?);', ('PRELOADED', data))
    con.commit()
    return cur.lastrowid


def get_cavities(filename):
    res = []

    # read the image of rectangle as grayscale
    img = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)

    # threshold
    thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

    # compute largest contour
    contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = contours[0] if len(contours) == 2 else contours[1]
    for c in contours:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.001 * peri, True)
        if len(approx) == 4:
            x, y, w, h = cv2.boundingRect(approx)
            res.insert(0, (x, y, w, h))

    return res


def load_cavity_maps(con, cur):
    path = r'C:\Users\drsch\Desktop\HarnessMaker\harness_maker_2\images'

    cur.execute('SELECT id, part_number, terminal_sizes, num_pins, rows FROM housings;')
    for id_, part_number, terminal_sizes, num_pins, rows in cur.fetchall():
        if id_ == 1:
            continue

        if not num_pins or not rows:
            continue

        print(part_number)

        terminal_sizes = sorted(eval(terminal_sizes))
        terminal_sizes = [terminal_sizes[~i + len(terminal_sizes)] for i in range(len(terminal_sizes))]

        image_path = os.path.join(path, part_number + '.png')
        overlay_path = os.path.join(path, part_number + '_pin_mask.png')

        if os.path.exists(overlay_path):
            overlay_data = open(overlay_path, 'rb').read()
            overlay_id = set_image_data(con, cur, overlay_data)

            sizes = set()

            cavity_masks = {}

            count = 0

            for i, (x, y, width, height) in enumerate(get_cavities(overlay_path)):
                sizes.add((width, height))
                cavity_masks[i] = [x, y, width, height]
                count += 1

            sizes = sorted(list(sizes))
            sizes = [sizes[~i + len(sizes)] for i in range(len(sizes))]

            size_map = {}
            for i, size in enumerate(sizes):
                if i >= len(terminal_sizes):
                    size_map[size] = terminal_sizes[-1]
                else:
                    size_map[size] = terminal_sizes[i]

            img = Image.open(overlay_path)

            cavity_data = []

            for i, (x, y, w, h) in list(cavity_masks.items()):
                terminal_size = size_map[(w, h)]

                center_x = int(w / 2) + x
                center_y = int(h / 2) + y

                r, g, b, _ = img.getpixel((center_x, center_y))
                rgb = r << 16 | g << 8 | b
                cavity_data.append([i, str(i + 1), terminal_size, x, y, w, h, rgb])

            img.close()

        else:
            overlay_id = 1

            count = num_pins
            pins_per_row = int(count / rows)

            pin_width = int(380 / pins_per_row)
            pin_width = min(pin_width, 50)

            total_pin_width = pin_width * pins_per_row

            start_x = int((400 - total_pin_width) / 2)
            x = start_x

            pin_height = int(230 / rows)
            pin_height = min(pin_height, 30)

            total_pin_height = pin_height * rows
            y = int((250 - total_pin_height) / 2)

            cavity_data = []
            pc = 0

            for i in range(num_pins):
                pc += 1
                if pc > pins_per_row:
                    pc = 0
                    y += pin_height
                    x = start_x

                cavity_data.append([i, str(i + 1), 0.0, x + 5, y + 5, pin_width - 10, pin_height - 10, 0x00FF00])
                x += pin_width

        if os.path.exists(image_path):
            image_data = open(image_path, 'rb').read()
        else:
            img = Image.new('RGBA', (400, 250), (255, 246, 244, 0))
            img.save('temp_image.png')
            img.close()
            image_data = open('temp_image.png', 'rb').read()

        image_id = set_image_data(con, cur, image_data)

        cur.execute('INSERT INTO cavity_maps (housing_id, overlay_id, image_id, count) '
                    'VALUES (?, ?, ?, ?);',
                    (id_, overlay_id, image_id, count))
        con.commit()
        cavity_map_id = cur.lastrowid

        for idx, name, size, x, y, width, height, rgb in cavity_data:
            cur.execute('INSERT INTO cavities (cavity_map_id, idx, name, size, '
                        'x, y, width, height, rgb) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);',
                        (cavity_map_id, idx, name, size, x, y, width, height, rgb))
            con.commit()


def load_transitions(con, cur):

    path = r'C:\Users\drsch\Desktop\HarnessMaker\harness_maker_2\images\transitions'
    cur.execute('SELECT id, name FROM transition_series;')
    for series_id, series_name in cur.fetchall():
        if series_id == 0:
            continue

        image_path = os.path.join(path, series_name + '.png')
        overlay_path = os.path.join(path, series_name + '_mask.png')

        overlay_data = open(overlay_path, 'rb').read()
        overlay_id = set_image_data(con, cur, overlay_data)

        cavity_data = []

        count = 0

        img = Image.open(overlay_path)

        for i, (x, y, w, h) in enumerate(get_cavities(overlay_path)):
            center_x = int(w / 2) + x
            center_y = int(h / 2) + y

            r, g, b, _ = img.getpixel((center_x, center_y))
            rgb = r << 16 | g << 8 | b
            cavity_data.append([i, str(i + 1), x, y, w, h, rgb])
            count += 1

        img.close()

        image_data = open(image_path, 'rb').read()
        image_id = set_image_data(con, cur, image_data)

        cur.execute('INSERT INTO transition_maps (tran_series_id, overlay_id, image_id, num_branches) '
                    'VALUES (?, ?, ?, ?);',
                    (series_id, overlay_id, image_id, count))

        con.commit()
        tran_map_id = cur.lastrowid

        for idx, name, x, y, width, height, rgb in cavity_data:
            cur.execute('INSERT INTO  transition_branches (tran_map_id, idx, name, '
                        'x, y, w, h, rgb) '
                        'VALUES (?, ?, ?, ?, ?, ?, ?, ?);',
                        (tran_map_id, idx, name, x, y, width, height, rgb))
            con.commit()



def load_shrink_tube(con, cur):
    cur.executemany('INSERT INTO bundle_cover_series (id, name, mfg_id) VALUES (?, ?, ?);',
                    ((0, 'Not Applicable', 1), (1, 'DR-25', 2)))
    con.commit()

    cur.executemany('INSERT INTO bundle_cover_resistances (name, value) VALUES (?, ?);',
                    (('Abrasion', 0x0001), ('Fluids', 0x0002), ('Mechanical Damage', 0x0004),
                    ('Strain Relief', 0x0008), ('Aviation Fuel', 0x0010), ('Brake Fluid', 0x0020),
                    ('Diesel Fuel', 0x0040), ('Hydraulic Fluid', 0x0080), ('Lubricating Oil', 0x0100),
                    ('Water', 0x0200)))
    con.commit()

    cur.executemany('INSERT INTO bundle_cover_materials (id, name) VALUES (?, ?);',
                    ((0, 'Unknown',), (1, 'Crosslinked Elastomer',)))
    con.commit()

    cur.executemany('INSERT INTO bundle_cover_rigidities (id, name) VALUES (?, ?);',
                    ((0, 'Unknown'), (1, 'Flexible',), (2, 'Very Flexible',)))
    con.commit()

    cur.execute('INSERT INTO images (path) '
                'VALUES ("https://www.te.com/catalog/common/images/PartImages/prdr-25.jpg?w=300");')
    con.commit()
    image_id = cur.lastrowid

    cur.execute('INSERT INTO cads (path) '
                'VALUES ("https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=DR-25&DocType=Customer%20Drawing&DocLang=English&DocFormat=pdf&PartCntxt=5039244037");')
    con.commit()
    cad_id = cur.lastrowid

    cur.execute('INSERT INTO cads (path) '
                'VALUES ("https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=DR-25-TW&DocType=Customer%20Drawing&DocLang=English&DocFormat=pdf&PartCntxt=8895704002");')
    con.commit()
    cad_id_tw = cur.lastrowid

    cur.executemany('INSERT INTO bundle_covers (part_number, mfg_id, description, series_id, '
                    'image_id, cad_id, min_temp_id, max_temp_id, color_id, min_size, max_size, wall, '
                    'shrink_ratio, resistance_values, material_id, rigidity_id, shrink_temp_id) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                    (('DR-25-1-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 12.8, 25.4, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-3/4-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 9.5, 19.0, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-3/8-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 4.8, 9.53, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-1/2-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 6.4, 12.7, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-2-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 25.4, 51.0, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-4-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 50.8, 101.6, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-3-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 38.0, 76.0, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-1/8-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 1.6, 3.2, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-3/16-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 2.4, 4.8, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-1/4-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 3.2, 6.4, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-1-1/2-0-SP', 2, '', 1, image_id, cad_id, 6, 51, 0, 19.0, 38.1, 'Single', '2:1', 0x03FF, 1, 1, 56),
                     ('DR-25-TW-1/2-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 6.4, 12.7, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-3/8-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 4.8, 9.5, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-3/16-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 2.4, 4.8, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-1-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 12.8, 25.4, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-1/4-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 3.2, 6.4, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-3/4-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 9.5, 19.0, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-1/8-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 1.6, 3.2, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-3/32-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 1.2, 2.4, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-1-1/4-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 15.0, 31.5, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56),
                     ('DR-25-TW-1-1/2-0-SP', 2, '', 1, image_id, cad_id_tw, 6, 51, 0, 19.1, 38.0, 'Single (thin wall)', '2:1', 0x03FF, 1, 2, 56)))
    con.commit()


import sqlite3


if __name__ == '__main__':
    con_ = sqlite3.connect('test.db')
    cur_ = con_.cursor()
    create_tables(con_, cur_)
    preload_database(con_, cur_)

    load_tpa_locks(con_, cur_)
    load_cpa_locks(con_, cur_)
    load_covers(con_, cur_)
    load_seals(con_, cur_)
    load_terminals(con_, cur_)
    load_housings(con_, cur_)
    load_cavity_maps(con_, cur_)
    load_transitions(con_, cur_)
    load_shrink_tube(con_, cur_)

    cur_.close()
    con_.close()


for feature in data['features']:
    if feature['code'] == '911841':
        for value in feature['values']:
            if value == '25':

'905343' - branch count

'904325' - shape, y, etc...


'901781' temperature range


'''
{
        "part_number": "416486-000",
        "images": [
            "https://www.te.com/catalog/common/images/PartImages/pr3j4-79tran.jpg"
        ],
        "datasheets": [
            [
                "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=1-1773853-4_moldedparts&DocType=Data%20Sheet&DocLang=English&DocFormat=pdf&PartCntxt=416486-000",
                "pdf"
            ],
            [
                "https://www.te.com/commerce/DocumentDelivery/DDEController?Action=srchrtrv&DocNm=2392785-1_vg-products&DocType=Data%20Sheet&DocLang=English&DocFormat=pdf&PartCntxt=416486-000",
                "pdf"
            ]
        ],
        "cads": [],
        "models3d": [],
        "models2d": [],
        "features": [
            {
                "code": "911841",
                "label": "Material Systems Code",
                "values": [
                    "25"
                ],
                "uom": null
            },
            {
                "code": "904325",
                "label": "Molded Part Shape",
                "values": [
                    "Y Shape"
                ],
                "uom": null
            },
            {
                "code": "905343",
                "label": "Number of Branches & Legs",
                "values": [
                    "3"
                ],
                "uom": null
            },
            {
                "code": "905410",
                "label": "Material Code",
                "values": [
                    "25"
                ],
                "uom": null
            },
            {
                "code": "901781",
                "label": "Operating Temperature Range",
                "values": [
                    "-75 \u2013 150"
                ],
                "uom": "\u00b0C"
            },
            {
                "code": "911839",
                "label": "Adhesive Requirement",
                "values": [
                    "Adhesive Precoat"
                ],
                "uom": null
            },
            
            904428   Resistance Protection
            905381   Adhesive Code
            911839  Adhesive Requirement
            
            {
                "code": "904428",
                "label": "Resistance Protection",
                "values": [
                    "Long-Term Fluid Exposure at High Temperatures"
                ],
                "uom": null
            },
            {
                "code": "905381",
                "label": "Adhesive Code",
                "values": [
                    "225"
                ],
                "uom": null
            }
        ],
        "feature_groups": [
        
        904325   Shape
        905343  Branches
        911839  Adhesive Requirement
        
        911841  series
        
        
            {
                "code": "904325",
                "label": "Molded Part Shape",
                "values": [
                    "Y Shape"
                ],
                "uom": null
            },
            {
                "code": "905343",
                "label": "Number of Branches & Legs",
                "values": [
                    "3"
                ],
                "uom": null
            },
            {
                "code": "911839",
                "label": "Adhesive Requirement",
                "values": [
                    "Adhesive Precoat"
                ],
                "uom": null
            },
            {
                "code": "911841",
                "label": "Material Systems Code",
                "values": [
                    "25"
                ],
                "uom": null
            },
            
            908582  material
            
            {
                "code": "908582",
                "label": "Primary Product Material",
                "values": [
                    "Fluid Resistant Modified Elastomer"
                ],
                "uom": null
            },
            {
                "code": "905410",
                "label": "Material Code",
                "values": [
                    "25"
                ],
                "uom": null
            },
            
            904711 branch 1 diameter range
            904713 branch 2 diameter range
            904715 branch 3 diameter range
            904717 branch 4 diameter range
            904719 branch 5 diameter range
            
            
            {
                "code": "904711",
                "label": "Inside Diameter Range (Body)",
                "values": [
                    "12.7 \u2013 26.9"
                ],
                "uom": "mm"
            },
            {
                "code": "904713",
                "label": "Inside Diameter Range (Leg 1)",
                "values": [
                    "12.7 \u2013 26.9"
                ],
                "uom": "mm"
            },
            {
                "code": "904715",
                "label": "Inside Diameter Range (Leg 2)",
                "values": [
                    "3.6 \u2013 6.6"
                ],
                "uom": "mm"
            },
            {
                "code": "911840",
                "label": "Flammability Performance",
                "values": [
                    "Flame-Retardant",
                    "Low Fire Hazard"
                ],
                "uom": null
            },
            
            901781   temp range
            
            
            
            {
                "code": "901781",
                "label": "Operating Temperature Range",
                "values": [
                    "-75 \u2013 150"
                ],
                "uom": "\u00b0C"
            },
            {
                "code": "904428",
                "label": "Resistance Protection",
                "values": [
                    "Long-Term Fluid Exposure at High Temperatures"
                ],
                "uom": null
            },
            
            904428  Resistance Protection
            
            904911  mechanical resistance
            {
                "code": "904911",
                "label": "Mechanical Resistance",
                "values": [
                    "Fluids",
                    "Mechanical Damage"
                ],
                "uom": null
            },
            {
                "code": "908180",
                "label": "Size Code",
                "values": [
                    "024"
                ],
                "uom": null
            },
            
            
            908179  series
            
            
            {
                "code": "908179",
                "label": "Molded Part Shape Code",
                "values": [
                    "342A"
                ],
                "uom": null
            },
            {
                "code": "905381",
                "label": "Adhesive Code",
                "values": [
                    "225"
                ],
                "uom": null
            }
        ],
        "description1": "Y Shape Cable Transistion, 3 Branches , 25 Material Code, 25 Material Systems Code, -75 \u2013 150 \u00b0C [-103 \u2013 302 \u00b0F], 225 Adhesive Code",
        "description2": "342A024-25/225-0",
        "compat_parts": [
            {
                "part_number": "9-120035-5",
                "features": []
            },
            {
                "part_number": "9-120035-6",
                "features": []
            }
        ]
    },


'''