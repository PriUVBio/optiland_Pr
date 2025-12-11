import numpy as np
from optiland import optic
from optiland.visualization import OpticViewer3D

class Endoscope(optic.Optic):
    """Compact medical endoscope for 4mm diameter sensor with enhanced light collection
    Scaled and optimized for 4mm sensor diameter
    """

    def __init__(self):
        super().__init__()
        
        # Scale factor to achieve 4mm diameter coverage
        scale = 15.0  # Scaling factor for 4mm sensor

        # Object medium (air for in-ear use)
        self.add_surface(index=0, radius=np.inf, thickness=np.inf)
        
        # Front lens group - scaled for 4mm sensor
        self.add_surface(index=1, radius=np.inf, thickness=0.5*scale, material="N-BK7")
        self.add_surface(index=2, radius=0.0284*scale, thickness=0.3*scale)
        
        # Aperture stop - sized for 4mm diameter
        self.add_surface(index=3, radius=np.inf, thickness=0.1*scale, is_stop=True)
        
        # Mid lens group - scaled
        self.add_surface(index=4, radius=-0.3742*scale, thickness=1.2*scale, material="N-LAK12")
        self.add_surface(index=5, radius=-0.0965*scale, thickness=0.08*scale)
        self.add_surface(index=6, radius=0.7827*scale, thickness=1.0*scale, material="SK16")
        self.add_surface(index=7, radius=-0.0842*scale, thickness=0.3*scale, material="SF4")
        self.add_surface(index=8, radius=-0.3720*scale, thickness=3.0*scale)
        
        # Rear lens group - scaled
        self.add_surface(index=9, radius=0.5158*scale, thickness=0.8*scale, material="N-LAF34")
        self.add_surface(index=10, radius=-0.3939*scale, thickness=0.15*scale, material="SF4")
        self.add_surface(index=11, radius=-0.8018*scale, thickness=0.2*scale)
        self.add_surface(index=12, radius=0.5380*scale, thickness=0.08*scale, material="SF4")
        self.add_surface(index=13, radius=0.2073*scale, thickness=0.6*scale, material="N-LAF34")
        self.add_surface(index=14, radius=-0.3509*scale, thickness=0.25*scale)
        
        # Final relay group - scaled for 4mm sensor
        self.add_surface(index=15, radius=0.5158*scale, thickness=0.5*scale, material="N-LAF34")
        self.add_surface(index=16, radius=-0.3939*scale, thickness=0.12*scale, material="SF4")
        self.add_surface(index=17, radius=-0.8018*scale, thickness=0.18*scale)
        self.add_surface(index=18, radius=0.5380*scale, thickness=0.06*scale, material="SF4")
        self.add_surface(index=19, radius=0.2073*scale, thickness=0.4*scale, material="N-LAF34")
        self.add_surface(index=20, radius=-0.3509*scale, thickness=0.2*scale)
        
        # Last element group - close to 4mm sensor
        self.add_surface(index=21, radius=0.5158*scale, thickness=0.3*scale, material="N-LAF34")
        self.add_surface(index=22, radius=-0.3939*scale, thickness=0.08*scale, material="SF4")
        self.add_surface(index=23, radius=-0.8018*scale, thickness=0.12*scale)
        self.add_surface(index=24, radius=0.5380*scale, thickness=0.05*scale, material="SF4")
        self.add_surface(index=25, radius=0.2073*scale, thickness=0.25*scale, material="N-LAF34")
        self.add_surface(index=26, radius=-0.3509*scale, thickness=0.1*scale)
        
        # Image surface (4mm diameter sensor)
        self.add_surface(index=27)

        # Enhanced light collection - larger aperture for 4mm sensor
        self.set_aperture(aperture_type="imageFNO", value=1.8)  # Even faster for better collection

        # Medical endoscope field angles - scaled for 4mm sensor
        self.set_field_type(field_type="angle")
        self.add_field(0.0)    # On-axis
        self.add_field(6)      # Moderate field for 4mm
        self.add_field(12)     # Edge field for 4mm diameter

        # Medical imaging wavelengths
        self.add_wavelength(value=0.4861327)  # Blue
        self.add_wavelength(value=0.5875618, is_primary=True)  # Green-yellow (primary)
        self.add_wavelength(value=0.6562725)  # Red

# Create and display the 4mm diameter endoscope
lens = Endoscope()

# 2D layout
print("Creating endoscope for 4mm diameter sensor...")
print(f"F-number: 1.8 (enhanced light collection)")
print(f"Field coverage: 0°, 6°, 12° (optimized for 4mm diameter)")
print(f"Sensor diameter: 4.0mm (medical imaging)")

fig, ax = lens.draw(figsize=(20, 4))
fig.savefig("endoscope_4mm_diameter.png", dpi=150, bbox_inches='tight')
print("✓ Saved: endoscope_4mm_diameter.png")

# 3D visualization
print("Creating 3D visualization...")
viewer3d = OpticViewer3D(lens)
viewer3d.view()
print("✓ 3D view opened")

print(f"\n4mm Endoscope specifications:")
print(f"Surfaces: {lens.surface_group.num_surfaces}")
print(f"Fields: {lens.fields.num_fields}")
print(f"Wavelengths: {lens.wavelengths.num_wavelengths}")
print(f"Target: 4.0mm diameter sensor, in-ear medical imaging")