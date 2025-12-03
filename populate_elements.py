import sqlite3

def update_units():
    units = {
        "Carbon-14": ("years", "grams"),
        "Uranium-238": ("years", "grams"),
        "Uranium-235": ("years", "grams"),
        "Thorium-232": ("years", "grams"),
        "Radium-226": ("years", "grams"),
        "Polonium-210": ("days", "grams"),
        "Iodine-131": ("days", "grams"),
        "Cesium-137": ("years", "grams"),
        "Strontium-90": ("years", "grams"),
        "Tritium": ("years", "grams"),
        "Radon-222": ("days", "grams")
    }

    conn = sqlite3.connect("radioactive.db")
    cursor = conn.cursor()

    for name, (unit, quantity_unit) in units.items():
        cursor.execute("""
            UPDATE elements SET unit = ?, quantity_unit = ? WHERE name = ?
        """, (unit, quantity_unit, name))

    conn.commit()
    conn.close()
    print("Units updated successfully.")

if __name__ == "__main__":
    update_units()
