
def resources(con, cur):
    cur.execute('CREATE TABLE resources('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'path TEXT DEFAULT "" NOT NULL, '
                'type TEXT DEFAULT "UNKNOWN", '
                'data BLOB DEFAULT NULL'
                ');')
    con.commit()


def manufacturers(con, cur):
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


def temperatures(con, cur):
    cur.execute('CREATE TABLE temperatures('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()


def genders(con, cur):
    cur.execute('CREATE TABLE genders('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()


def protections(con, cur):
    cur.execute('CREATE TABLE protections('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL'
                ');')
    con.commit()


def adhesives(con, cur):
    cur.execute('CREATE TABLE adhesives('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'code TEXT DEFAULT "" NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'accessory_part_nums TEXT DEFAULT "[]" NOT NULL'
                ');')
    con.commit()


def cavity_locks(con, cur):
    cur.execute('CREATE TABLE cavity_locks('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL'
                ');')
    con.commit()


def colors(con, cur):
    cur.execute('CREATE TABLE colors('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'rgb INTEGER NOT NULL'
                ');')
    con.commit()


def directions(con, cur):
    cur.execute('CREATE TABLE directions('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()


def ip_fluids(con, cur):
    cur.execute('CREATE TABLE ip_fluids('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'short_desc TEXT NOT NULL, '
                'description TEXT NOT NULL, '
                'icon_data BLOB DEFAULT NULL'                        
                ');')
    con.commit()


def ip_solids(con, cur):
    cur.execute('CREATE TABLE ip_solids('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'short_desc TEXT NOT NULL, '
                'description TEXT NOT NULL, '
                'icon_data BLOB DEFAULT NULL'
                ');')
    con.commit()


def ip_supps(con, cur):
    cur.execute('CREATE TABLE ip_supps('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'description TEXT NOT NULL'
                ');')
    con.commit()


def platings(con, cur):
    cur.execute('CREATE TABLE platings('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'symbol TEXT UNIQUE NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL'
                ');')
    con.commit()


def materials(con, cur):
    cur.execute('CREATE TABLE materials('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL'
                ');')
    con.commit()


def shapes(con, cur):
    cur.execute('CREATE TABLE shapes('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT UNIQUE NOT NULL'
                ');')
    con.commit()


def series(con, cur):
    cur.execute('CREATE TABLE series('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'mfg_id INTEGER DEFAULT 1 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def families(con, cur):
    cur.execute('CREATE TABLE families('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def ip_ratings(con, cur):
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
    con.commit()


def accessories(con, cur):
    cur.execute('CREATE TABLE accesories('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT NULL, '
                'material_id INTEGER DEFAULT 0 NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def transitions(con, cur):
    cur.execute('CREATE TABLE transitions('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '
                'material_id INTEGER DEFAULT 0 NOT NULL, '
                'branch_count INTEGER DEFAULT 0 NOT NULL, '
                'shape_id INTEGER DEFAULT 0 NOT NULL, '
                'protection_ids TEXT DEFAULT "[]" NOT NULL, '
                'adhesive_ids TEXT DEFAULT "[]" NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES transition_series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, ' 
                'FOREIGN KEY (shape_id) REFERENCES shapes(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def transition_branches(con, cur):
    cur.execute('CREATE TABLE transition_branches('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'transition_id INTEGER NOT NULL, '
                'idx INTEGER NOT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'bulb_offset TEXT DEFAULT NULL, '
                'bulb_length REAL DEFUALT NULL, '
                'min_dia REAL NOT NULL, '
                'max_dia REAL NOT NULL, '
                'length REAL NOT NULL, '
                'offset TEXT DEFAULT NULL, '
                'angle REAL DEFAULT NULL, '
                'flange_height REAL DEFAULT NULL, '
                'flange_width REAL DEFAULT NULL, '
                'FOREIGN KEY (transition_id) REFERENCES transitions(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()


def boots(con, cur):
    cur.execute('CREATE TABLE boots('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def bundle_covers(con, cur):
    cur.execute('CREATE TABLE bundle_covers('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'material_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '
                'rigidity TEXT DEFAULT "NOT SET" NOT NULL, '
                'shrink_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'min_dia INTEGER DEFAULT 0 NOT NULL, '
                'max_dia INTEGER DEFAULT 0 NOT NULL, '
                'wall TEXT DEFAULT "Single" NOT NULL, '
                'shrink_ratio TEXT DEFAULT "" NOT NULL, '
                'protection_ids TEXT DEFAULT "[]" NOT NULL, '
                'adhesive_ids TEXT DEFAULT "[]" NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (shrink_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def covers(con, cur):
    cur.execute('CREATE TABLE covers('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '                
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'direction_id INTEGER DEFAULT 0 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'pins TEXT DEFAULT "" NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (direction_id) REFERENCES directions(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def cpa_locks(con, cur):
    cur.execute('CREATE TABLE cpa_locks('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'pins TEXT DEFAULT "" NOT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'terminal_size REAL DEFAULT "0.0" NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def tpa_locks(con, cur):
    cur.execute('CREATE TABLE tpa_locks('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'pins TEXT DEFAULT "" NOT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'terminal_size REAL DEFAULT "0.0" NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def seals(con, cur):
    cur.execute('CREATE TABLE seals('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT NULL, '
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '     
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'type TEXT DEFAULT "" NOT NULL, '
                'hardness INTEGER DEFAULT -1 NOT NULL, '
                'lubricant TEXT DEFAULT "" NOT NULL, '
                'length REAL DEFAULT "0.0" NOT NULL, '
                'o_dia REAL DEFAULT "0.0" NOT NULL, '
                'i_dia REAL DEFAULT "0.0" NOT NULL, '
                'wire_dia_min REAL DEFAULT "0.0" NOT NULL, '
                'wire_dia_max REAL DEFAULT "0.0" NOT NULL, '   
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '    
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'                
                ');')
    con.commit()


def wires(con, cur):
    cur.execute('CREATE TABLE wires('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'addl_color_ids TEXT DEFAULT "[]" NOT NULL, '
                'material_id INTEGER DEFAULT 0 NOT NULL, '
                'num_conductors INTEGER DEFAULT 1 NOT NULL, '
                'shielded INTEGER DEFAULT 0 NOT NULL, '
                'tpi INTEGER DEFAULT 0 NOT NULL, '
                'conductor_dia_mm REAL DEFAULT "0.0" NOT NULL, '
                'size_mm2 REAL DEFAULT "0.0" NOT NULL, '
                'size_awg INTEGER DEFAULT 0 NOT NULL, '
                'od_mm REAL DEFAULT "0.0" NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (color_id) REFERENCES colors(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (material_id) REFERENCES materials(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def terminals(con, cur):
    cur.execute('CREATE TABLE terminals('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'plating_id INTEGER DEFAULT 0 NOT NULL, '
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'gender_id INTEGER DEFAULT 0 NOT NULL, '
                'sealing INTEGER DEFAULT 0 NOT NULL, '
                'cavity_lock_id INTEGER DEFAULT 0 NOT NULL, '                
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
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (gender_id) REFERENCES genders(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cavity_lock_id) REFERENCES cavity_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '   
                'FOREIGN KEY (plating_id) REFERENCES platings(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'                               
                ');')
    con.commit()


def housings(con, cur):
    cur.execute('CREATE TABLE housings('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number TEXT UNIQUE NOT NULL, '
                'mfg_id INTEGER DEFAULT 0 NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'family_id INTEGER DEFAULT 0 NOT NULL, '
                'series_id INTEGER DEFAULT 0 NOT NULL, '
                'color_id INTEGER DEFAULT 0 NOT NULL, '                    
                'min_temp_id INTEGER DEFAULT 0 NOT NULL, '
                'max_temp_id INTEGER DEFAULT 0 NOT NULL, '    
                'image_id INTEGER DEFAULT 0 NOT NULL, '
                'datasheet_id INTEGER DEFAULT 0 NOT NULL, '
                'cad_id INTEGER DEFAULT 0 NOT NULL, '
                'gender_id INTEGER DEFAULT 0 NOT NULL, '
                'direction_id INTEGER DEFAULT 0 NOT NULL, '    
                'length REAL DEFAULT "0.0" NOT NULL, '
                'width REAL DEFAULT "0.0" NOT NULL, '
                'height REAL DEFAULT "0.0" NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'cavity_lock_id INTEGER DEFAULT 0 NOT NULL, '
                'sealing INTEGER DEFAULT 0 NOT NULL, '
                'rows INTEGER DEFAULT 0 NOT NULL, '    
                'num_pins INTEGER DEFAULT 0 NOT NULL, '
                'terminal_sizes TEXT DEFAULT "[]" NOT NULL, '
                'centerline REAL DEFAULT "0.0" NOT NULL, '
                'compat_cpas TEXT DEFAULT "[]" NOT NULL, '    
                'compat_tpas TEXT DEFAULT "[]" NOT NULL, '    
                'compat_covers TEXT DEFAULT "[]" NOT NULL, '    
                'compat_terminals TEXT DEFAULT "[]" NOT NULL, '    
                'compat_seals TEXT DEFAULT "[]" NOT NULL, '
                'compat_housings TEXT DEFAULT "[]" NOT NULL, '
                'ip_rating_id INTEGER DEFAULT 0 NOT NULL, '                
                'cavitymap_id INTEGER DEFAULT 0 NOT NULL, '               
                'cavitymap_overlay_id INTEGER DEFAULT 0 NOT NULL, '
                'footprint_id INTEGER DEFAULT 0 NOT NULL, '
                'model_2d_id INTEGER DEFAULT 0 NOT NULL, '
                'model_3d_id INTEGER DEFAULT 0 NOT NULL, '
                'weight REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (mfg_id) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (family_id) REFERENCES families(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (series_id) REFERENCES series(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (gender_id) REFERENCES genders(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (ip_rating_id) REFERENCES ip_ratings(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (image_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (datasheet_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cad_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (min_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (max_temp_id) REFERENCES temperatures(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (cavity_lock_id) REFERENCES terminal_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '                
                'FOREIGN KEY (direction_id) REFERENCES directions(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, ' 
                'FOREIGN KEY (cavitymap_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cavitymap_overlay_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, ' 
                'FOREIGN KEY (model_2d_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (model_3d_id) REFERENCES resources(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '  
                ');')
    con.commit()


def cavities(con, cur):
    cur.execute('CREATE TABLE cavities('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'housing_id INTEGER NOT NULL, '
                'idx INTEGER NOT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'size REAL DEFAULT "0.0" NOT NULL, '
                'point_2d TEXT DEFAULT "[0.0, 0.0]" NOT NULL, '
                'point_3d TEXT DEFAULT "[0.0, 0.0, 0.0]" NOT NULL, '
                'rotation_3d TEXT DEFAULT "[0.0, 0.0, 0.0]" NOT NULL, ' 
                'FOREIGN KEY (housing_id) REFERENCES housings(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()


def housing_crossref(con, cur):
    cur.execute('CREATE TABLE housing_crossref('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number1 TEXT NOT NULL, '
                'housing_id1 INTEGER DEFAULT NULL, '
                'mfg_id1 INTEGER DEFAULT NULL, '
                'part_number2 TEXT NOT NULL, '
                'housing_id2 INTEGER DEFAULT NULL, '
                'mfg_id2 INTEGER DEFAULT NULL, '
                'FOREIGN KEY (housing_id1) REFERENCES housings(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id1) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (housing_id2) REFERENCES housings(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id2) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def terminal_crossref(con, cur):
    cur.execute('CREATE TABLE terminal_crossref('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number1 TEXT NOT NULL, '
                'terminal_id1 INTEGER DEFAULT NULL, '
                'mfg_id1 INTEGER DEFAULT NULL, '
                'part_number2 TEXT NOT NULL, '
                'terminal_id2 INTEGER DEFAULT NULL, '
                'mfg_id2 INTEGER DEFAULT NULL, '
                'FOREIGN KEY (terminal_id1) REFERENCES terminals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id1) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (terminal_id2) REFERENCES terminals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id2) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def seal_crossref(con, cur):
    cur.execute('CREATE TABLE seal_crossref('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number1 TEXT NOT NULL, '
                'seal_id1 INTEGER DEFAULT NULL, '
                'mfg_id1 INTEGER DEFAULT NULL, '
                'part_number2 TEXT NOT NULL, '
                'seal_id2 INTEGER DEFAULT NULL, '
                'mfg_id2 INTEGER DEFAULT NULL, '
                'FOREIGN KEY (seal_id1) REFERENCES seals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id1) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (seal_id2) REFERENCES seals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id2) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def cover_crossref(con, cur):
    cur.execute('CREATE TABLE cover_crossref('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number1 TEXT NOT NULL, '
                'cover_id1 INTEGER DEFAULT NULL, '
                'mfg_id1 INTEGER DEFAULT NULL, '
                'part_number2 TEXT NOT NULL, '
                'cover_id2 INTEGER DEFAULT NULL, '
                'mfg_id2 INTEGER DEFAULT NULL, '
                'FOREIGN KEY (cover_id1) REFERENCES covers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id1) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cover_id2) REFERENCES covers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id2) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def boot_crossref(con, cur):
    cur.execute('CREATE TABLE boot_crossref('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number1 TEXT NOT NULL, '
                'boot_id1 INTEGER DEFAULT NULL, '
                'mfg_id1 INTEGER DEFAULT NULL, '
                'part_number2 TEXT NOT NULL, '
                'boot_id2 INTEGER DEFAULT NULL, '
                'mfg_id2 INTEGER DEFAULT NULL, '
                'FOREIGN KEY (boot_id1) REFERENCES booth(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id1) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (boot_id2) REFERENCES boots(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id2) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def tpa_lock_crossref(con, cur):
    cur.execute('CREATE TABLE tpa_lock_crossref('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number1 TEXT NOT NULL, '
                'tpa_lock_id1 INTEGER DEFAULT NULL, '
                'mfg_id1 INTEGER DEFAULT NULL, '
                'part_number2 TEXT NOT NULL, '
                'tpa_lock_id2 INTEGER DEFAULT NULL, '
                'mfg_id2 INTEGER DEFAULT NULL, '
                'FOREIGN KEY (tpa_lock_id1) REFERENCES tpa_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id1) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (tpa_lock_id2) REFERENCES tpa_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id2) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def cpa_lock_crossref(con, cur):
    cur.execute('CREATE TABLE cpa_lock_crossref('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'part_number1 TEXT NOT NULL, '
                'cpa_lock_id1 INTEGER DEFAULT NULL, '
                'mfg_id1 INTEGER DEFAULT NULL, '
                'part_number2 TEXT NOT NULL, '
                'cpa_lock_id2 INTEGER DEFAULT NULL, '
                'mfg_id2 INTEGER DEFAULT NULL, '
                'FOREIGN KEY (cpa_lock_id1) REFERENCES cpa_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id1) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cpa_lock_id2) REFERENCES cpa_locks(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (mfg_id2) REFERENCES manufacturers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


# ================ project tables ======================
def projects(con, cur):
    cur.execute('CREATE TABLE projects('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'name TEXT NOT NULL, '
                'obj_count INTEGER DEFAULT 0 NOT NULL'
                ');')
    con.commit()


def pjt_coordinates_3d(con, cur):
    cur.execute('CREATE TABLE pjt_coordinates_3d('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'x REAL DEFAULT "0.0" NOT NULL, '
                'y REAL DEFAULT "0.0" NOT NULL, '
                'z REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_coordinates_2d(con, cur):
    cur.execute('CREATE TABLE pjt_coordinates_2d('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'x REAL DEFAULT "0.0" NOT NULL, '
                'y REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_circuits(con, cur):
    cur.execute('CREATE TABLE pjt_circuits('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'circuit_num INTEGER NOT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'description TEXT DEFAULT "" NOT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_bundle_layouts(con, cur):
    cur.execute('CREATE TABLE pjt_bundle_layouts('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'coord_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_wire3d_layouts(con, cur):
    cur.execute('CREATE TABLE pjt_wire3d_layouts('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'coord_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_wire2d_layouts(con, cur):
    cur.execute('CREATE TABLE pjt_wire2d_layouts('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'coord_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (coord_id) REFERENCES pjt_coordinates_2d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_bundles(con, cur):
    cur.execute('CREATE TABLE pjt_bundles('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'part_id INTEGER DEFAULT NULL, '
                'start_coord_id INTEGER DEFAULT NULL, '
                'stop_coord_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (part_id) REFERENCES bundle_covers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (start_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (stop_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_splices(con, cur):
    cur.execute('CREATE TABLE pjt_splices('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'part_id INTEGER DEFAULT NULL, '
                'circuit_id INTEGER DEFAULT NULL, '
                'coord3d_id INTEGER DEFAULT NULL, '
                'coord2d_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (part_id) REFERENCES splices(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (coord3d_id) REFERENCES pjt_circuits(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (coord2d_id) REFERENCES pjt_coordinates_2d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_housings(con, cur):
    cur.execute('CREATE TABLE pjt_housings('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'part_id INTEGER DEFAULT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'coord3d_id INTEGER DEFAULT NULL, '
                'coord2d_id INTEGER DEFAULT NULL, '
                'x_angle_3d REAL DEFAULT "0.0" NOT NULL, '
                'y_angle_3d REAL DEFAULT "0.0" NOT NULL, '
                'z_angle_3d REAL DEFAULT "0.0" NOT NULL, '
                'angle_2d REAL DEFAULT "0.0" NOT NULL, '
                'seal_ids TEXT DEFAULT "[]" NOT NULL, '
                'cpa_lock_ids TEXT DEFAULT "[]" NOT NULL, '
                'tpa_lock_ids TEXT DEFAULT "[]" NOT NULL, '
                'cover_id INTEGER DEFAULT NULL, '
                'boot_id INTEGER DEFAULT NULL, '
                'accessory_ids TEXT DEFAULT "[]" NOT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (part_id) REFERENCES housings(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (coord3d_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (coord2d_id) REFERENCES pjt_coordinates_2d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cover_id) REFERENCES covers(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (boot_id) REFERENCES boots(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_cavities(con, cur):
    cur.execute('CREATE TABLE pjt_cavities('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'part_id INTEGER DEFAULT NULL, '
                'housing_id INTEGER NOT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'coord2d_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (part_id) REFERENCES cavities(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (housing_id) REFERENCES pjt_housings(id) ON DELETE CASCADE ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_terminals(con, cur):
    cur.execute('CREATE TABLE pjt_terminals('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'part_id INTEGER DEFAULT NULL, '
                'cavity_id INTEGER NOT NULL, '
                'seal_id INTEGER DEFAULT NULL, '
                'circuit_id INTEGER DEFAULT NULL, '
                'coord3d_id INTEGER DEFAULT NULL, '
                'coord2d_id INTEGER DEFAULT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (part_id) REFERENCES terminals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (cavity_id) REFERENCES pjt_cavities(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (seal_id) REFERENCES seals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (circuit_id) REFERENCES pjt_circuits(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (coord3d_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (coord2d_id) REFERENCES pjt_coordinates_2d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_transitions(con, cur):
    cur.execute('CREATE TABLE pjt_transitions('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'part_id INTEGER DEFAULT NULL, '
                'name TEXT DEFAULT "" NOT NULL, '
                'branch1_coord_id INTEGER DEFAULT NULL, '
                'branch2_coord_id INTEGER DEFAULT NULL, '
                'branch3_coord_id INTEGER DEFAULT NULL, '
                'branch4_coord_id INTEGER DEFAULT NULL, '
                'branch5_coord_id INTEGER DEFAULT NULL, '
                'branch6_coord_id INTEGER DEFAULT NULL, '
                'x_angle REAL DEFAULT "0.0" NOT NULL, '
                'y_angle REAL DEFAULT "0.0" NOT NULL, '
                'z_angle REAL DEFAULT "0.0" NOT NULL, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (part_id) REFERENCES terminals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (branch1_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (branch2_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (branch3_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (branch4_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (branch5_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (branch6_coord_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'
                ');')
    con.commit()


def pjt_wires(con, cur):
    cur.execute('CREATE TABLE pjt_wires('
                'id INTEGER PRIMARY KEY AUTOINCREMENT, '
                'project_id INTEGER NOT NULL, '
                'part_id INTEGER DEFAULT NULL, '
                'circuit_id INTEGER DEFAULT NULL, '
                'start_coord3d_id INTEGER DEFAULT NULL, '
                'stop_coord3d_id INTEGER DEFAULT NULL, '
                'start_coord2d_id INTEGER DEFAULT NULL, '
                'stop_coord2d_id INTEGER DEFAULT NULL, '
                'is_visible INTEGER DEFAULT 1, '
                'FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE, '
                'FOREIGN KEY (part_id) REFERENCES terminals(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (circuit_id) REFERENCES pjt_circuits(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (start_coord3d_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (stop_coord3d_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (start_coord2d_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE, '
                'FOREIGN KEY (stop_coord2d_id) REFERENCES pjt_coordinates_3d(id) ON DELETE SET DEFAULT ON UPDATE CASCADE'                ');')
    con.commit()


if __name__ == '__main__':
    import sqlite3
    con_ = sqlite3.connect('test.db')
    cur_ = con_.cursor()

    funcs = (
        resources,
        manufacturers,
        temperatures,
        genders,
        protections,
        adhesives,
        cavity_locks,
        colors,
        directions,
        ip_fluids,
        ip_solids,
        ip_supps,
        platings,
        materials,
        shapes,
        series,
        families,
        ip_ratings,
        accessories,
        transition_series,
        transitions,
        transition_branches,
        boots,
        bundle_cover_resistances,
        bundle_covers,
        covers,
        cpa_locks,
        tpa_locks,
        seals,
        wires,
        terminals,
        housings,
        cavities,
        housing_crossref,
        terminal_crossref,
        seal_crossref,
        cover_crossref,
        boot_crossref,
        tpa_lock_crossref,
        cpa_lock_crossref,
        projects,
        pjt_coordinates_3d,
        pjt_coordinates_2d,
        pjt_circuits,
        pjt_bundle_layouts,
        pjt_wire3d_layouts,
        pjt_wire2d_layouts,
        pjt_bundles,
        pjt_splices,
        pjt_housings,
        pjt_cavities,
        pjt_terminals,
        pjt_transitions,
        pjt_wires
    )

    for func in funcs:
        func(con_, cur_)

    cur_.close()
    con_.close()

'''

for feature in data['features']:
    if feature['code'] == '911841':
        for value in feature['values']:
            if value == '25':

'905343' - branch count

'904325' - shape, y, etc...


'901781' temperature range


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