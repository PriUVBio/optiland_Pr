#!/usr/bin/env python3
"""
MEDICAL ENDOSCOPE LENS DESIGN AND ANALYSIS
==========================================

Simple working endoscope lens for 3.9mm sensor
Based on proven optical design principles

Author: Medical Optics Design Team
Date: December 7, 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import os

# Optiland imports
from optiland import optic
from optiland.visualization import OpticViewer3D


class EndoscopeLens(optic.Optic):
    """
    Medical endoscope lens design
    
    Simple 3-element design for in-ear imaging
    Based on proven doublet + singlet configuration
    """
    
    def __init__(self):
        super().__init__()
        self.name = "Medical_Endoscope_3.9mm"
        
        # Object at infinity 
        self.add_surface(index=0, thickness=np.inf)
        
        # Element 1: First lens (strong positive, forms real image)
        self.add_surface(index=1, radius=3.0, thickness=2.0, material='N-BK7')
        self.add_surface(index=2, radius=-5.0, thickness=1.0)
        
        # Element 2: Second lens (weak negative for aberration correction)
        self.add_surface(index=3, radius=-8.0, thickness=1.0, material='N-SF11')
        self.add_surface(index=4, radius=6.0, thickness=0.5)
        
        # Aperture stop
        self.add_surface(index=5, thickness=0.5, is_stop=True)
        
        # Element 3: Final lens (positive, relay to image)
        self.add_surface(index=6, radius=4.0, thickness=2.0, material='N-BK7')
        self.add_surface(index=7, radius=-4.0, thickness=5.0)  # Back focal distance
        
        # Image surface
        self.add_surface(index=8)
        
        # Aperture setup
        self.set_aperture(aperture_type='EPD', value=2.0)  # 2mm entrance pupil
        
        # Field setup: Conservative field angles for medical imaging
        self.set_field_type(field_type='angle')
        self.add_field(0)     # On-axis
        self.add_field(5)     # 5 degrees
        self.add_field(10)    # 10 degrees  
        self.add_field(15)    # 15 degrees (maximum useful field)
        
        # Wavelength setup (medical imaging optimized)
        self.add_wavelength(value=0.486)          # Blue (F-line)
        self.add_wavelength(value=0.588, is_primary=True)  # Yellow-green (d-line)
        self.add_wavelength(value=0.656)          # Red (C-line)


def analyze_endoscope_simple(lens, results_dir):
    """Simple analysis function for endoscope lens"""
    
    print("\n" + "="*80)
    print("SIMPLIFIED ENDOSCOPE LENS ANALYSIS")
    print("="*80)
    
    # System properties
    print(f"\nSYSTEM PROPERTIES")
    print("-" * 40)
    print(f"Lens Name: {lens.name}")
    print(f"Surfaces: {lens.surface_group.num_surfaces}")
    print(f"Fields: {lens.fields.num_fields}")
    print(f"Wavelengths: {lens.wavelengths.num_wavelengths}")
    
    try:
        efl = lens.paraxial.f2()
        fno = lens.paraxial.FNO()
        print(f"Effective Focal Length: {efl:.3f} mm")
        print(f"F-Number: {fno:.2f}")
        print(f"Numerical Aperture: {1/(2*fno):.3f}")
    except Exception as e:
        print(f"Paraxial calculation error: {e}")
    
    # 2D Layout
    print(f"\nGenerating 2D layout...")
    try:
        fig, ax = lens.draw(figsize=(12, 4))
        layout_file = os.path.join(results_dir, '01_endoscope_layout_simple.png')
        plt.savefig(layout_file, dpi=150, bbox_inches='tight')
        plt.close()
        print(f"✓ Saved: 01_endoscope_layout_simple.png")
    except Exception as e:
        print(f"✗ Layout generation failed: {e}")
    
    # 3D Visualization
    print(f"\nGenerating 3D visualization...")
    try:
        viewer3d = OpticViewer3D(lens)
        viewer3d.view()
        print(f"✓ 3D Visualization opened")
    except Exception as e:
        print(f"✗ 3D visualization failed: {e}")
    
    # Ray tracing test
    print(f"\nRAY TRACING TEST")
    print("-" * 40)
    
    spot_results = []
    
    for field_idx in range(lens.fields.num_fields):
        field_angle = lens.fields.get_field(field_idx).y
        
        try:
            # Generate rays for this field
            rays = lens.get_ray_generator()
            
            # Trace to image surface
            rays.set_field(lens.fields.get_field(field_idx))
            rays.set_wavelength(lens.wavelengths.primary_wavelength)
            ray_data = rays.trace_to_image_surface()
            
            # Calculate RMS spot size
            if ray_data is not None and not np.any(np.isnan(ray_data['y'])):
                x_coords = ray_data['y']  # Note: Optiland uses y for image height
                y_coords = ray_data['z']  # and z for image depth
                
                # Remove NaN values
                valid = ~(np.isnan(x_coords) | np.isnan(y_coords))
                if np.sum(valid) > 0:
                    x_clean = x_coords[valid]
                    y_clean = y_coords[valid]
                    
                    # Calculate RMS
                    rms_spot = np.sqrt(np.mean(x_clean**2 + y_clean**2))
                    spot_results.append({
                        'field': field_angle,
                        'rms_mm': rms_spot,
                        'rms_um': rms_spot * 1000
                    })
                    print(f"Field {field_angle:2.0f}°: RMS = {rms_spot:.4f} mm ({rms_spot*1000:.1f} µm)")
                else:
                    print(f"Field {field_angle:2.0f}°: No valid rays reached image")
            else:
                print(f"Field {field_angle:2.0f}°: Ray tracing failed")
                
        except Exception as e:
            print(f"Field {field_angle:2.0f}°: Error - {e}")
    
    # Performance summary
    print(f"\nPERFORMANCE SUMMARY")
    print("-" * 40)
    
    if spot_results:
        best_field = min(spot_results, key=lambda x: x['rms_mm'])
        worst_field = max(spot_results, key=lambda x: x['rms_mm'])
        
        print(f"Best performance: Field {best_field['field']:.0f}° = {best_field['rms_um']:.1f} µm RMS")
        print(f"Worst performance: Field {worst_field['field']:.0f}° = {worst_field['rms_um']:.1f} µm RMS")
        
        # Medical imaging assessment
        if best_field['rms_um'] < 20:
            print("✓ Excellent resolution for medical imaging")
        elif best_field['rms_um'] < 50:
            print("✓ Good resolution for medical imaging")
        elif best_field['rms_um'] < 100:
            print("⚠ Acceptable resolution, optimization recommended")
        else:
            print("✗ Poor resolution, requires optimization")
    else:
        print("✗ No valid ray tracing results - design needs revision")
    
    print(f"\n" + "="*80)
    
    return spot_results


def main():
    """Main execution function"""
    
    # Create results directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = f"results/endoscope_simple_{timestamp}"
    os.makedirs(results_dir, exist_ok=True)
    
    print("="*80)
    print("SIMPLE ENDOSCOPE LENS DESIGN & ANALYSIS")
    print("="*80)
    print(f"\nResults directory: {results_dir}")
    
    # STEP 1: Create lens
    print(f"\n" + "-"*60)
    print("STEP 1: Creating simplified endoscope lens")
    print("-"*60)
    
    lens = EndoscopeLens()
    
    print(f"✓ Lens created: {lens.name}")
    print(f"  - Surfaces: {lens.surface_group.num_surfaces}")
    print(f"  - Fields: {lens.fields.num_fields}")  
    print(f"  - Wavelengths: {lens.wavelengths.num_wavelengths}")
    
    # STEP 2: Analysis
    print(f"\n" + "-"*60)
    print("STEP 2: Optical analysis and ray tracing")
    print("-"*60)
    
    spot_results = analyze_endoscope_simple(lens, results_dir)
    
    # STEP 3: Summary
    print(f"\n" + "-"*60)
    print("ANALYSIS COMPLETE")
    print("-"*60)
    
    print(f"\nResults saved to: {results_dir}/")
    print(f"\nKey outputs:")
    print(f"  - 01_endoscope_layout_simple.png")
    print(f"  - Interactive 3D visualization")
    
    if spot_results:
        print(f"  - Ray tracing: {len(spot_results)} field angles analyzed")
    
    print(f"\n" + "="*80)


if __name__ == "__main__":
    main()